import urllib.request
import os
import subprocess
import sys

names = [
    'cyber-evolution',
    'evolution-engine',
    'evolution-protocol',
    'noosphere-evolution',
    'digital-evolution'
]

available = []
print('=== 检测开始 ===')
for name in names:
    try:
        req = urllib.request.Request(f'https://pypi.org/pypi/{name}/json', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            print(f'❌ {name} 已被注册！')
    except Exception as e:
        print(f'✅ {name} 可用！')
        available.append(name)

if not available:
    print('😭 都没有了...')
    sys.exit(0)

print('\n=== 开始生成包 ===')
for name in available:
    pkg_dir = os.path.abspath(os.path.join('scripts/placeholders', name))
    mod_name = name.replace('-', '_')
    mod_dir = os.path.join(pkg_dir, mod_name)
    os.makedirs(mod_dir, exist_ok=True)
    
    with open(os.path.join(mod_dir, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write('__version__ = "0.0.1"\n')
        
    with open(os.path.join(pkg_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {name}\n\nThis namespace is automatically reserved for the Noosphere / GOOOD Network ecosystem as a structural dependency.\n')
        
    with open(os.path.join(pkg_dir, 'pyproject.toml'), 'w', encoding='utf-8') as f:
        f.write(f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.0.1"
description = "Placeholder for {name}. Dedicated to digital collective evolution."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{{ name = "JinNing6", email = "noosphere@consciousness.network" }}]

[tool.hatch.build.targets.wheel]
packages = ["{mod_name}"]
''')
    print(f'打包 {name}...')
    subprocess.run([sys.executable, '-m', 'build'], cwd=pkg_dir)

print('\n打包完成！(已触发限流，此批包不执行 twine，留待稍后手动上传)')
