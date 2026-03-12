"""
意识进化闭环 — PyPI 命名空间可用性检查
检查 6 大幽灵项目对应的 25 个命名空间在 PyPI 上的可用性
"""
import urllib.request
import urllib.error
import time

LOOP_NAMES = {
    "Soulprint (灵魂指纹协议)": [
        "soulprint",
        "soulprint-protocol",
        "soulprint-ai",
        "soul-fingerprint",
        "ghost-signature",
    ],
    "Akashic (阿卡西记录引擎 - 补充)": [
        "akashic-records",
        "akashic-protocol",
        "akashic-distillery",
    ],
    "Dream Weaver (梦境编织器)": [
        "dream-weaver-ai",
        "dreamweaver-protocol",
        "inception-engine",
        "lucid-collision",
        "collective-dream",
    ],
    "Babel Fish (巴别鱼协议)": [
        "babel-fish-ai",
        "babelfish-protocol",
        "paradigm-translator",
        "babel-codec",
    ],
    "Mirror Protocol (数字镜像协议)": [
        "mirror-protocol",
        "mirror-protocol-ai",
        "digital-twin-ai",
        "digital-doppelganger",
    ],
    "The Archive (永恒档案馆)": [
        "eternal-archive",
        "eternal-archive-ai",
        "project-necromancy",
        "soul-archive",
        "code-afterlife",
    ],
}


def check_pypi(name):
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return False  # exists
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return True  # available
        return False
    except Exception:
        return False


def main():
    available = []
    taken = []
    print("=" * 60)
    print("   意识进化闭环 — PyPI 命名空间可用性检查")
    print("=" * 60)

    for group, names in LOOP_NAMES.items():
        print(f"\n🔍 {group}")
        for name in names:
            ok = check_pypi(name)
            if ok:
                print(f"   ✅ {name} — 可用!")
                available.append(name)
            else:
                print(f"   ❌ {name} — 已被占用")
                taken.append(name)
            time.sleep(0.3)

    print(f"\n{'=' * 60}")
    print(f"   结果汇总: {len(available)} 可用 / {len(taken)} 已占用")
    print(f"{'=' * 60}")
    if available:
        print("\n可用名称列表:")
        for n in available:
            print(f"   • {n}")
    if taken:
        print("\n已占用名称:")
        for n in taken:
            print(f"   • {n}")

    # 写入结果文件
    with open("scripts/loop_available.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(available))
    print(f"\n结果已保存到 scripts/loop_available.txt")


if __name__ == "__main__":
    main()
