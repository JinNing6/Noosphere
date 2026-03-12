"""
批量上传所有已构建的闭环占位包到 PyPI (逐个执行 twine, 不捕获输出)
"""
import os
import subprocess
import sys
import glob

PYTHON = sys.executable
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placeholders")

NAMES = [
    "soulprint-protocol",
    "soulprint-ai",
    "soul-fingerprint",
    "ghost-signature",
    "akashic-protocol",
    "akashic-distillery",
    "dream-weaver-ai",
    "dreamweaver-protocol",
    "inception-engine",
    "lucid-collision",
    "collective-dream",
    "babel-fish-ai",
    "babelfish-protocol",
    "paradigm-translator",
    "babel-codec",
    "mirror-protocol",
    "mirror-protocol-ai",
    "digital-twin-ai",
    "digital-doppelganger",
    "eternal-archive",
    "eternal-archive-ai",
    "project-necromancy",
    "soul-archive",
    "code-afterlife",
]

success = []
failed = []

for i, name in enumerate(NAMES, 1):
    dist_dir = os.path.join(BASE, name, "dist")
    if not os.path.exists(dist_dir):
        print(f"[{i}/{len(NAMES)}] SKIP {name} - no dist/")
        failed.append(name)
        continue

    files = glob.glob(os.path.join(dist_dir, "*"))
    if not files:
        print(f"[{i}/{len(NAMES)}] SKIP {name} - dist/ empty")
        failed.append(name)
        continue

    print(f"[{i}/{len(NAMES)}] Uploading {name}...")
    result = subprocess.run(
        [PYTHON, "-m", "twine", "upload", "--skip-existing"] + files,
        timeout=60,
    )
    if result.returncode == 0:
        print(f"  OK {name}")
        success.append(name)
    else:
        print(f"  FAIL {name}")
        failed.append(name)

print(f"\nDone: {len(success)} OK, {len(failed)} FAIL")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "loop_success.txt"), "w") as f:
    f.write("\n".join(["soulprint"] + success))
