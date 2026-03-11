"""
Wikipedia 数据预拉取脚本

从 Wikipedia REST API 预拉取知识节点的摘要、缩略图 URL 和链接，
存为静态 JSON 供前端直接使用（无需运行时 API 调用）。

Usage:
    python scripts/fetch_wikipedia.py
"""

import json
import time
import httpx
from pathlib import Path

# 输出路径
OUTPUT_PATH = Path(__file__).parent.parent / "src" / "data" / "wikipedia_cache.json"

# 要拉取的条目（英文 Wikipedia 标题 → 中文标题映射）
ARTICLES = {
    # ── 数学 & 逻辑 ──
    "Euler's_formula": "欧拉公式",
    "Gödel's_incompleteness_theorems": "哥德尔不完备定理",
    "Game_theory": "博弈论",
    "Fractal": "分形",
    "Pi": "圆周率",
    "Fibonacci_sequence": "斐波那契数列",
    "Chaos_theory": "混沌理论",
    "Topology": "拓扑学",

    # ── 物理 & 宇宙 ──
    "Quantum_entanglement": "量子纠缠",
    "Black_hole": "黑洞",
    "Dark_matter": "暗物质",
    "General_relativity": "广义相对论",
    "Wave–particle_duality": "波粒二象性",
    "String_theory": "弦理论",
    "Entropy": "熵",
    "Standard_Model": "标准模型",

    # ── 生命科学 ──
    "CRISPR": "CRISPR 基因编辑",
    "Neuroplasticity": "神经可塑性",
    "Telomere": "端粒",
    "DNA": "DNA",
    "Evolution": "进化论",
    "Photosynthesis": "光合作用",
    "Consciousness": "意识",
    "Epigenetics": "表观遗传学",

    # ── 哲学 & 思想 ──
    "Brain_in_a_vat": "缸中之脑",
    "Existentialism": "存在主义",
    "Taoism": "道家思想",
    "Stoicism": "斯多葛主义",
    "Dialectics": "辩证法",
    "Phenomenology_(philosophy)": "现象学",
    "Noosphere": "智识圈",
    "Panpsychism": "泛心论",

    # ── 艺术 & 创造 ──
    "Golden_ratio": "黄金分割",
    "Harmony": "和声学",
    "Perspective_(graphical)": "透视法",
    "Venus_de_Milo": "断臂维纳斯",
    "Wabi-sabi": "侘寂美学",
    "Bauhaus": "包豪斯",
    "Synesthesia": "联觉",

    # ── 工程 & 技术 ──
    "Internet_protocol_suite": "互联网协议栈",
    "Nuclear_fusion": "核聚变",
    "Semiconductor": "半导体",
    "Cryptography": "密码学",
    "3D_printing": "3D 打印",
    "Nanotechnology": "纳米技术",
    "Quantum_computing": "量子计算",

    # ── 社会 & 历史 ──
    "Silk_Road": "丝绸之路",
    "Renaissance": "文艺复兴",
    "Industrial_Revolution": "工业革命",
    "Library_of_Alexandria": "亚历山大图书馆",
    "Rosetta_Stone": "罗塞塔石碑",
    "Gutenberg_Bible": "古腾堡圣经",
    "Universal_Declaration_of_Human_Rights": "世界人权宣言",

    # ── AI & 计算 ──
    "Transformer_(deep_learning_architecture)": "Transformer",
    "Reinforcement_learning": "强化学习",
    "Artificial_general_intelligence": "通用人工智能",
    "Neural_network_(machine_learning)": "神经网络",
    "Turing_test": "图灵测试",
    "Chinese_room": "中文房间",
    "Attention_(machine_learning)": "注意力机制",
}

# 学科分类
DISCIPLINE_MAP = {
    "Euler's_formula": "math", "Gödel's_incompleteness_theorems": "math",
    "Game_theory": "math", "Fractal": "math", "Pi": "math",
    "Fibonacci_sequence": "math", "Chaos_theory": "math", "Topology": "math",

    "Quantum_entanglement": "physics", "Black_hole": "physics",
    "Dark_matter": "physics", "General_relativity": "physics",
    "Wave–particle_duality": "physics", "String_theory": "physics",
    "Entropy": "physics", "Standard_Model": "physics",

    "CRISPR": "biology", "Neuroplasticity": "biology", "Telomere": "biology",
    "DNA": "biology", "Evolution": "biology", "Photosynthesis": "biology",
    "Consciousness": "biology", "Epigenetics": "biology",

    "Brain_in_a_vat": "philosophy", "Existentialism": "philosophy",
    "Taoism": "philosophy", "Stoicism": "philosophy",
    "Dialectics": "philosophy", "Phenomenology_(philosophy)": "philosophy",
    "Noosphere": "philosophy", "Panpsychism": "philosophy",

    "Golden_ratio": "art", "Harmony": "art",
    "Perspective_(graphical)": "art", "Venus_de_Milo": "art",
    "Wabi-sabi": "art", "Bauhaus": "art", "Synesthesia": "art",

    "Internet_protocol_suite": "engineering", "Nuclear_fusion": "engineering",
    "Semiconductor": "engineering", "Cryptography": "engineering",
    "3D_printing": "engineering", "Nanotechnology": "engineering",
    "Quantum_computing": "engineering",

    "Silk_Road": "history", "Renaissance": "history",
    "Industrial_Revolution": "history", "Library_of_Alexandria": "history",
    "Rosetta_Stone": "history", "Gutenberg_Bible": "history",
    "Universal_Declaration_of_Human_Rights": "history",

    "Transformer_(deep_learning_architecture)": "ai",
    "Reinforcement_learning": "ai", "Artificial_general_intelligence": "ai",
    "Neural_network_(machine_learning)": "ai", "Turing_test": "ai",
    "Chinese_room": "ai", "Attention_(machine_learning)": "ai",
}


def fetch_summary(title: str) -> dict | None:
    """从 Wikipedia REST API 获取文章摘要"""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    headers = {
        "User-Agent": "Noosphere/1.0 (https://github.com/JinNing6/Noosphere; noosphere@example.com)"
    }
    try:
        resp = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"  ⚠️ {title}: HTTP {resp.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ {title}: {e}")
        return None


def main():
    print("🧠 Noosphere Wikipedia 数据预拉取")
    print(f"📊 共 {len(ARTICLES)} 个条目")
    print("=" * 50)

    results = {}
    for i, (en_title, zh_title) in enumerate(ARTICLES.items(), 1):
        print(f"  [{i:2d}/{len(ARTICLES)}] {zh_title} ({en_title})...", end=" ")
        data = fetch_summary(en_title)
        if data:
            thumbnail = None
            if "thumbnail" in data:
                thumbnail = data["thumbnail"].get("source")

            results[en_title] = {
                "title_en": data.get("title", en_title.replace("_", " ")),
                "title_zh": zh_title,
                "summary": data.get("extract", ""),
                "thumbnail": thumbnail,
                "wiki_url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{en_title}"),
                "discipline": DISCIPLINE_MAP.get(en_title, "other"),
            }
            print("✅")
        else:
            results[en_title] = {
                "title_en": en_title.replace("_", " "),
                "title_zh": zh_title,
                "summary": "",
                "thumbnail": None,
                "wiki_url": f"https://en.wikipedia.org/wiki/{en_title}",
                "discipline": DISCIPLINE_MAP.get(en_title, "other"),
            }
            print("⚠️ fallback")

        time.sleep(0.1)  # 礼貌性延迟

    # 保存
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"✅ 数据已保存到 {OUTPUT_PATH}")
    print(f"📦 文件大小: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    thumbnails = sum(1 for v in results.values() if v["thumbnail"])
    print(f"📸 有缩略图: {thumbnails}/{len(results)}")


if __name__ == "__main__":
    main()
