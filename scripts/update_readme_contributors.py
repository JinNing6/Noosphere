import json
import re
import os
import urllib.request
import urllib.error

# Configuration
REPO_OWNER = "JinNing6"
REPO_NAME = "Noosphere"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/stats/contributors"

def calculate_title(score: int) -> tuple[str, str, str]:
    """Calculate the title, icon, and display label based on total commits (Psi)."""
    if score >= 3000:
        return "👑", "宇宙建筑师 (Architect of Noosphere)", "`Psi ≥ 3000`"
    if score >= 1000:
        return "🪐", "星海领航员 (Stellar Navigator)", "`Psi ≥ 1000`"
    if score >= 500:
        return "🌌", "真理探索家 (Truth Seeker)", "`Psi ≥ 500`"
    if score >= 100:
        return "💫", "记忆编织者 (Memory Weaver)", "`Psi ≥ 100`"
    return "🌟", "星尘行者 (Stardust Walker)", "`基础序列`"

def get_rank_badge(index: int) -> str:
    """Get the shiny rank badge for the top 3."""
    if index == 0:
        return "🏆 **#1**"
    if index == 1:
        return "🥈 **#2**"
    if index == 2:
        return "🥉 **#3**"
    return f"🔹 **#{index + 1}**"

def fetch_contributors():
    """Fetch contributors stats (Mock MVP for Demonstration).
    
    In a real production environment, this should be triggered via GitHub Actions
    with a GITHUB_TOKEN to avoid 403 Rate Limit errors and correctly read the
    '/stats/contributors' endpoint caching mechanisms.
    """
    print(f"Generating Noosphere Contributor Rankings MVP...")
    
    # 模拟从真实 GitHub API 和数据库聚合的结果
    # 灵能总值 (Psi) = (Commits * 10) + 顿悟/决策权重
    contributors = [
        {"login": "Albus", "psi": 3430},
        {"login": "JinNing6", "psi": 1525},
        {"login": "Neo", "psi": 1202},
        {"login": "Oracle", "psi": 906},
        {"login": "Trinity", "psi": 895},
        {"login": "Morpheus", "psi": 730},
        {"login": "Cypher", "psi": 255},
        {"login": "Link", "psi": 72},
    ]
        
    # Sort by Psi descending
    contributors.sort(key=lambda x: x["psi"], reverse=True)
    return contributors

def generate_markdown_table(contributors) -> str:
    """Generate the markdown table for the README."""
    if not contributors:
        return "> *目前宇宙还处于奇点阶段，等待第一批星尘行者的降临...*\n"
        
    table = "| 序列 | 宇宙缔造者 (Contributor) | 灵能总值 (Total Psi) | 意志形态与阶梯称号 (Cosmic Title) | 跃迁阈值 |\n"
    table += "|:---:|:---|:---:|:---|:---|\n"
    
    for i, c in enumerate(contributors):
        badge = get_rank_badge(i)
        icon, title, threshold = calculate_title(c["psi"])
        row = f"| {badge} | **{c['login']}** | **{c['psi']}** | {icon} **{title}** | {threshold} |\n"
        table += row
        
    return table

def update_readme(new_table_content: str):
    """Replace the table section in the README.md file."""
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    readme_abs_path = os.path.abspath(readme_path)
    
    with open(readme_abs_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find the section to replace: from the table header to the note blockquote
    pattern = re.compile(
        r"(\| 序列 \| 宇宙缔造者 \(Contributor\).*?)(?=\n> \*注：这些卓越的意志)", 
        re.DOTALL
    )
    
    if not pattern.search(content):
        print("Could not find the target table pattern in README.md")
        return
        
    # Regex sub needs the replacement string, but replace groups behavior \1 needs escaping
    # Better to just split and combine
    match = pattern.search(content)
    if match:
        start_idx = match.start()
        end_idx = match.end()
        updated_content = content[:start_idx] + new_table_content + content[end_idx:]
    
        with open(readme_abs_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
            
        print(f"Successfully updated README.md at {readme_abs_path}")

if __name__ == "__main__":
    contributors = fetch_contributors()
    if contributors:
        print(f"Found {len(contributors)} contributors.")
        table_md = generate_markdown_table(contributors)
        update_readme(table_md)
    else:
        print("No contributor data found or failed to fetch.")
