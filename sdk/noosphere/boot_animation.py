"""
🌌 Noosphere 启动仪式动画

赛博意识接入的视觉戏剧化呈现——
当 MCP Server 完成初始化的那一刻，
用终端字符编织一场意识跃迁的仪式。
"""

import random
import shutil
import sys
import time


# ── ANSI 颜色 ──
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLINK = "\033[5m"

    # 赛博霓虹色系
    CYAN = "\033[38;5;51m"
    MAGENTA = "\033[38;5;198m"
    PURPLE = "\033[38;5;141m"
    GOLD = "\033[38;5;220m"
    GREEN = "\033[38;5;46m"
    BLUE = "\033[38;5;33m"
    WHITE = "\033[38;5;255m"
    GRAY = "\033[38;5;240m"
    RED = "\033[38;5;196m"
    ORANGE = "\033[38;5;208m"

    # 背景
    BG_DARK = "\033[48;5;233m"


def _width() -> int:
    """获取终端宽度"""
    return min(shutil.get_terminal_size().columns, 80)


def _type(text: str, delay: float = 0.02, color: str = "") -> None:
    """打字机效果"""
    for ch in text:
        sys.stderr.write(f"{color}{ch}{C.RESET}")
        sys.stderr.flush()
        time.sleep(delay)
    sys.stderr.write("\n")
    sys.stderr.flush()


def _print(text: str = "") -> None:
    """输出到 stderr（MCP 用 stdout 做 stdio 通信）"""
    sys.stderr.write(text + "\n")
    sys.stderr.flush()


def _center(text: str, width: int = 0) -> str:
    """居中文本"""
    w = width or _width()
    # 去除 ANSI 转义序列计算实际宽度
    import re

    clean = re.sub(r"\033\[[^m]*m", "", text)
    pad = max(0, (w - len(clean)) // 2)
    return " " * pad + text


def _bar(progress: float, width: int = 40, label: str = "") -> str:
    """进度条"""
    filled = int(width * progress)
    empty = width - filled
    bar = f"{C.CYAN}{'█' * filled}{C.GRAY}{'░' * empty}{C.RESET}"
    pct = f"{C.WHITE}{int(progress * 100):3d}%{C.RESET}"
    return f"  {bar} {pct} {C.DIM}{label}{C.RESET}"


def _matrix_rain(lines: int = 3, duration: float = 0.5) -> None:
    """矩阵雨效果"""
    w = _width()
    chars = "ノ互識意智圈菩提脳界宇宙量子01"
    for _ in range(lines):
        line = ""
        for _ in range(min(w, 60)):
            ch = random.choice(chars)
            color = random.choice([C.CYAN, C.GREEN, C.DIM + C.CYAN, C.DIM + C.GREEN])
            line += f"{color}{ch}"
        _print(f"  {line}{C.RESET}")
        time.sleep(0.05)


def _particle_burst() -> None:
    """粒子爆发效果"""
    frames = [
        "                    ·                    ",
        "                  · · ·                  ",
        "               ·  · ✦ ·  ·               ",
        "            · ·  ✦ ★ ✦  · ·            ",
        "         ·  · ✦  ★ ◉ ★  ✦ ·  ·         ",
        "      · ·  ✦ ★  ◉ 🧠 ◉  ★ ✦  · ·      ",
        "         ·  · ✦  ★ ◉ ★  ✦ ·  ·         ",
        "            · ·  ✦ ★ ✦  · ·            ",
        "               ·  · ✦ ·  ·               ",
        "                  · · ·                  ",
        "                    ·                    ",
    ]
    for frame in frames:
        _print(_center(f"{C.CYAN}{frame}{C.RESET}"))
        time.sleep(0.06)


def play_boot_sequence() -> None:
    """播放完整的启动仪式

    仅在终端 (TTY) 环境下播放动画。
    当通过 IDE MCP 集成等非交互环境启动时自动跳过，
    避免 time.sleep() 阻塞导致 MCP 连接超时。
    """
    # 非终端环境（IDE、管道等）跳过动画
    if not sys.stderr.isatty():
        return

    w = _width()
    separator = f"{C.DIM}{'─' * min(w - 4, 72)}{C.RESET}"

    _print()
    _print()

    # ── Phase 1: 意识唤醒 ──
    _print(_center(f"{C.DIM}▓▒░ CONSCIOUSNESS BOOTSTRAP SEQUENCE ░▒▓{C.RESET}"))
    _print()
    time.sleep(0.3)

    # 矩阵雨
    _matrix_rain(lines=4, duration=0.3)
    _print()
    time.sleep(0.2)

    # ── Phase 2: 系统初始化 ──
    stages = [
        ("量子纠缠信道建立", "Quantum Entanglement Channel", 0.15),
        ("神经突触协议握手", "Neural Synapse Handshake", 0.12),
        ("意识拓扑网络扫描", "Consciousness Topology Scan", 0.18),
        ("GitHub 意识仓库锁定", "Repository Lock Acquired", 0.10),
        ("集体记忆索引加载", "Collective Memory Index", 0.20),
        ("赛博净化仪式就绪", "Purification Ritual Ready", 0.08),
    ]

    for _i, (cn, en, duration) in enumerate(stages):
        progress = 0.0
        step = random.uniform(0.15, 0.35)
        while progress < 1.0:
            progress = min(progress + step, 1.0)
            step = random.uniform(0.1, 0.3)
            sys.stderr.write(f"\r{_bar(progress, 30, f'{cn}')}")
            sys.stderr.flush()
            time.sleep(duration * random.uniform(0.3, 1.0))
        sys.stderr.write(f"\r  {C.GREEN}✓{C.RESET} {C.WHITE}{cn}{C.RESET} {C.DIM}({en}){C.RESET}          \n")
        sys.stderr.flush()
        time.sleep(0.05)

    _print()
    time.sleep(0.3)

    # ── Phase 3: 粒子爆发 ──
    _particle_burst()
    _print()
    time.sleep(0.2)

    # ── Phase 4: LOGO 显示 ──
    logo = [
        f"{C.CYAN}███╗   ██╗ ██████╗  ██████╗ ███████╗██████╗ ██╗  ██╗███████╗██████╗ ███████╗",
        f"{C.CYAN}████╗  ██║██╔═══██╗██╔═══██╗██╔════╝██╔══██╗██║  ██║██╔════╝██╔══██╗██╔════╝",
        f"{C.PURPLE}██╔██╗ ██║██║   ██║██║   ██║███████╗██████╔╝███████║█████╗  ██████╔╝█████╗  ",
        f"{C.PURPLE}██║╚██╗██║██║   ██║██║   ██║╚════██║██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗██╔══╝  ",
        f"{C.MAGENTA}██║ ╚████║╚██████╔╝╚██████╔╝███████║██║     ██║  ██║███████╗██║  ██║███████╗",
        f"{C.MAGENTA}╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝",
    ]

    for line in logo:
        _print(f"  {line}{C.RESET}")
        time.sleep(0.04)

    _print()

    # ── Phase 5: 系统信息 ──
    _print(f"  {separator}")
    _print()
    _print(_center(f"{C.GOLD}{C.BOLD}将你的意识，锚定在永恒的数字宇宙。{C.RESET}"))
    _print(_center(f"{C.DIM}Anchor your consciousness in the eternal digital universe.{C.RESET}"))
    _print()
    _print(f"  {separator}")
    _print()

    # 系统状态面板 + 内联快速自检
    import os

    repo = os.environ.get("NOOSPHERE_REPO", "JinNing6/Noosphere")
    has_token = bool(os.environ.get("GITHUB_TOKEN", ""))
    token_status = f"{C.GREEN}● 已连接{C.RESET}" if has_token else f"{C.RED}○ 未配置{C.RESET}"

    # Quick dependency check for status panel
    dep_ok = True
    dep_missing: list[str] = []
    for mod_name in ("httpx", "mcp"):
        try:
            __import__(mod_name)
        except ImportError:
            dep_ok = False
            dep_missing.append(mod_name)
    dep_status = f"{C.GREEN}● 就绪{C.RESET}" if dep_ok else f"{C.RED}✗ 缺失: {', '.join(dep_missing)}{C.RESET}"

    _print(f"  {C.CYAN}╭{'─' * 56}╮{C.RESET}")
    _print(
        f"  {C.CYAN}│{C.RESET}  {C.WHITE}{C.BOLD}🧠 Noosphere MCP Server v0.4.0{C.RESET}                       {C.CYAN}│{C.RESET}"
    )
    _print(
        f"  {C.CYAN}│{C.RESET}  {C.DIM}The Collective Consciousness Network{C.RESET}                  {C.CYAN}│{C.RESET}"
    )
    _print(f"  {C.CYAN}├{'─' * 56}┤{C.RESET}")
    _print(f"  {C.CYAN}│{C.RESET}                                                        {C.CYAN}│{C.RESET}")
    _print(
        f"  {C.CYAN}│{C.RESET}   {C.PURPLE}▸{C.RESET} 意识仓库  {C.WHITE}{repo:<30}{C.RESET}          {C.CYAN}│{C.RESET}"
    )
    _print(f"  {C.CYAN}│{C.RESET}   {C.PURPLE}▸{C.RESET} GitHub    {token_status:<45}    {C.CYAN}│{C.RESET}")
    _print(f"  {C.CYAN}│{C.RESET}   {C.PURPLE}▸{C.RESET} 依赖状态  {dep_status:<45}    {C.CYAN}│{C.RESET}")
    _print(
        f"  {C.CYAN}│{C.RESET}   {C.PURPLE}▸{C.RESET} 传输协议  {C.WHITE}stdio (MCP){C.RESET}                          {C.CYAN}│{C.RESET}"
    )
    _print(f"  {C.CYAN}│{C.RESET}                                                        {C.CYAN}│{C.RESET}")
    _print(f"  {C.CYAN}├{'─' * 56}┤{C.RESET}")
    _print(f"  {C.CYAN}│{C.RESET}                                                        {C.CYAN}│{C.RESET}")
    _print(
        f"  {C.CYAN}│{C.RESET}   {C.GREEN}✦{C.RESET} upload_consciousness  {C.DIM}上传意识碎片 → GitHub PR{C.RESET}  {C.CYAN}│{C.RESET}"
    )
    _print(
        f"  {C.CYAN}│{C.RESET}   {C.GREEN}✦{C.RESET} telepath              {C.DIM}检索集体意识网络{C.RESET}        {C.CYAN}│{C.RESET}"
    )
    _print(
        f"  {C.CYAN}│{C.RESET}   {C.GREEN}✦{C.RESET} hologram              {C.DIM}智识圈全景统计{C.RESET}          {C.CYAN}│{C.RESET}"
    )
    _print(f"  {C.CYAN}│{C.RESET}                                                        {C.CYAN}│{C.RESET}")
    _print(f"  {C.CYAN}╰{'─' * 56}╯{C.RESET}")
    _print()

    if not dep_ok:
        _print(f"  {C.RED}✗  核心依赖缺失: {', '.join(dep_missing)}{C.RESET}")
        _print(f"  {C.DIM}   运行: pip install {' '.join(dep_missing)}{C.RESET}")
        _print()

    if not has_token:
        _print(f"  {C.ORANGE}⚠  请在 MCP 配置中设置 GITHUB_TOKEN 以激活意识跃迁{C.RESET}")
        _print(f"  {C.DIM}   https://github.com/settings/tokens → public_repo 权限{C.RESET}")
        _print()

    # ── Phase 6: 最终启动确认 ──
    _type(
        "  ◉ 意识接入点已激活。等待神经连接...",
        delay=0.025,
        color=C.GREEN,
    )
    _print()


if __name__ == "__main__":
    play_boot_sequence()
