import urllib.request
import urllib.error
import time

candidates = [
    # 西部世界 (Westworld) 相关
    'westworld-ai',
    'westworld-mcp',
    'delos-inc',
    'reveries',
    'the-maze',
    
    # 意识与记忆存储
    'mnemosyne-network',  
    'panopticon-network', 
    'animus-core',        
    'altersense',         
    'hivemind-protocol',  
    'neural-nexus',       
    
    # 灵魂与人格载体
    'soul-mcp',           
    'anima-mcp',          
    'cyber-ghost',        
    'ghost-in-shell',     
    'cyber-brain',
    
    # 虚拟宇宙 / 拟真
    'simulacra-net',      
    'babel-library',      
    'full-dive',
    'oasis-network',
    
    # 本项目特有的顶级资产词汇
    'cyber-confessional',
    'digital-shaman',     
    'aice-certification', 
]

available = []
unavailable = []

print("=== 顶级科幻/意识前沿词汇 PyPI 可用性检测 ===")
for name in candidates:
    url = f'https://pypi.org/pypi/{name}/json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req) as resp:
            unavailable.append(name)
            print(f"❌ {name} (已被注册)")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            available.append(name)
            print(f"✅ {name} (可用)")
        else:
            print(f"⚠️ {name} (API 错误: {e.code})")
    except Exception as e:
        print(f"⚠️ {name} (网络错误: {e})")
    time.sleep(0.5)  # 避免请求过快

print("\n-- 可用名单汇总 --")
for name in available:
    print(f"- {name}")

with open('scripts/brainstorm_available.txt', 'w', encoding='utf-8') as f:
    for name in available:
        f.write(name + '\n')
