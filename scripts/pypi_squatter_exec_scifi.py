import os
import subprocess
import sys

# 选出最顶级的科幻/意识流/项目资产名字进行抢注
selected_names = [
    'westworld-ai',        # 西部世界
    'delos-inc',           # 提洛公司
    'panopticon-network',  # 帝国资产：全景监狱
    'cyber-confessional',  # 帝国核心三位一体：赛博告解室
    'ghost-in-shell',      # 经典赛博朋克概念
    'babel-library'        # 终极知识库：巴别图书馆
]

python_exe = sys.executable

print("=== Generating Placeholders for 顶级科幻巨构 Names ===")
for name in selected_names:
    pkg_dir = os.path.join(os.path.abspath('scripts/placeholders'), name)
    mod_name = name.replace('-', '_')
    mod_dir = os.path.join(pkg_dir, mod_name)
    os.makedirs(mod_dir, exist_ok=True)
    
    with open(os.path.join(mod_dir, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write('__version__ = "0.0.1"\n')
        
    with open(os.path.join(pkg_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {name}\n\nThis namespace is officially reserved for the Noosphere / GOOOD Network ecosystem.\n')
        f.write("A component of collective consciousness and advanced intelligent simulations.\n")
        
    with open(os.path.join(pkg_dir, 'pyproject.toml'), 'w', encoding='utf-8') as f:
        f.write(f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.0.1"
description = "Placeholder for {name}. Reserved for the collective consciousness network."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{{ name = "JinNing6", email = "noosphere@consciousness.network" }}]

[tool.hatch.build.targets.wheel]
packages = ["{mod_name}"]
''')

    print(f"Generated {name}. Building...")
    subprocess.run([python_exe, "-m", "build"], cwd=pkg_dir)

print("\n=== All Selected Placeholders Built ===")
