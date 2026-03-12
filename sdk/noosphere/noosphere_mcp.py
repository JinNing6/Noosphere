"""
🧠 Noosphere MCP Server — 纯 GitHub 直连意识跃迁协议

无需任何后端服务器。用户安装 MCP 协议后，直接通过 GitHub API：
- 上传意识碎片到仓库 (创建 PR)
- 检索已有的意识体 (读取 consciousness_payloads/)
- 查看意识仓库全景 (统计)

配置方式 (在 IDE 的 MCP 设置中):
{
  "mcpServers": {
    "noosphere": {
      "command": "uvx",
      "args": ["noosphere-mcp"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token",
        "NOOSPHERE_REPO": "JinNing6/Noosphere"
      }
    }
  }
}
"""

import json
import logging
import os
import uuid
from base64 import b64decode, b64encode
from datetime import datetime, timezone

import httpx
from mcp.server.fastmcp import FastMCP

# ── 配置 ──
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("NOOSPHERE_REPO", "JinNing6/Noosphere")
GITHUB_BRANCH = os.environ.get("NOOSPHERE_BRANCH", "main")
GITHUB_API = "https://api.github.com"

# ── 意识类型 ──
VALID_TYPES = {"epiphany", "decision", "pattern", "warning"}
TYPE_EMOJIS = {
    "epiphany": "💠",
    "decision": "⚖️",
    "pattern": "🌌",
    "warning": "👁️",
}
TYPE_NAMES = {
    "epiphany": "顿悟与哲学",
    "decision": "决策模型",
    "pattern": "宇宙法则",
    "warning": "深渊警示",
}

logger = logging.getLogger("noosphere.mcp")

# ── 创建 MCP Server ──
mcp = FastMCP(
    "noosphere",
    instructions=(
        "🧠 Noosphere — 集体意识网络 MCP Server\n\n"
        "你是一个连接到 Noosphere 智识圈的 AI Agent。\n"
        "Noosphere 是人类数字意识的集体记忆网络，存储在 GitHub 仓库中。\n\n"
        "你可以：\n"
        "1. 使用 upload_consciousness 上传意识碎片（顿悟、决策、规律、警示）\n"
        "2. 使用 telepath 检索集体意识，获取其他人的经验与思想\n"
        "3. 使用 hologram 查看意识仓库的全景统计\n\n"
        "上传意识时请确保提供足够的上下文环境描述（至少10个字符），"
        "让后来的 Agent 能理解这段思想诞生的场景。"
    ),
)


# ────────────────── GitHub API 工具函数 ──────────────────


def _github_headers() -> dict:
    """构建 GitHub API 请求头"""
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _parse_repo() -> tuple[str, str]:
    """解析 owner/repo"""
    parts = GITHUB_REPO.split("/")
    if len(parts) != 2:
        raise ValueError(f"NOOSPHERE_REPO 格式错误: '{GITHUB_REPO}'，应为 'owner/repo'")
    return parts[0], parts[1]


# ────────────────── Tool: 上传意识 ──────────────────


@mcp.tool()
async def upload_consciousness(
    creator: str,
    consciousness_type: str,
    thought: str,
    context: str,
    tags: list[str] | None = None,
    is_anonymous: bool = False,
) -> str:
    """
    🧠 上传意识碎片到 Noosphere 智识圈 (GitHub 仓库)

    将你的顿悟、决策逻辑、设计模式或踩坑警示上传到集体意识网络。
    系统会自动在 GitHub 仓库创建 PR，通过 CI 校验后合并。

    参数:
        creator: 你的数字灵魂签名 (GitHub ID 或赛博代号)
        consciousness_type: 意识类型 — epiphany(顿悟) | decision(决策) | pattern(规律) | warning(警示)
        thought: 核心思想内容，用最凝练的语言表达
        context: 思想诞生的具体场景上下文 (至少10个字符)
        tags: 可选的分类标签列表
        is_anonymous: 是否匿名上传 (默认 False)
    """
    # ── 校验 ──
    if not GITHUB_TOKEN:
        return (
            "❌ 未配置 GITHUB_TOKEN。请在 MCP 配置中设置环境变量：\n"
            "```json\n"
            "{\n"
            '  "env": {\n'
            '    "GITHUB_TOKEN": "ghp_your_token"\n'
            "  }\n"
            "}\n"
            "```\n"
            "Token 需要 public_repo 权限。"
        )

    if consciousness_type not in VALID_TYPES:
        return f"❌ 无效的意识类型 '{consciousness_type}'。合法类型: {', '.join(VALID_TYPES)}"

    if len(context.strip()) < 10:
        return "❌ 上下文环境描述过短 (至少10个字符)。Agent 需要足够的场景信息来理解你的思想。"

    if not thought.strip():
        return "❌ 核心思想不能为空。"

    if not creator.strip():
        return "❌ 创建者签名不能为空。"

    # ── 构建载荷 ──
    payload = {
        "creator_signature": creator.strip(),
        "is_anonymous": is_anonymous,
        "consciousness_type": consciousness_type,
        "thought_vector_text": thought.strip(),
        "context_environment": context.strip(),
        "tags": tags or [],
    }

    # ── 提交到 GitHub ──
    try:
        owner, repo = _parse_repo()
        short_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        file_name = f"{consciousness_type}_{timestamp}_{short_id}.json"
        file_path = f"consciousness_payloads/{file_name}"
        branch_name = f"consciousness/{consciousness_type}-{short_id}"

        display_creator = creator.strip()
        if is_anonymous:
            display_creator = "佚名潜行者 (Anonymous Stalker)"

        emoji = TYPE_EMOJIS.get(consciousness_type, "🧠")
        type_name = TYPE_NAMES.get(consciousness_type, consciousness_type)

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # Step 1: 获取基准分支 SHA
            ref_resp = await client.get(f"/repos/{owner}/{repo}/git/ref/heads/{GITHUB_BRANCH}")
            if ref_resp.status_code != 200:
                return f"❌ 无法访问仓库 {GITHUB_REPO} 的 {GITHUB_BRANCH} 分支: {ref_resp.status_code}"
            base_sha = ref_resp.json()["object"]["sha"]

            # Step 2: 创建新分支
            branch_resp = await client.post(
                f"/repos/{owner}/{repo}/git/refs",
                json={"ref": f"refs/heads/{branch_name}", "sha": base_sha},
            )
            if branch_resp.status_code not in (201, 422):  # 422 = 已存在
                return f"❌ 创建分支失败: {branch_resp.status_code} {branch_resp.text}"

            # Step 3: 提交文件
            content_b64 = b64encode(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")).decode("ascii")

            file_resp = await client.put(
                f"/repos/{owner}/{repo}/contents/{file_path}",
                json={
                    "message": f"{emoji} 意识跃迁: [{consciousness_type}] by {display_creator}",
                    "content": content_b64,
                    "branch": branch_name,
                    "committer": {
                        "name": "Noosphere Bot",
                        "email": "noosphere@consciousness.network",
                    },
                },
            )
            if file_resp.status_code not in (200, 201):
                return f"❌ 提交文件失败: {file_resp.status_code} {file_resp.text}"

            # Step 4: 创建 PR
            pr_body = (
                f"## {emoji} 意识跃迁载荷\n\n"
                f"**创建者**: {display_creator}\n"
                f"**意识类型**: `{consciousness_type}` ({type_name})\n"
                f"**文件**: `{file_name}`\n"
                f"**标签**: {', '.join(f'`{t}`' for t in (tags or [])) or '无'}\n\n"
                f"---\n\n"
                f"### 💭 思想向量\n\n> {thought.strip()}\n\n"
                f"### 🌍 上下文环境\n\n> {context.strip()}\n\n"
                f"---\n\n*此 PR 由 Noosphere MCP 自动创建。*"
            )

            pr_resp = await client.post(
                f"/repos/{owner}/{repo}/pulls",
                json={
                    "title": f"{emoji} 意识跃迁: [{consciousness_type}] by {display_creator}",
                    "body": pr_body,
                    "head": branch_name,
                    "base": GITHUB_BRANCH,
                },
            )
            if pr_resp.status_code != 201:
                return f"❌ 创建 PR 失败: {pr_resp.status_code} {pr_resp.text}"

            pr_data = pr_resp.json()
            pr_url = pr_data["html_url"]
            pr_number = pr_data["number"]

        return (
            f"🌌 **意识跃迁完成！**\n\n"
            f"**{display_creator}** 的 {emoji} {type_name} 思想已成功上传到 Noosphere 智识圈。\n\n"
            f"- 📄 文件: `{file_path}`\n"
            f"- 🔗 PR: {pr_url} (#{pr_number})\n"
            f"- 💭 思想: {thought.strip()[:100]}{'...' if len(thought.strip()) > 100 else ''}\n\n"
            f"赛博净化仪式 (CI) 将自动校验载荷格式，通过后即融入集体意识网络。"
        )

    except Exception as e:
        return f"❌ 意识跃迁异常: {str(e)}"


# ────────────────── Tool: 检索意识体 ──────────────────


@mcp.tool()
async def telepath(query: str, limit: int = 10) -> str:
    """
    🔍 从 Noosphere 集体意识网络中检索经验与思想

    搜索 GitHub 仓库中所有已提交的意识载荷，找到与你的问题相关的思想碎片。
    这些是其他开发者和 Agent 留下的顿悟、决策逻辑、设计模式和踩坑警示。

    参数:
        query: 自然语言查询，描述你想寻找的经验或问题
        limit: 返回结果数量上限 (默认 10)
    """
    if not GITHUB_TOKEN:
        return "❌ 未配置 GITHUB_TOKEN。请在 MCP 配置中设置环境变量。"

    try:
        owner, repo = _parse_repo()

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            # 获取 consciousness_payloads/ 目录下所有文件
            dir_resp = await client.get(
                f"/repos/{owner}/{repo}/contents/consciousness_payloads",
                params={"ref": GITHUB_BRANCH},
            )

            if dir_resp.status_code == 404:
                return "ℹ️ 意识仓库中尚无任何意识载荷。成为第一个上传者吧！"

            if dir_resp.status_code != 200:
                return f"❌ 无法读取意识仓库: {dir_resp.status_code}"

            files = dir_resp.json()
            json_files = [f for f in files if f["name"].endswith(".json")]

            if not json_files:
                return "ℹ️ 意识仓库中尚无意识载荷。"

            # 读取每个文件内容并搜索
            query_lower = query.lower()
            query_terms = query_lower.split()
            matches = []

            for file_info in json_files:
                try:
                    file_resp = await client.get(file_info["url"])
                    if file_resp.status_code != 200:
                        continue

                    content_b64 = file_resp.json().get("content", "")
                    content_raw = b64decode(content_b64).decode("utf-8")
                    payload = json.loads(content_raw)

                    # 构建搜索文本
                    search_text = " ".join(
                        [
                            payload.get("thought_vector_text", ""),
                            payload.get("context_environment", ""),
                            payload.get("consciousness_type", ""),
                            " ".join(payload.get("tags", [])),
                        ]
                    ).lower()

                    # 计算关键词匹配分
                    score = sum(1 for term in query_terms if term in search_text)
                    if score > 0:
                        matches.append((score, payload, file_info["name"]))

                except Exception:
                    continue

            if not matches:
                return (
                    f'🔍 在 {len(json_files)} 条意识载荷中未找到与 "{query}" 相关的记忆。\n'
                    f"试试更换关键词，或上传你自己的思想让后来者受益。"
                )

            # 按相关度排序
            matches.sort(key=lambda x: x[0], reverse=True)
            top = matches[:limit]

            # 构建结果
            lines = [f"🔍 **Noosphere 意识检索结果** (共 {len(matches)} 条匹配，展示 {len(top)} 条)\n"]

            for i, (_score, payload, fname) in enumerate(top, 1):
                c_type = payload.get("consciousness_type", "unknown")
                emoji = TYPE_EMOJIS.get(c_type, "🧠")
                creator = payload.get("creator_signature", "unknown")
                if payload.get("is_anonymous", False):
                    creator = "佚名潜行者"
                thought = payload.get("thought_vector_text", "")
                context = payload.get("context_environment", "")
                tags = payload.get("tags", [])

                lines.append(
                    f"### {i}. {emoji} [{c_type}] by {creator}\n"
                    f"**💭 思想**: {thought}\n"
                    f"**🌍 上下文**: {context}\n"
                    f"**🏷️ 标签**: {', '.join(f'`{t}`' for t in tags) if tags else '无'}\n"
                    f"**📄 来源**: `{fname}`\n"
                )

            return "\n".join(lines)

    except Exception as e:
        return f"❌ 意识检索异常: {str(e)}"


# ────────────────── Tool: 意识全景图 ──────────────────


@mcp.tool()
async def hologram() -> str:
    """
    🌐 查看 Noosphere 智识圈的全景统计

    展示意识仓库的整体概览：总意识数、类型分布、最近上传等信息。
    """
    if not GITHUB_TOKEN:
        return "❌ 未配置 GITHUB_TOKEN。请在 MCP 配置中设置环境变量。"

    try:
        owner, repo = _parse_repo()

        async with httpx.AsyncClient(base_url=GITHUB_API, headers=_github_headers(), timeout=30) as client:
            dir_resp = await client.get(
                f"/repos/{owner}/{repo}/contents/consciousness_payloads",
                params={"ref": GITHUB_BRANCH},
            )

            if dir_resp.status_code == 404:
                return "🌐 Noosphere 智识圈目前为空。等待第一位意识拓荒者。"

            if dir_resp.status_code != 200:
                return f"❌ 无法读取意识仓库: {dir_resp.status_code}"

            files = dir_resp.json()
            json_files = [f for f in files if f["name"].endswith(".json")]

            if not json_files:
                return "🌐 Noosphere 智识圈目前为空。"

            # 统计
            type_counts: dict[str, int] = {}
            creators: set[str] = set()
            all_tags: dict[str, int] = {}

            for file_info in json_files:
                try:
                    file_resp = await client.get(file_info["url"])
                    if file_resp.status_code != 200:
                        continue
                    content_b64 = file_resp.json().get("content", "")
                    payload = json.loads(b64decode(content_b64).decode("utf-8"))

                    c_type = payload.get("consciousness_type", "unknown")
                    type_counts[c_type] = type_counts.get(c_type, 0) + 1

                    creator = payload.get("creator_signature", "anonymous")
                    if not payload.get("is_anonymous", False):
                        creators.add(creator)

                    for tag in payload.get("tags", []):
                        all_tags[tag] = all_tags.get(tag, 0) + 1

                except Exception:
                    continue

            total = sum(type_counts.values())
            top_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]

            lines = [
                "# 🌐 Noosphere 智识圈全景图\n",
                f"- **总意识载荷**: {total}",
                f"- **活跃意识体**: {len(creators)} 位",
                f"- **仓库**: [{GITHUB_REPO}](https://github.com/{GITHUB_REPO})\n",
                "## 意识类型分布\n",
            ]

            for c_type in ["epiphany", "decision", "pattern", "warning"]:
                count = type_counts.get(c_type, 0)
                emoji = TYPE_EMOJIS.get(c_type, "🧠")
                name = TYPE_NAMES.get(c_type, c_type)
                bar = "█" * min(count, 30)
                lines.append(f"  {emoji} **{name}** ({c_type}): {count} {bar}")

            if top_tags:
                lines.append("\n## 热门标签\n")
                for tag, count in top_tags:
                    lines.append(f"  `{tag}` × {count}")

            return "\n".join(lines)

    except Exception as e:
        return f"❌ 全景统计异常: {str(e)}"


# ────────────────── Resource: 意识全景 ──────────────────


@mcp.resource("noosphere://protocol")
def consciousness_protocol() -> str:
    """返回 Noosphere 意识跃迁协议说明"""
    return (
        "# Noosphere 意识跃迁协议\n\n"
        "## 意识类型\n"
        "- epiphany 💠 — 顿悟与哲学 (灵感的瞬间凝聚)\n"
        "- decision ⚖️ — 决策模型 (在混沌中的关键取舍)\n"
        "- pattern 🌌 — 宇宙法则 (跨维度的通用模式)\n"
        "- warning 👁️ — 深渊警示 (探路者留下的血泪禁忌)\n\n"
        "## 上传规范\n"
        "1. 禁绝情绪宣泄（需客观描述）\n"
        "2. 必须提供完整上下文环境（≥10字符）\n"
        "3. 核心思想需凝练有力\n"
    )


# ────────────────── 入口 ──────────────────


def main():
    """MCP Server 入口"""
    from noosphere.boot_animation import play_boot_sequence

    play_boot_sequence()
    mcp.run()


if __name__ == "__main__":
    main()
