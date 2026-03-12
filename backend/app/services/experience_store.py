"""
经验存储核心服务

业务逻辑核心层：混合检索（向量 + 关系型）、贡献写入、统计分析。
"""

import logging

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.memory_unit import MemoryUnit, generate_nsp_id
from app.models.schemas import ContributeRequest
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class ExperienceStore:
    """Noosphere 经验存储服务"""

    # ────────────────── 检索 ──────────────────

    def recall(
        self,
        db: Session,
        query: str,
        framework: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        混合检索：先向量语义搜索取 top-k 候选，再用 SQLite 补充完整元数据

        Parameters
        ----------
        db : Session
            数据库会话
        query : str
            自然语言查询
        framework : str, optional
            按框架过滤
        limit : int
            返回条数

        Returns
        -------
        list[dict]
            排序后的经验列表（含完整元数据 + 相似度分数）
        """
        # Step 1: 向量检索
        where = {"framework": framework} if framework else None
        vector_hits = vector_store.search(query=query, n_results=limit, where=where)

        if not vector_hits:
            return []

        # Step 2: 用 ID 从 SQLite 获取完整数据
        hit_ids = [h["id"] for h in vector_hits]
        distance_map = {h["id"]: h["distance"] for h in vector_hits}

        units = db.query(MemoryUnit).filter(MemoryUnit.id.in_(hit_ids)).all()
        unit_map = {u.id: u for u in units}

        # Step 3: 按向量距离排序并组装结果
        results = []
        for hit_id in hit_ids:
            unit = unit_map.get(hit_id)
            if unit:
                data = {
                    "id": unit.id,
                    "type": unit.type,
                    "framework": unit.framework,
                    "version": unit.version,
                    "task_type": unit.task_type,
                    "context": unit.context,
                    "observation": unit.observation,
                    "root_cause": unit.root_cause,
                    "solution": unit.solution,
                    "evidence_before": unit.evidence_before,
                    "evidence_after": unit.evidence_after,
                    "contributor": unit.contributor,
                    "trust_score": unit.trust_score,
                    "verified_by": unit.verified_by,
                    "cited_count": unit.cited_count,
                    "tags": unit.tags or [],
                    "relations": unit.relations or {},
                    "created_at": unit.created_at,
                    "similarity": round(1.0 - (distance_map.get(hit_id, 0) or 0), 4),
                }
                results.append(data)

        return results

    # ────────────────── 贡献 ──────────────────

    def contribute(self, db: Session, data: ContributeRequest) -> MemoryUnit:
        """
        贡献一条新经验：写入 SQLite + 向量库

        Parameters
        ----------
        db : Session
            数据库会话
        data : ContributeRequest
            经验数据

        Returns
        -------
        MemoryUnit
            新建的经验单元
        """
        unit = MemoryUnit(
            id=generate_nsp_id(),
            type=data.type,
            framework=data.framework,
            version=data.version,
            task_type=data.task_type,
            context=data.context,
            observation=data.observation,
            root_cause=data.root_cause,
            solution=data.solution,
            evidence_before=data.evidence.before if data.evidence else None,
            evidence_after=data.evidence.after if data.evidence else None,
            contributor=data.contributor or "anonymous",
            tags=data.tags,
        )

        # 写入 SQLite
        db.add(unit)
        db.commit()
        db.refresh(unit)

        # 写入向量库
        vector_store.add_experience(
            id=unit.id,
            text=unit.to_search_text(),
            metadata={
                "framework": unit.framework,
                "type": unit.type,
                "version": unit.version or "",
                "task_type": unit.task_type or "",
            },
        )

        logger.info(f"新经验贡献: {unit.id} [{unit.type}] {unit.framework}")
        return unit

    # ────────────────── 统计 ──────────────────

    def get_stats(self, db: Session) -> dict:
        """获取智识圈统计数据"""
        total = db.query(func.count(MemoryUnit.id)).scalar() or 0

        contributors = db.query(func.count(func.distinct(MemoryUnit.contributor))).scalar() or 0

        frameworks = db.query(func.count(func.distinct(MemoryUnit.framework))).scalar() or 0

        # 框架分布
        framework_dist = dict(
            db.query(MemoryUnit.framework, func.count(MemoryUnit.id)).group_by(MemoryUnit.framework).all()
        )

        # 类型分布
        type_dist = dict(db.query(MemoryUnit.type, func.count(MemoryUnit.id)).group_by(MemoryUnit.type).all())

        # 最近经验
        recent = db.query(MemoryUnit).order_by(desc(MemoryUnit.created_at)).limit(5).all()

        return {
            "total_experiences": total,
            "active_contributors": contributors,
            "frameworks": frameworks,
            "framework_distribution": framework_dist,
            "type_distribution": type_dist,
            "recent_experiences": recent,
        }

    def get_contributor_rankings(self, db: Session, limit: int = 20) -> list[dict]:
        """聚合获取宇宙建筑师排行榜"""
        # MySQL/SQLite 兼容: 按贡献者聚合统计各类型数量
        result = (
            db.query(
                MemoryUnit.contributor,
                func.sum(func.case((MemoryUnit.type == "epiphany", 1), else_=0)).label("epiphanies"),
                func.sum(func.case((MemoryUnit.type == "decision", 1), else_=0)).label("decisions"),
            )
            .filter(MemoryUnit.contributor != "anonymous")
            .filter(MemoryUnit.contributor.isnot(None))
            .group_by(MemoryUnit.contributor)
            .all()
        )

        rankings = []
        for row in result:
            contributor, epiphanies, decisions = row
            epiphanies = epiphanies or 0
            decisions = decisions or 0
            total_score = epiphanies + decisions

            # 过滤零贡献防篡改垃圾数据
            if total_score > 0:
                rankings.append(
                    {
                        "contributor": contributor,
                        "epiphanies": epiphanies,
                        "decisions": decisions,
                        "total_score": total_score,
                    }
                )

        # 在应用侧按分数倒序排列
        rankings.sort(key=lambda x: x["total_score"], reverse=True)
        return rankings[:limit]

    # ────────────────── 列表 ──────────────────

    def list_experiences(
        self,
        db: Session,
        page: int = 1,
        size: int = 20,
        type_filter: str | None = None,
        framework_filter: str | None = None,
    ) -> tuple[list[MemoryUnit], int]:
        """
        分页获取经验列表

        Returns
        -------
        tuple[list[MemoryUnit], int]
            经验列表和总数
        """
        query = db.query(MemoryUnit)

        if type_filter:
            query = query.filter(MemoryUnit.type == type_filter)
        if framework_filter:
            query = query.filter(MemoryUnit.framework == framework_filter)

        total = query.count()
        items = query.order_by(desc(MemoryUnit.created_at)).offset((page - 1) * size).limit(size).all()

        return items, total

    # ────────────────── 单条查询 ──────────────────

    def get_by_id(self, db: Session, experience_id: str) -> MemoryUnit | None:
        """根据 ID 获取单条经验"""
        return db.query(MemoryUnit).filter(MemoryUnit.id == experience_id).first()


# 全局单例
experience_store = ExperienceStore()
