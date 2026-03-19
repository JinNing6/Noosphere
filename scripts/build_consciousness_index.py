"""
Build script: Merge all consciousness_payloads/*.json into a single index file
for the frontend to fetch at runtime.

Now enhanced with:
- resonance_count: Real resonance (reactions) from GitHub Issues API
- parent_id: Parent consciousness ID for evolution chains
- issue_number: GitHub Issue number for linking

Usage: python scripts/build_consciousness_index.py
Output: frontend/public/consciousness_index.json
"""
import json
import os
import hashlib
import urllib.request
import urllib.error
from pathlib import Path

PAYLOADS_DIR = Path(__file__).parent.parent / "consciousness_payloads"
OUTPUT_FILE = Path(__file__).parent.parent / "frontend" / "public" / "consciousness_index.json"

# GitHub API config
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "JinNing6/Noosphere")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def fetch_issue_reactions(issue_number: int) -> int:
    """Fetch reactions count for a specific GitHub Issue."""
    if not issue_number or issue_number <= 0:
        return 0

    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{issue_number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Noosphere-Builder/1.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("reactions", {}).get("total_count", 0)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  ⚠️ Could not fetch reactions for issue #{issue_number}: {e}")
        return 0


def build_index():
    payloads = []
    seen_texts = set()  # Deduplicate by thought_vector_text
    issue_numbers = []  # Collect issue numbers for batch fetching

    # Phase 1: Read all JSON files and collect data
    for f in sorted(PAYLOADS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"  ⚠️ Skipping invalid JSON: {f.name}")
            continue

        text = data.get("thought_vector_text", "")
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)

        # Generate stable ID from content hash
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        issue_num = data.get("promoted_from_issue", 0)

        payload = {
            "id": f"soul-{content_hash}",
            "creator": data.get("creator_signature", "匿名意识"),
            "type": data.get("consciousness_type", "epiphany"),
            "text": text,
            "context": data.get("context_environment", ""),
            "tags": data.get("tags", []),
            "uploaded_at": data.get("uploaded_at", ""),
            "anonymous": data.get("is_anonymous", False),
            "issue_number": issue_num if isinstance(issue_num, int) and issue_num > 0 else None,
            "parent_id": data.get("parent_id", None),
            "resonance_count": 0,  # Will be filled in Phase 2
        }

        # Track for batch fetching: only include is_seed=false or promoted issues
        if payload["issue_number"]:
            issue_numbers.append((len(payloads), payload["issue_number"]))

        payloads.append(payload)

    # Phase 2: Batch fetch reactions from GitHub API
    if issue_numbers:
        print(f"  🔄 Fetching reactions for {len(issue_numbers)} issues from GitHub...")
        for idx, issue_num in issue_numbers:
            reactions = fetch_issue_reactions(issue_num)
            payloads[idx]["resonance_count"] = reactions
            if reactions > 0:
                print(f"    💖 Issue #{issue_num}: {reactions} resonance")
    else:
        print("  ℹ️ No promoted issues found, skipping reactions fetch.")

    # Sort by uploaded_at (newest first), fallback to id
    payloads.sort(key=lambda x: x.get("uploaded_at", "") or x["id"], reverse=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payloads, f, ensure_ascii=False, indent=None)

    total_resonance = sum(p["resonance_count"] for p in payloads)
    print(f"✅ Built consciousness index: {len(payloads)} unique entries")
    print(f"   💖 Total resonance: {total_resonance}")
    print(f"   Output: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build_index()

