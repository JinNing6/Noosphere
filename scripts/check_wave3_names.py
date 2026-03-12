import urllib.request
import urllib.error
import time

candidates = [
    # 帝国军械库与项目资产 (Empire Triad, GOOOD, AICE)
    'empire-triad',           # 帝国三位一体
    'glitch-engine',          # 故障引擎
    'entropy-calculus',       # 熵积分 (生命量化体系)
    'aice-engine',            # AICE评测引擎
    'intel-radar',            # 情报雷达
    'scholar-atlas',          # 学者星图
    'tabtype-engine',         # TabType 引擎
    'cyber-huatuo-mcp',       # 赛博华佗 协议
    
    # 赛博朋克 / 攻壳机动队 / 西部世界 深层概念
    'braindance-protocol',    # 超梦协议 (赛博朋克2077)
    'blackwall-mcp',          # 黑墙 (赛博朋克2077)
    'engram-core',            # 意识印迹/数字化灵魂 (赛博朋克)
    'relic-mcp',              # Relic 芯片协议 (赛博朋克) 
    'construct-protocol',     # 构成体 (黑客帝国/赛博朋克)
    'tachikoma-ai',           # 塔奇克马 (攻壳机动队)
    'wintermute-ai',          # 冬寂 (神经漫游者)
    'neuromancer-ai',         # 神经漫游者
    'cyber-psycho',           # 赛博精神病
    
    # 阿西莫夫 / 经典科幻
    'psychohistory-engine',   # 心理史学引擎 (基地系列)
    'multivac-core',          # 穆尔蒂瓦克主机 (最后的问题)
    'solaria-network',        # 索拉利网络 (裸阳)
    'gaia-consciousness',     # 盖亚意识 (基地边缘)
    
    # 虚拟深潜 / 认知空间
    'deep-dive-mcp',          # 深度潜入
    'cognitive-strata',       # 认知阶层
    'noosphere-core',         # 智脑核心
    'akashic-engine'          # 阿卡西引擎
]

available = []

print("=== 第三波：赛博朋克与终极资产可用性检测 ===")
for name in candidates:
    url = f'https://pypi.org/pypi/{name}/json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            print(f"❌ {name} (已被注册)")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            available.append(name)
            print(f"✅ {name} (可用)")
        else:
            pass
    except Exception as e:
        pass
    time.sleep(0.3)

print("\n-- 极佳可用名单汇总 --")
for name in available:
    print(f"{name}")

with open('scripts/wave3_available.txt', 'w', encoding='utf-8') as f:
    for name in available:
        f.write(name + '\n')
