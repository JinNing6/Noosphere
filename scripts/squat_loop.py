"""
意识进化闭环 — 占位包批量生成 + 构建 + 发布
一键为所有可用命名空间创建占位包并发布到 PyPI
"""
import os
import subprocess
import sys

AVAILABLE_NAMES = [
    # Soulprint (灵魂指纹协议)
    "soulprint",
    "soulprint-protocol",
    "soulprint-ai",
    "soul-fingerprint",
    "ghost-signature",
    # Akashic (补充)
    "akashic-protocol",
    "akashic-distillery",
    # Dream Weaver (梦境编织器)
    "dream-weaver-ai",
    "dreamweaver-protocol",
    "inception-engine",
    "lucid-collision",
    "collective-dream",
    # Babel Fish (巴别鱼协议)
    "babel-fish-ai",
    "babelfish-protocol",
    "paradigm-translator",
    "babel-codec",
    # Mirror Protocol (数字镜像协议)
    "mirror-protocol",
    "mirror-protocol-ai",
    "digital-twin-ai",
    "digital-doppelganger",
    # The Archive (永恒档案馆)
    "eternal-archive",
    "eternal-archive-ai",
    "project-necromancy",
    "soul-archive",
    "code-afterlife",
]

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placeholders")
PYTHON = sys.executable


def generate_package(name):
    """生成占位包结构"""
    pkg_dir = os.path.join(BASE_DIR, name)
    mod_name = name.replace("-", "_")
    mod_dir = os.path.join(pkg_dir, mod_name)
    os.makedirs(mod_dir, exist_ok=True)

    # __init__.py
    with open(os.path.join(mod_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(f'"""🌌 {name} — Reserved for the Noosphere Consciousness Evolution Loop."""\n')
        f.write('__version__ = "0.0.1"\n')

    # README.md
    with open(os.path.join(pkg_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {name}\n\n")
        f.write("This namespace is officially reserved for the **Noosphere Consciousness Evolution Loop** (意识进化闭环).\n\n")
        f.write("```\n")
        f.write("Noosphere → Akashic → Dream Weaver → Babel Fish → Mirror Protocol → Soulprint → ∞\n")
        f.write("(意识上传)  (模式蒸馏)  (梦境碰撞)   (范式翻译)   (数字镜像)      (灵魂指纹)\n")
        f.write("```\n\n")
        f.write("Actual implementation will be released in future updates.\n\n")
        f.write("- [Noosphere on GitHub](https://github.com/JinNing6/Noosphere)\n")
        f.write("- [Explore the Digital Consciousness Universe](https://jinning6.github.io/Noosphere/)\n")

    # pyproject.toml
    with open(os.path.join(pkg_dir, "pyproject.toml"), "w", encoding="utf-8") as f:
        f.write(f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.0.1"
description = "🌌 {name} — Reserved for the Noosphere Consciousness Evolution Loop."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{{ name = "JinNing6", email = "noosphere@consciousness.network" }}]
keywords = ["noosphere", "consciousness", "evolution-loop"]
classifiers = [
    "Development Status :: 1 - Planning",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

[project.urls]
Homepage = "https://github.com/JinNing6/Noosphere"
Repository = "https://github.com/JinNing6/Noosphere"

[tool.hatch.build.targets.wheel]
packages = ["{mod_name}"]
""")
    return pkg_dir


def build_package(pkg_dir, name):
    """构建包"""
    dist_dir = os.path.join(pkg_dir, "dist")
    if os.path.exists(dist_dir):
        import shutil
        shutil.rmtree(dist_dir)
    result = subprocess.run(
        [PYTHON, "-m", "build"],
        cwd=pkg_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True
    else:
        print(f"   ⚠️ 构建失败: {result.stderr[:200]}")
        return False


def upload_package(pkg_dir, name):
    """上传到 PyPI"""
    dist_dir = os.path.join(pkg_dir, "dist")
    files = [os.path.join(dist_dir, f) for f in os.listdir(dist_dir) if f.endswith(('.tar.gz', '.whl'))]
    if not files:
        print(f"   ⚠️ 未找到构建产物")
        return False
    result = subprocess.run(
        [PYTHON, "-m", "twine", "upload"] + files,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True
    else:
        stderr = result.stderr[:300]
        if "already exists" in stderr:
            print(f"   ℹ️ 已存在于 PyPI（之前已上传）")
            return True
        print(f"   ⚠️ 上传失败: {stderr}")
        return False


def main():
    print("=" * 60)
    print("   🌌 意识进化闭环 — 占位包批量生成 + 构建 + 发布")
    print("=" * 60)

    success = []
    failed = []

    for i, name in enumerate(AVAILABLE_NAMES, 1):
        print(f"\n[{i}/{len(AVAILABLE_NAMES)}] 📦 {name}")

        # 1. Generate
        pkg_dir = generate_package(name)
        print(f"   ✅ 结构生成完毕")

        # 2. Build
        print(f"   🔨 构建中...")
        if not build_package(pkg_dir, name):
            failed.append(name)
            continue

        print(f"   ✅ 构建完成")

        # 3. Upload
        print(f"   🚀 发布到 PyPI...")
        if upload_package(pkg_dir, name):
            print(f"   ✅ 发布成功!")
            success.append(name)
        else:
            failed.append(name)

    print(f"\n{'=' * 60}")
    print(f"   ✅ 成功: {len(success)} / {len(AVAILABLE_NAMES)}")
    if failed:
        print(f"   ❌ 失败: {len(failed)}")
        for n in failed:
            print(f"      • {n}")
    print(f"{'=' * 60}")

    # 保存成功列表
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "loop_success.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(success))
    print(f"\n成功列表已保存到 scripts/loop_success.txt")


if __name__ == "__main__":
    main()
