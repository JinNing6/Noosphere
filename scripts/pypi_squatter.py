import os
import json
import urllib.request
import urllib.error
import shutil
import argparse

# 拟抢占名称清单
TARGET_NAMES = [
    # Noosphere/Akashic 核心
    "akashic",
    "akashic-records",
    "akashic-network",
    "akashic-mcp",
    "akasha-mcp",
    "noosphere-network",
    "noosphere-protocol",
    "collective-consciousness",
    
    # 历史核心项目延伸
    "cyber-huatuo",
    "goood-mcp",
    "aice-eval",
    "paopao-agent"
]

def check_pypi_availability(name):
    """检查包名是否在 PyPI 可用"""
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return False, "已被注册"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True, "可用"
        return False, f"API 错误: {e.code}"
    except Exception as e:
        return False, f"访问错误: {str(e)}"

def generate_placeholder_package(name, output_dir="scripts/placeholders"):
    """生成用来占位的空包结构"""
    pkg_dir = os.path.join(output_dir, name)
    os.makedirs(pkg_dir, exist_ok=True)
    
    # 转换为合法的 Python 模块名 (连字符替换为下划线)
    module_name = name.replace("-", "_")
    module_dir = os.path.join(pkg_dir, module_name)
    os.makedirs(module_dir, exist_ok=True)
    
    # 1. 写入 __init__.py
    with open(os.path.join(module_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(f'"""Placeholder for {name}. Reserved by the Noosphere / GOOOD Network."""\n')
        f.write('__version__ = "0.0.1"\n')
        
    # 2. 写入 README.md
    with open(os.path.join(pkg_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {name}\n\n")
        f.write("This namespace is officially reserved for the Noosphere / GOOOD Network ecosystem.\n")
        f.write("Actual implementation will be released in future updates.\n\n")
        f.write("- [Noosphere on GitHub](https://github.com/JinNing6/Noosphere)\n")
        
    # 3. 写入 pyproject.toml
    pyproject_toml = f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.0.1"
description = "Placeholder for {name}. Reserved for the collective consciousness network."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [
    {{ name = "JinNing6", email = "noosphere@consciousness.network" }},
]
keywords = ["noosphere", "placeholder"]
classifiers = [
    "Development Status :: 1 - Planning",
    "Programming Language :: Python :: 3",
]
dependencies = []

[project.urls]
Homepage = "https://github.com/JinNing6/Noosphere"
Repository = "https://github.com/JinNing6/Noosphere"

[tool.hatch.build.targets.wheel]
packages = ["{module_name}"]
"""
    with open(os.path.join(pkg_dir, "pyproject.toml"), "w", encoding="utf-8") as f:
        f.write(pyproject_toml)
        
    print(f"[+] 占位包已生成: {pkg_dir}")

def main():
    print("=== 开始检测 PyPI 包名占位可用性 ===")
    
    available_names = []
    
    for name in TARGET_NAMES:
        is_available, status = check_pypi_availability(name)
        if is_available:
            print(f"✅ {name}: {status}")
            available_names.append(name)
        else:
            print(f"❌ {name}: {status}")
            
    print(f"\n共有 {len(available_names)} 个名称可用。准备生成结构...")
    
    if available_names:
        for name in available_names:
            generate_placeholder_package(name, output_dir="e:/ideaProjects/agent/Noosphere/scripts/placeholders")
        print("\n=== 所有结构生成完毕 ===")
        print("您现在可以进入对应的包目录中...")
        print("然后执行: python -m PIP install hatch build twine")
        print("并在每个包目录内运行: hatch build & twine upload dist/*")
    else:
        print("\n没有可用的名称能够被生成。")

if __name__ == "__main__":
    main()
