import os
import subprocess
import sys

names = [
    'akashic-network',
    'noosphere-network',
    'collective-consciousness',
    'cyber-huatuo',
    'goood-mcp'
]

python_exe = sys.executable

print("=== Generating Placeholders for Selected Names ===")
for name in names:
    pkg_dir = os.path.join(os.path.abspath('scripts/placeholders'), name)
    mod_name = name.replace('-', '_')
    mod_dir = os.path.join(pkg_dir, mod_name)
    os.makedirs(mod_dir, exist_ok=True)
    
    with open(os.path.join(mod_dir, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write('__version__ = "0.0.1"\n')
        
    with open(os.path.join(pkg_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {name}\n\nThis namespace is officially reserved for the Noosphere / GOOOD Network ecosystem.\n')
        
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
    # 使用 python -m build 这个标准的打包命令（如果是用 PyPA build）或使用 hatch build
    subprocess.run([python_exe, "-m", "build"], cwd=pkg_dir)

print("\n=== All Selected Placeholders Built ===")
print("To publish, please navigate to 'scripts/placeholders/<package>' and run 'twine upload dist/*'")
