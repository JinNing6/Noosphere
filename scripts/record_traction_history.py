"""
Append the current public traction snapshot to the reviewable history ledger.

This script is intentionally separate from the Pages deploy build. Recording is
manual and append-only so velocity reports compare against prior real snapshots
instead of static vanity counters.

Usage: python scripts/record_traction_history.py
Input: frontend/public/traction_proof.json
Output: frontend/public/traction_history.json
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
TRACTION_PROOF_FILE = REPO_ROOT / "frontend" / "public" / "traction_proof.json"
HISTORY_FILE = REPO_ROOT / "frontend" / "public" / "traction_history.json"

NOOSPHERE_HOME_URL = "https://jinning6.github.io/Noosphere/"
HISTORY_URL = "https://jinning6.github.io/Noosphere/traction_history.json"
RECORD_WORKFLOW_URL = "https://github.com/JinNing6/Noosphere/actions/workflows/record-traction-history.yml"
NON_FABRICATION_DISCLOSURE = (
    "No downloads, reposts, referrals, retention, rewards, or install counts are "
    "inferred from public repository, IssueOps, Pull Request, URL, or history snapshots."
)
RECORDING_POLICY = (
    "Manual append-only history. Each row is a reviewable public traction_proof.json "
    "snapshot; velocity is computed only from prior recorded snapshots."
)


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def number(value, fallback=0):
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)) and math.isfinite(value):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def read_nested(source, *path, fallback=0):
    current = source if isinstance(source, dict) else {}
    for key in path:
        if not isinstance(current, dict):
            return fallback
        current = current.get(key)
    return current if current is not None else fallback


def normalize_snapshot(snapshot):
    if not isinstance(snapshot, dict):
        return None

    generated_at = str(snapshot.get("generated_at") or "").strip()
    if not generated_at:
        return None

    return {
        "generated_at": generated_at,
        "repo": {
            "stars": number(read_nested(snapshot, "repo", "stars")),
            "forks": number(read_nested(snapshot, "repo", "forks")),
            "open_issues": number(read_nested(snapshot, "repo", "open_issues")),
        },
        "memory": {
            "public_memories": number(read_nested(snapshot, "memory", "public_memories")),
            "media_memories": number(read_nested(snapshot, "memory", "media_memories")),
            "embedding_neighbor_edges": number(read_nested(snapshot, "memory", "embedding_neighbor_edges")),
        },
        "share_proof": {
            "total_proof_issues": number(read_nested(snapshot, "share_proof", "total_proof_issues")),
            "reviewable_public_urls": number(read_nested(snapshot, "share_proof", "reviewable_public_urls")),
        },
        "target_progress": {
            "real_contributor_identities": number(
                read_nested(snapshot, "target_progress", "real_contributor_identities")
            ),
            "target_contributor_count": number(
                read_nested(snapshot, "target_progress", "target_contributor_count"),
                fallback=10,
            ),
        },
    }


def parse_timestamp(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def delta(current, baseline, *path):
    return number(read_nested(current, *path)) - number(read_nested(baseline, *path))


def build_velocity(baseline, current):
    if not baseline or not current or baseline.get("generated_at") == current.get("generated_at"):
        current_at = current.get("generated_at", "") if isinstance(current, dict) else ""
        return {
            "status": "baseline-only",
            "baseline_generated_at": current_at,
            "current_generated_at": current_at,
            "days_elapsed": 0,
            "deltas": {
                "stars": 0,
                "forks": 0,
                "open_issues": 0,
                "public_memories": 0,
                "reviewable_public_urls": 0,
                "real_contributor_identities": 0,
            },
            "per_day": {
                "stars": 0,
                "reviewable_public_urls": 0,
                "real_contributor_identities": 0,
            },
        }

    baseline_time = parse_timestamp(baseline["generated_at"])
    current_time = parse_timestamp(current["generated_at"])
    days_elapsed = 0
    if baseline_time and current_time:
        seconds = max(0, (current_time - baseline_time).total_seconds())
        days_elapsed = round(seconds / 86400, 4)

    deltas = {
        "stars": delta(current, baseline, "repo", "stars"),
        "forks": delta(current, baseline, "repo", "forks"),
        "open_issues": delta(current, baseline, "repo", "open_issues"),
        "public_memories": delta(current, baseline, "memory", "public_memories"),
        "reviewable_public_urls": delta(current, baseline, "share_proof", "reviewable_public_urls"),
        "real_contributor_identities": delta(
            current,
            baseline,
            "target_progress",
            "real_contributor_identities",
        ),
    }
    divisor = days_elapsed if days_elapsed > 0 else 1

    return {
        "status": "delta",
        "baseline_generated_at": baseline["generated_at"],
        "current_generated_at": current["generated_at"],
        "days_elapsed": days_elapsed,
        "deltas": deltas,
        "per_day": {
            "stars": round(deltas["stars"] / divisor, 4),
            "reviewable_public_urls": round(deltas["reviewable_public_urls"] / divisor, 4),
            "real_contributor_identities": round(deltas["real_contributor_identities"] / divisor, 4),
        },
    }


def build_share_card(history):
    velocity = history["latest_velocity"]
    deltas = velocity["deltas"]
    return "\n".join([
        "Noosphere traction history",
        (
            f"{history['snapshots_recorded']} recorded real snapshots - "
            f"mode: {history['recording_mode']}"
        ),
        (
            "Velocity: "
            f"{deltas['stars']:+d} stars, "
            f"{deltas['reviewable_public_urls']:+d} proof URLs, "
            f"{deltas['real_contributor_identities']:+d} real contributors"
        ),
        f"History: {HISTORY_URL}",
        f"Open graph: {NOOSPHERE_HOME_URL}",
        NON_FABRICATION_DISCLOSURE,
    ])


def build_traction_history(existing_history, current_snapshot):
    existing_history = existing_history if isinstance(existing_history, dict) else {}
    normalized_current = normalize_snapshot(current_snapshot)
    if not normalized_current:
        raise ValueError("current traction snapshot is missing generated_at")

    snapshots = []
    seen = set()
    for raw_snapshot in existing_history.get("snapshots", []):
        normalized = normalize_snapshot(raw_snapshot)
        if not normalized:
            continue
        key = normalized["generated_at"]
        if key in seen:
            continue
        snapshots.append(normalized)
        seen.add(key)

    if normalized_current["generated_at"] not in seen:
        snapshots.append(normalized_current)
        seen.add(normalized_current["generated_at"])

    if len(snapshots) >= 2:
        latest_velocity = build_velocity(snapshots[-2], snapshots[-1])
    else:
        latest_velocity = build_velocity(None, snapshots[-1])

    history = {
        "generated_at": utc_now_iso(),
        "source": "Manual append-only records of generated Noosphere traction_proof.json snapshots",
        "recording_mode": "manual append-only",
        "recording_policy": RECORDING_POLICY,
        "history_url": HISTORY_URL,
        "record_workflow_url": RECORD_WORKFLOW_URL,
        "snapshots_recorded": len(snapshots),
        "latest_velocity": latest_velocity,
        "snapshots": snapshots,
        "disclaimer": NON_FABRICATION_DISCLOSURE,
    }
    history["share_card"] = build_share_card(history)
    return history


def read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return fallback


def write_traction_history():
    current_snapshot = read_json(TRACTION_PROOF_FILE, {})
    existing_history = read_json(HISTORY_FILE, {"snapshots": []})
    history = build_traction_history(existing_history, current_snapshot)
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    velocity = history["latest_velocity"]
    deltas = velocity["deltas"]
    print(
        "OK Recorded traction history: "
        f"{history['snapshots_recorded']} snapshots, "
        f"{deltas['stars']:+d} stars, "
        f"{deltas['reviewable_public_urls']:+d} proof URLs, "
        f"{deltas['real_contributor_identities']:+d} contributors"
    )
    print(f"   Output: {HISTORY_FILE}")
    print(f"   Size: {HISTORY_FILE.stat().st_size / 1024:.1f} KB")
    return history


if __name__ == "__main__":
    write_traction_history()
