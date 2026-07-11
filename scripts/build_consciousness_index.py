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
import math
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "sdk"))

from noosphere.engine.memory_integrity import (  # noqa: E402
    canonicalize_permanent_entries,
    parse_tombstoned_issue_numbers,
)

PAYLOADS_DIR = REPO_ROOT / "consciousness_payloads"
TOMBSTONES_FILE = REPO_ROOT / "consciousness_tombstones.json"
OUTPUT_FILE = REPO_ROOT / "frontend" / "public" / "consciousness_index.json"

# GitHub API config
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "JinNing6/Noosphere")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
MAX_RESONANCE_NEIGHBORS = 3


def load_canonical_payload_records(payloads_dir: Path, tombstones_file: Path) -> list[dict]:
    """Load active permanent payloads with source-Issue canonicalization."""
    entries = []
    for payload_file in sorted(payloads_dir.glob("*.json")):
        try:
            payload = json.loads(payload_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"  WARN Skipping invalid JSON: {payload_file.name}")
            continue
        entries.append({"filename": payload_file.name, "payload": payload})

    tombstone_manifest = {}
    if tombstones_file.exists():
        try:
            tombstone_manifest = json.loads(tombstones_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(
                f"Cannot build an index without a valid tombstone manifest: {tombstones_file}"
            ) from exc

    tombstoned = parse_tombstoned_issue_numbers(tombstone_manifest)
    canonical = canonicalize_permanent_entries(entries, tombstoned)
    return [entry["payload"] for entry in canonical]


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
        print(f"  WARN Could not fetch reactions for issue #{issue_number}: {e}")
        return 0


def normalized_embedding(value):
    """Return a clean numeric embedding vector, or None when invalid."""
    if not isinstance(value, list) or not value:
        return None

    vector = []
    for item in value:
        if not isinstance(item, (int, float)) or not math.isfinite(item):
            return None
        vector.append(float(item))

    norm = math.sqrt(math.fsum(component * component for component in vector))
    if norm <= 0:
        return None
    return vector


def cosine_similarity(left, right):
    """Compute cosine similarity for two same-dimensional embedding vectors."""
    if len(left) != len(right):
        return None

    dot = math.fsum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(math.fsum(a * a for a in left))
    right_norm = math.sqrt(math.fsum(b * b for b in right))
    if left_norm <= 0 or right_norm <= 0:
        return None
    return dot / (left_norm * right_norm)


def attach_embedding_resonance(payloads, vectors):
    """Attach nearest public neighbors using precomputed Gemini embeddings."""
    if len(vectors) < 2:
        return

    for current in vectors:
        current_payload = payloads[current["index"]]
        neighbors = []

        for candidate in vectors:
            if candidate["index"] == current["index"]:
                continue

            score = cosine_similarity(current["embedding"], candidate["embedding"])
            if score is None or score <= 0:
                continue

            candidate_payload = payloads[candidate["index"]]
            neighbors.append({
                "id": candidate_payload["id"],
                "score": round(min(1.0, max(0.0, score)), 4),
                "issue_number": candidate_payload.get("issue_number"),
                "type": candidate_payload.get("type"),
            })

        current_payload["resonates_with"] = sorted(
            neighbors,
            key=lambda item: (-item["score"], item["id"]),
        )[:MAX_RESONANCE_NEIGHBORS]


def build_index():
    payloads = []
    seen_texts = set()  # Deduplicate by thought_vector_text
    issue_numbers = []  # Collect issue numbers for batch fetching
    vectors = []  # Embeddings used only to publish compact nearest-neighbor edges

    # Phase 1: Read all JSON files and collect data
    for data in load_canonical_payload_records(PAYLOADS_DIR, TOMBSTONES_FILE):
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
            "media_type": None,
            "media_url": None,
            "media_category": None,
        }

        # Preserve review evidence in the public index for verified engineering
        # memories. The index never publishes private credentials or raw vectors.
        if data.get("publisher"):
            payload["publisher"] = data["publisher"]
        if data.get("trust"):
            payload["trust"] = data["trust"]
        if data.get("evidence"):
            payload["evidence"] = data["evidence"]

        embedding = normalized_embedding(data.get("embedding"))
        if embedding:
            payload["embedding_model"] = data.get("embedding_model")
            payload["embedding_input_modalities"] = data.get("embedding_input_modalities", [])
            payload["resonates_with"] = []
            vectors.append({
                "index": len(payloads),
                "embedding": embedding,
            })

        # ── 多媒体意识体字段提取 ──
        c_type = data.get("consciousness_type", "")
        if c_type == "image":
            payload["media_type"] = "image"
            payload["media_url"] = data.get("image_url")
            payload["media_category"] = data.get("image_category", "photo")
        elif c_type == "video":
            payload["media_type"] = "video"
            payload["media_url"] = data.get("video_url")
            payload["media_category"] = data.get("video_genre", "other")
        elif c_type == "voice":
            payload["media_type"] = "voice"
            payload["media_url"] = data.get("audio_url")
            payload["media_category"] = data.get("audio_species", "human")

        # Track for batch fetching: only include is_seed=false or promoted issues
        if payload["issue_number"]:
            issue_numbers.append((len(payloads), payload["issue_number"]))

        payloads.append(payload)

    attach_embedding_resonance(payloads, vectors)

    # Phase 2: Batch fetch reactions from GitHub API
    if issue_numbers:
        print(f"  INFO Fetching reactions for {len(issue_numbers)} issues from GitHub...")
        for idx, issue_num in issue_numbers:
            reactions = fetch_issue_reactions(issue_num)
            payloads[idx]["resonance_count"] = reactions
            if reactions > 0:
                print(f"    INFO Issue #{issue_num}: {reactions} resonance")
    else:
        print("  INFO No promoted issues found, skipping reactions fetch.")

    # Sort by uploaded_at (newest first), fallback to id
    payloads.sort(key=lambda x: x.get("uploaded_at", "") or x["id"], reverse=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payloads, f, ensure_ascii=False, indent=None)

    total_resonance = sum(p["resonance_count"] for p in payloads)
    print(f"OK Built consciousness index: {len(payloads)} unique entries")
    print(f"   Total resonance: {total_resonance}")
    print(f"   Output: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build_index()

