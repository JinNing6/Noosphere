import os
import subprocess
import sys

# 读取刚刚生成的 wave3_available.txt
with open('scripts/wave3_available.txt', 'r', encoding='utf-8') as f:
    wave3_names = [line.strip() for line in f if line.strip()]

python_exe = sys.executable

print('=== 开始批量生成并构建第 3 波顶级包 ===')
for name in wave3_names:
    pkg_dir = os.path.join(os.path.abspath('scripts/placeholders'), name)
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
description = "Placeholder for {name}. Dedicated to collective consciousness."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{{ name = "JinNing6", email = "noosphere@consciousness.network" }}]

[tool.hatch.build.targets.wheel]
packages = ["{mod_name}"]
''')
    print(f'Building {name}...')
    subprocess.run([python_exe, '-m', 'build'], cwd=pkg_dir)

print('\n=== 全部构建完成 ===')
