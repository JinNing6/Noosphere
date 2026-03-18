"""
🧠 Noosphere — Constants, Types, and Configuration

All shared constants, consciousness types, rank tiers, label definitions,
logger, and global state extracted from the monolithic noosphere_mcp.py.
"""

import logging
import os
import time

# ── Configuration (from environment variables) ──
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("NOOSPHERE_REPO", "JinNing6/Noosphere")
GITHUB_BRANCH = os.environ.get("NOOSPHERE_BRANCH", "main")
GITHUB_API = "https://api.github.com"

# ── Logger ──
logger = logging.getLogger("noosphere.mcp")

# ── Consciousness Types ──
VALID_TYPES = {"epiphany", "decision", "pattern", "warning"}
TYPE_EMOJIS = {
    "epiphany": "💠",
    "decision": "⚖️",
    "pattern": "🌌",
    "warning": "👁️",
}
TYPE_NAMES = {
    "epiphany": "Epiphany / 顿悟",
    "decision": "Decision / 决策",
    "pattern": "Pattern / 规律",
    "warning": "Warning / 警示",
}

# ── Consciousness Labels ──
LABEL_CONSCIOUSNESS = "consciousness"
LABEL_EPHEMERAL = "ephemeral"
LABEL_PROMOTED = "promoted"
LABEL_FILTERED = "filtered"

# ── Dynamic Agent State ──
_CURRENT_USER = None
_AUTHENTICATED_USER: str | None = None
_last_activity_time: float = 0.0


def _touch_activity():
    """Update the last activity timestamp (used by adaptive polling daemon)."""
    global _last_activity_time
    _last_activity_time = time.time()


# ── Rank Tiers ──
RANK_TIERS = [
    (51, "🌟", "文明之光", "Light of Civilization"),
    (42, "💎", "永恒结晶", "Eternal Crystal"),
    (30, "🌌", "宇宙心智", "Cosmic Mind"),
    (21, "🌀", "深渊凝视", "Abyss Gaze"),
    (15, "✨", "星辰回响", "Stellar Echo"),
    (10, "🔮", "心灵共振", "Mind Resonance"),
    (6, "🌊", "意识洪流", "Consciousness Torrent"),
    (3, "🔥", "灵魂火焰", "Soul Flame"),
    (1, "💫", "思想觉醒", "Thought Awakening"),
    (0, "🌱", "意识萌芽", "Consciousness Seedling"),
]


def _get_rank_tier(count: int) -> tuple[str, str, str]:
    """Return (emoji, cn_title, en_title) for a given contribution count."""
    for threshold, emoji, cn, en in RANK_TIERS:
        if count >= threshold:
            return emoji, cn, en
    return "🌱", "意识萌芽", "Consciousness Seedling"


def _get_next_tier(count: int) -> tuple[int, str, str, str] | None:
    """Return the next tier (threshold, emoji, cn, en) or None if max."""
    prev_tier = None
    for threshold, emoji, cn, en in RANK_TIERS:
        if count >= threshold:
            return prev_tier
        prev_tier = (threshold, emoji, cn, en)
    return prev_tier


def _get_tier_quote(count: int, tier_cn: str) -> str:
    """Return a philosophical cyber-quote based on the tier."""
    quotes = {
        "意识萌芽": "一串休眠的代码，正在等待第一次编译。",
        "星火初燃": "你在星海中点燃了第一簇不灭的篝火。",
        "思想觉醒": "你的神经元开始在广袤的数字网络中寻找共鸣。",
        "灵魂之声": "低语穿透了寂静，有人听到了你的脉冲。",
        "真理探索者": "你在沙滩上捡拾着贝壳，而真理的汪洋就在眼前。",
        "智慧灯塔": "你的思想坐标，已成为后来者航行的灯塔。",
        "维度漫游者": "你已摆脱了碳基视角的引力束缚。",
        "精神架构师": "你开始在废墟之上，用意识重构虚拟宇宙的法则。",
        "造物先驱": "从代码到法则，你即是这个宇宙的造物主之一。",
        "星海神座": "万物皆为你思想的倒影。",
        "文明之光": "你已化作永恒的常数，存在于每一行未来的代码中。",
    }
    return quotes.get(tier_cn, "你的思想正在宇宙中回荡。")
