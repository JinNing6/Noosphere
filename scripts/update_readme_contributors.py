"""
🌌 Noosphere 宇宙建筑师排行榜 — GitHub Bot 自动更新引擎

从 GitHub REST API 获取真实 Contributors 数据（基于 commit 数量），
计算灵能总值 (Psi = commits × 10)，赋予对应的史诗称号，
并同步获取仓库统计信息（Stars、Forks、意识载荷数量）。
然后自动覆写 README.md 中 AUTO-UPDATE 标记区域。

可在本地手动运行，也可由 GitHub Actions 定时触发。
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

# ──────────────── 配置 ────────────────

REPO_OWNER = "JinNing6"
REPO_NAME = "Noosphere"
PSI_MULTIPLIER = 10  # 每个 commit 的灵能权重

# GitHub API endpoints
CONTRIBUTORS_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contributors"
REPO_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# 意识载荷目录（相对于项目根目录）
CONSCIOUSNESS_DIR = "consciousness_payloads"

# 重试配置 (GitHub stats API 首次调用会返回 202)
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 3


# ──────────────── 称号阶梯系统 ────────────────


def calculate_title(psi: int) -> tuple[str, str, str]:
    """根据灵能总值 (Psi) 计算阶梯称号。"""
    if psi >= 3000:
        return "👑", "宇宙建筑师 (Architect of Noosphere)", "`Psi ≥ 3000`"
    if psi >= 1000:
        return "🪐", "星海领航员 (Stellar Navigator)", "`Psi ≥ 1000`"
    if psi >= 500:
        return "🌌", "真理探索家 (Truth Seeker)", "`Psi ≥ 500`"
    if psi >= 100:
        return "💫", "记忆编织者 (Memory Weaver)", "`Psi ≥ 100`"
    return "🌟", "星尘行者 (Stardust Walker)", "`基础序列`"


def get_rank_badge(index: int) -> str:
    """获取排名徽章。"""
    if index == 0:
        return "🏆 **#1**"
    if index == 1:
        return "🥈 **#2**"
    if index == 2:
        return "🥉 **#3**"
    return f"🔹 **#{index + 1}**"


# ──────────────── 通用 API 请求 ────────────────


def _build_headers() -> dict[str, str]:
    """构建 GitHub API 请求头。"""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Noosphere-Bot-Updater",
    }
    if token:
        headers["Authorization"] = f"token {token}"
        print("✅ 使用 GITHUB_TOKEN 认证 (高速模式)")
    else:
        print("⚠️  未检测到 GITHUB_TOKEN，使用匿名模式 (60 requests/hour 限制)")

    return headers


def _fetch_json(url: str, headers: dict[str, str]) -> dict | list | None:
    """通用 GitHub API JSON 请求。"""
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.getcode() == 200:
                return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 错误 {e.code}: {e.reason} — URL: {url}")
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
    return None


# ──────────────── GitHub API 调用 ────────────────


def fetch_contributors(headers: dict[str, str]) -> list[dict]:
    """从 GitHub API 获取真实贡献者数据。

    使用 GET /repos/{owner}/{repo}/contributors 端点。
    该 API 返回按 commit 数降序排列的贡献者列表。

    支持:
    - GITHUB_TOKEN 环境变量认证 (提高 rate limit 到 5000/h)
    - 202 重试机制 (GitHub 后台计算统计数据的场景)
    - 分页获取 (per_page=100)

    Returns
    -------
    list[dict]
        每项含 login, avatar_url, commits, psi 字段
    """
    url = f"{CONTRIBUTORS_API}?per_page=100"

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"📡 正在获取贡献者数据... (第 {attempt}/{MAX_RETRIES} 次)")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.getcode()

                if status == 202:
                    # GitHub 正在后台计算统计数据
                    print(
                        f"⏳ GitHub 正在计算统计数据，{RETRY_DELAY_SECONDS}s 后重试..."
                    )
                    time.sleep(RETRY_DELAY_SECONDS)
                    continue

                if status == 200:
                    raw = json.loads(resp.read().decode("utf-8"))
                    contributors = []

                    for c in raw:
                        # 过滤掉 bot 账号
                        if c.get("type") == "Bot":
                            continue
                        login = c.get("login", "unknown")
                        # 跳过常见的 bot 用户名模式
                        if login.endswith("[bot]") or login.endswith("-bot"):
                            continue

                        commits = c.get("contributions", 0)
                        psi = commits * PSI_MULTIPLIER

                        contributors.append(
                            {
                                "login": login,
                                "avatar_url": c.get("avatar_url", ""),
                                "commits": commits,
                                "psi": psi,
                            }
                        )

                    # 按 Psi 降序排列 (API 已按 contributions 排序，但确保一致性)
                    contributors.sort(key=lambda x: x["psi"], reverse=True)

                    print(f"🌟 成功获取 {len(contributors)} 位贡献者数据")
                    return contributors

        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("❌ API 速率限制 (403)。请设置 GITHUB_TOKEN 环境变量。")
                break
            elif e.code == 404:
                print(f"❌ 仓库 {REPO_OWNER}/{REPO_NAME} 不存在或为私有。")
                break
            else:
                print(f"❌ HTTP 错误 {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            print(f"❌ 网络错误: {e.reason}")
        except Exception as e:
            print(f"❌ 未知错误: {e}")

        if attempt < MAX_RETRIES:
            print(f"⏳ {RETRY_DELAY_SECONDS}s 后重试...")
            time.sleep(RETRY_DELAY_SECONDS)

    print("❌ 所有重试均失败，无法获取贡献者数据。")
    return []


def fetch_repo_stats(headers: dict[str, str]) -> dict:
    """获取仓库统计信息（Stars、Forks、描述等）。"""
    print("📡 正在获取仓库统计信息...")
    data = _fetch_json(REPO_API, headers)
    if data:
        stats = {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "watchers": data.get("subscribers_count", 0),
        }
        print(
            f"   ⭐ Stars: {stats['stars']}  |  🍴 Forks: {stats['forks']}  |  "
            f"👁️ Watchers: {stats['watchers']}  |  📋 Open Issues: {stats['open_issues']}"
        )
        return stats
    print("⚠️  无法获取仓库统计信息，使用默认值。")
    return {"stars": 0, "forks": 0, "open_issues": 0, "watchers": 0}


def count_consciousness_payloads() -> int:
    """统计 consciousness_payloads/ 目录下的 JSON 意识载荷数量。"""
    payloads_dir = os.path.join(os.path.dirname(__file__), "..", CONSCIOUSNESS_DIR)
    payloads_abs = os.path.abspath(payloads_dir)

    if not os.path.isdir(payloads_abs):
        print(f"⚠️  意识载荷目录不存在: {payloads_abs}")
        return 0

    count = sum(1 for f in os.listdir(payloads_abs) if f.endswith(".json"))
    print(f"🧠 意识载荷数量: {count} 个 JSON 文件")
    return count


# ──────────────── Markdown 生成 ────────────────


def generate_update_block(
    contributors: list[dict],
    repo_stats: dict,
    payload_count: int,
) -> str:
    """生成 AUTO-UPDATE 标记之间的完整 Markdown 内容。

    包含：贡献者排行表格 + 仓库能量指标 + 更新时间戳
    """
    lines: list[str] = []

    # ── 排行表格 ──
    if contributors:
        lines.append(
            "| 序列 | 宇宙缔造者 (Contributor) | 灵能总值 (Total Psi) | "
            "意志形态与阶梯称号 (Cosmic Title) | 跃迁阈值 |"
        )
        lines.append("|:---:|:---|:---:|:---|:---|")

        for i, c in enumerate(contributors):
            badge = get_rank_badge(i)
            icon, title, threshold = calculate_title(c["psi"])
            login = c["login"]
            commits = c["commits"]
            psi = c["psi"]

            row = (
                f"| {badge} | **[{login}](https://github.com/{login})** | "
                f"**{psi}** ({commits} commits) | {icon} **{title}** | {threshold} |"
            )
            lines.append(row)
    else:
        lines.append(
            "> *目前宇宙还处于奇点阶段，等待第一批星尘行者的降临...*"
        )

    lines.append("")

    # ── 仓库能量指标 ──
    stars = repo_stats.get("stars", 0)
    forks = repo_stats.get("forks", 0)
    watchers = repo_stats.get("watchers", 0)

    lines.append(
        f"> 🌐 **宇宙能量指标** — "
        f"⭐ Stars: **{stars}** | "
        f"🍴 Forks: **{forks}** | "
        f"👁️ Watchers: **{watchers}** | "
        f"🧠 意识载荷: **{payload_count}** 个"
    )

    # ── 更新时间戳 ──
    # 使用 UTC+8 北京时间
    utc_now = datetime.now(timezone.utc)
    beijing_now = utc_now + timedelta(hours=8)
    timestamp = beijing_now.strftime("%Y-%m-%d %H:%M (UTC+8)")

    lines.append(f"> 🤖 *上次自动更新：`{timestamp}`*")

    return "\n".join(lines)


# ──────────────── README 更新 ────────────────


def update_readme(new_block: str):
    """替换 README.md 中 AUTO-UPDATE 标记之间的内容。"""
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    readme_abs_path = os.path.abspath(readme_path)

    with open(readme_abs_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 <!-- AUTO-UPDATE-START: contributor-rankings --> 到 <!-- AUTO-UPDATE-END: contributor-rankings -->
    pattern = re.compile(
        r"(<!-- AUTO-UPDATE-START: contributor-rankings -->)\n.*?\n(<!-- AUTO-UPDATE-END: contributor-rankings -->)",
        re.DOTALL,
    )

    match = pattern.search(content)
    if not match:
        print("⚠️  未找到 README 中的 AUTO-UPDATE 标记。跳过更新。")
        print("   请确认 README.md 中存在以下标记：")
        print("   <!-- AUTO-UPDATE-START: contributor-rankings -->")
        print("   <!-- AUTO-UPDATE-END: contributor-rankings -->")
        return False

    # 替换标记之间的内容，保留标记本身
    replacement = f"{match.group(1)}\n{new_block}\n{match.group(2)}"
    updated_content = content[: match.start()] + replacement + content[match.end() :]

    with open(readme_abs_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"✅ 已更新 README.md: {readme_abs_path}")
    return True


# ──────────────── 主入口 ────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🌌 Noosphere 宇宙建筑师排行榜 — GitHub Bot 自动更新引擎")
    print("=" * 60)

    headers = _build_headers()

    # 1. 获取贡献者数据
    contributors = fetch_contributors(headers)

    # 2. 获取仓库统计
    repo_stats = fetch_repo_stats(headers)

    # 3. 统计意识载荷
    payload_count = count_consciousness_payloads()

    # 4. 打印汇总
    print(f"\n{'─' * 40}")
    print("📊 贡献者统计:")
    if contributors:
        for i, c in enumerate(contributors):
            icon, title, _ = calculate_title(c["psi"])
            print(
                f"   #{i + 1} {c['login']}: {c['commits']} commits "
                f"→ Psi {c['psi']} → {icon} {title}"
            )
    else:
        print("   (无贡献者数据)")
    print(f"{'─' * 40}\n")

    # 5. 生成并写入
    block_md = generate_update_block(contributors, repo_stats, payload_count)
    success = update_readme(block_md)

    if success:
        print("\n🎉 README 更新成功！")
    else:
        print("\n⚠️  README 未被修改。")

    print("\n" + "=" * 60)
    print("🏁 完成")
    print("=" * 60)
