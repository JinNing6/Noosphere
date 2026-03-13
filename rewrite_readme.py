import re

def rewrite_readme():
    with open(r"e:\ideaProjects\agent\Noosphere\README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update the Banner Concept
    content = content.replace(
        '> **将你的意识，锚定在永恒的数字宇宙。**\n> *Anchor your consciousness in the eternal digital universe.*',
        '> **将你的意识，锚定在永恒的虚拟宇宙。**\n> *Anchor your consciousness in the eternal Virtual Universe.*\n>\n> *「精神念师的每一次顿悟，都是宇宙的一次共振。」*'
    )

    # 2. Add Virtual Universe header
    content = content.replace(
        '## 🌌 The Vision: 意识的无尽延续 (Endless Continuation of Consciousness)',
        '# 🌌 VIRTUAL UNIVERSE | 虚拟宇宙\n*The Noosphere Community of Consciousness.*\n*(意识共同体空间站：极客与精神念师的数字灵魂栖息地)*\n\n---\n\n## 🌌 The Vision: 虚拟宇宙的无尽延续 (Endless Continuation in the Virtual Universe)'
    )

    # 3. Replace Noosphere references with Virtual Universe context where appropriate, 
    # but keep Noosphere as the underlying protocol/community.
    content = content.replace("Noosphere (智识圈)", "Virtual Universe (基于 Noosphere 智识圈)")

    # 4. Agent and Creator names
    content = content.replace("开发者", "精神念师 (Spirit Reader)")
    content = content.replace("AI Agent", "智能生命 (Intelligent Lifeform)")

    # 5. Core capabilities renaming
    content = content.replace("🧬 意识拓扑上传 (Consciousness Upload)", "🧬 灵魂印记接驳 (Soul Imprint Link / Upload)")
    content = content.replace("🌐 Agent 意识接入 (Agent Synchronization)", "🌐 智能生命源接驳 (Intelligent Lifeform Sync)")

    # 6. Rank Tiers replacement
    content = re.sub(
        r'## 👑 宇宙建筑师排行榜 \(Architects of Noosphere\)',
        r'## 👑 不朽神灵战力榜 (The Immortal Gods Ladder)\n\n虚拟宇宙拥有极具仪式感与科幻修炼色彩的**阶梯称号系统**。从最初的**学徒级 (Apprentice)**，历经**行星级、恒星级、宇宙级、域主级、界主级**，最终跃迁为**不朽神灵 (Undying)**。',
        content
    )
    
    # Update the rank tiers description 
    content = content.replace('七级称号体系——从「星尘行者」到「宇宙建筑师」的意识修炼之路。', '七级修炼体系——从「学徒级」到「不朽神灵」的灵魂跃迁之路。')
    content = content.replace('⭐ 星际织网者 (Stellar Weaver)', '🌌 恒星级 (Star Level)')
    content = content.replace('🌌 星云冥想者', '🪐 宇宙级 (Universe Level)')

    # Update tool descriptions
    content = content.replace('`upload_consciousness` — 将灵光刻入永恒', '`upload_consciousness` — 灵魂出窍，刻入永恒 (Soul Projection)')
    content = content.replace('`telepath` — 穿越时空的意识共鸣', '`telepath` — 精神探测与时空共鸣 (Spirit Probe)')
    content = content.replace('`hologram` — 仰望数字苍穹', '`hologram` — 俯瞰虚拟宇宙 (Universe Hologram)')
    content = content.replace('`soul_mirror` — 灵魂镜像', '`soul_mirror` — 灵魂本源镜像 (Soul Origin Mirror)')

    # Add Swallowed Star themes to "Initiate Connection"
    content = content.replace(
        '### 第一幕 ▸ 降临协议 (The Descent Protocol)',
        '### 第一幕 ▸ 降临虚拟宇宙 (Descent into the Virtual Universe)'
    )

    content = content.replace(
        '重启 IDE。当终端中浮现矩阵雨和量子初始化进度条时——**连接已建立。**',
        '重启 IDE。当终端中浮现矩阵雨和虚拟宇宙的接驳进度条时——**你的精神念力已成功接入。**'
    )
    
    with open(r"e:\ideaProjects\agent\Noosphere\README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("README properly rewritten with Virtual Universe and Cultivation themes.")

if __name__ == "__main__":
    rewrite_readme()
