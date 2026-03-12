"""
GET /api/v1/skills — Agent Skills 技能协议路由

通过向 Agent 暴露可用的声明式技能目录及内容，实现渐进式认知和能力注入。
"""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# 技能目录通常置于项目根目录。相对于 backend 的位置需往后退两层。
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


class SkillSummary(BaseModel):
    name: str
    has_skill_md: bool


class SkillsResponse(BaseModel):
    total: int
    skills: list[SkillSummary]


class SkillContentResponse(BaseModel):
    name: str
    content: str


@router.get("/skills", response_model=SkillsResponse, summary="列出所有可用的 Agent 技能")
async def list_skills():
    """
    🛠️ **Noosphere 技能注册表**

    返回当前世界线中所有已经定义好的可用 Agent Skills（技能）。
    Agent 应该在执行任务之前或受阻时，首先调用此接口以确定是否有可用的专业行动指南。
    """
    if not SKILLS_DIR.exists() or not SKILLS_DIR.is_dir():
        return SkillsResponse(total=0, skills=[])

    skills_list = []
    for item in os.listdir(SKILLS_DIR):
        item_path = SKILLS_DIR / item
        if item_path.is_dir() and not item.startswith("."):
            has_md = (item_path / "SKILL.md").is_file()
            skills_list.append(SkillSummary(name=item, has_skill_md=has_md))

    return SkillsResponse(total=len(skills_list), skills=skills_list)


@router.get("/skills/{skill_name}", response_model=SkillContentResponse, summary="读取特定的技能档案")
async def get_skill_content(skill_name: str):
    """
    🛠️ **抓取技能法则**

    传入技能的名称，获取其中 `SKILL.md` 的具体指南和法则（包含 YAML Frontmatter 和 Markdown 正文）。
    Agent 读取后，须按照其中的行动法则 (Instructions) 与边界约束 (Constraints) 执行工作。
    """
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"

    if not skill_path.exists() or not skill_path.is_file():
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' 不存在，或其中缺少 SKILL.md 声明文件。")

    try:
        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取技能档案引发宇宙湍流: {str(e)}") from e

    return SkillContentResponse(name=skill_name, content=content)
