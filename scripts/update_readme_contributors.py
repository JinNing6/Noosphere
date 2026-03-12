"""
🌌 Noosphere 宇宙建筑师排行榜 — 真实 GitHub 数据驱动

从 GitHub REST API 获取真实 Contributors 数据（基于 commit 数量），
计算灵能总值 (Psi = commits × 10)，赋予对应的史诗称号，
然后自动覆写 README.md 中的排行表格。

可在本地手动运行，也可由 GitHub Actions 定时触发。
"""

import json
import os
import re
import time
import urllib.error
import urllib.request

# ──────────────── 配置 ────────────────

REPO_OWNER = "JinNing6"
REPO_NAME = "Noosphere"
PSI_MULTIPLIER = 10  # 每个 commit 的灵能权重

# GitHub API endpoints
CONTRIBUTORS_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contributors"

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


# ──────────────── GitHub API 调用 ────────────────


def fetch_contributors() -> list[dict]:
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
        每项含 login, avatar_url, contributions, psi 字段
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Noosphere-Contributor-Updater",
    }
    if token:
        headers["Authorization"] = f"token {token}"
        print("✅ 使用 GITHUB_TOKEN 认证 (高速模式)")
    else:
        print("⚠️  未检测到 GITHUB_TOKEN，使用匿名模式 (60 requests/hour 限制)")

    url = f"{CONTRIBUTORS_API}?per_page=100"

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"📡 正在获取贡献者数据... (第 {attempt}/{MAX_RETRIES} 次)")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.getcode()

                if status == 202:
                    # GitHub 正在后台计算统计数据
                    print(f"⏳ GitHub 正在计算统计数据，{RETRY_DELAY_SECONDS}s 后重试...")
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
                print(f"❌ API 速率限制 (403)。请设置 GITHUB_TOKEN 环境变量。")
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


# ──────────────── Markdown 生成 ────────────────


def generate_markdown_table(contributors: list[dict]) -> str:
    """生成 README 排行榜 Markdown 表格。"""
    if not contributors:
        return "> *目前宇宙还处于奇点阶段，等待第一批星尘行者的降临...*\n"

    table = "| 序列 | 宇宙缔造者 (Contributor) | 灵能总值 (Total Psi) | 意志形态与阶梯称号 (Cosmic Title) | 跃迁阈值 |\n"
    table += "|:---:|:---|:---:|:---|:---|\n"

    for i, c in enumerate(contributors):
        badge = get_rank_badge(i)
        icon, title, threshold = calculate_title(c["psi"])
        login = c["login"]
        commits = c["commits"]
        psi = c["psi"]

        # 在 Psi 后面注明来源 (commit 数)
        row = f"| {badge} | **[{login}](https://github.com/{login})** | **{psi}** ({commits} commits) | {icon} **{title}** | {threshold} |\n"
        table += row

    return table


# ──────────────── README 更新 ────────────────


def update_readme(new_table_content: str):
    """替换 README.md 中的排行表格区块。"""
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    readme_abs_path = os.path.abspath(readme_path)

    with open(readme_abs_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配从表头到注释说明之间的区块
    pattern = re.compile(
        r"(\| 序列 \| 宇宙缔造者 \(Contributor\).*?)(?=\n> \*注：这些卓越的意志)",
        re.DOTALL,
    )

    if not pattern.search(content):
        print("⚠️  未找到 README 中的排行表格标记。跳过更新。")
        return

    match = pattern.search(content)
    if match:
        start_idx = match.start()
        end_idx = match.end()
        updated_content = content[:start_idx] + new_table_content + content[end_idx:]

        with open(readme_abs_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"✅ 已更新 README.md: {readme_abs_path}")


# ──────────────── 主入口 ────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🌌 Noosphere 宇宙建筑师排行榜 — 真实数据更新")
    print("=" * 60)

    contributors = fetch_contributors()
    if contributors:
        print(f"\n📊 贡献者统计:")
        for i, c in enumerate(contributors):
            icon, title, _ = calculate_title(c["psi"])
            print(f"   #{i+1} {c['login']}: {c['commits']} commits → Psi {c['psi']} → {icon} {title}")

        table_md = generate_markdown_table(contributors)
        update_readme(table_md)
    else:
        print("\n⚠️  无贡献者数据。README 保持不变。")

    print("\n" + "=" * 60)
    print("🏁 完成")
    print("=" * 60)
