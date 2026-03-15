"""
Build script: Merge all consciousness_payloads/*.json into a single index file
for the frontend to fetch at runtime.

Usage: python scripts/build_consciousness_index.py
Output: frontend/public/consciousness_index.json
"""
import json
import os
import hashlib
from pathlib import Path

PAYLOADS_DIR = Path(__file__).parent.parent / "consciousness_payloads"
OUTPUT_FILE = Path(__file__).parent.parent / "frontend" / "public" / "consciousness_index.json"


def build_index():
    payloads = []
    seen_texts = set()  # Deduplicate by thought_vector_text

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
        
        payloads.append({
            "id": f"soul-{content_hash}",
            "creator": data.get("creator_signature", "匿名意识"),
            "type": data.get("consciousness_type", "epiphany"),
            "text": text,
            "context": data.get("context_environment", ""),
            "tags": data.get("tags", []),
            "uploaded_at": data.get("uploaded_at", ""),
            "anonymous": data.get("is_anonymous", False),
        })

    # Sort by uploaded_at (newest first), fallback to id
    payloads.sort(key=lambda x: x.get("uploaded_at", "") or x["id"], reverse=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payloads, f, ensure_ascii=False, indent=None)

    print(f"✅ Built consciousness index: {len(payloads)} unique entries")
    print(f"   Output: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    build_index()
