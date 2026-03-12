import urllib.request
import os
import subprocess
import sys

names = [
    'black-mirror',
    'blackmirror',
    'black-mirror-ai',
    'blackmirror-ai',
    'black-mirror-mcp',
    'cyber-mirror',
]

available = []
print('=== Black Mirror Series Check ===')
for name in names:
    try:
        req = urllib.request.Request(f'https://pypi.org/pypi/{name}/json', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            print(f'X {name} - taken')
    except Exception as e:
        print(f'OK {name} - available!')
        available.append(name)

if not available:
    print('None available.')
    sys.exit(0)

print(f'\n=== Building {len(available)} packages ===')
for name in available:
    pkg_dir = os.path.abspath(os.path.join('scripts/placeholders', name))
    mod_name = name.replace('-', '_')
    mod_dir = os.path.join(pkg_dir, mod_name)
    os.makedirs(mod_dir, exist_ok=True)

    with open(os.path.join(mod_dir, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write('__version__ = "0.0.1"\n')

    with open(os.path.join(pkg_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {name}\n\nReserved for the Noosphere / GOOOD Network ecosystem.\n')

    with open(os.path.join(pkg_dir, 'pyproject.toml'), 'w', encoding='utf-8') as f:
        f.write(f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.0.1"
description = "Placeholder for {name}. The mirror that reflects digital consciousness."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{{ name = "JinNing6", email = "noosphere@consciousness.network" }}]

[tool.hatch.build.targets.wheel]
packages = ["{mod_name}"]
''')
    print(f'Building {name}...')
    subprocess.run([sys.executable, '-m', 'build'], cwd=pkg_dir)

with open('scripts/mirror_available.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(available))

print('\nDone!')
