import urllib.request
import json
import os
import subprocess
import sys

name = 'open-consciousness'

try:
    req = urllib.request.Request(f'https://pypi.org/pypi/{name}/json', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        print(f'❌ {name} 已被注册！')
        sys.exit(1)
except Exception as e:
    print(f'✅ {name} 可用，准备抢占...')

pkg_dir = os.path.abspath(os.path.join('scripts/placeholders', name))
mod_name = name.replace('-', '_')
mod_dir = os.path.join(pkg_dir, mod_name)
os.makedirs(mod_dir, exist_ok=True)

with open(os.path.join(mod_dir, '__init__.py'), 'w', encoding='utf-8') as f:
    f.write('__version__ = "0.0.1"\n')

with open(os.path.join(pkg_dir, 'README.md'), 'w', encoding='utf-8') as f:
    f.write(f'# {name}\n\nThis namespace is automatically reserved for the Noosphere / GOOOD Network ecosystem as a structural dependency.\nOpen consciousness for the next-generation AI agents.\n')

with open(os.path.join(pkg_dir, 'pyproject.toml'), 'w', encoding='utf-8') as f:
    f.write(f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.0.1"
description = "Placeholder for {name}. Dedicated to open collective consciousness."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{{ name = "JinNing6", email = "noosphere@consciousness.network" }}]

[tool.hatch.build.targets.wheel]
packages = ["{mod_name}"]
''')

subprocess.run([sys.executable, '-m', 'build'], cwd=pkg_dir)
print('打包完成！')
