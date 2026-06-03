"""
Build a public share proof index from GitHub Issues.

The output is a reviewable proof wall for the frontend. It only counts public
http(s) proof URLs submitted through the Share Proof Issue Form; it never infers
downloads, reposts, referrals, retention, rewards, or install counts.

Usage: python scripts/build_share_proof_index.py
Output: frontend/public/share_proofs.json
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
OUTPUT_FILE = REPO_ROOT / "frontend" / "public" / "share_proofs.json"
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "JinNing6/Noosphere")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
SHARE_PROOF_FORM_URL = "https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml"
DISCLAIMER = (
    "No downloads, reposts, referrals, retention, rewards, or install counts are "
    "inferred from share proof URLs."
)
MAX_ISSUES = 300


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def compact_line(value, max_length=180):
    normalized = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max(0, max_length - 3)].rstrip() + "..."


def extract_issue_form_field(body, label):
    pattern = re.compile(
        rf"### {re.escape(label)}\s*\r?\n+([\s\S]*?)(?=\r?\n### |$)",
        re.IGNORECASE,
    )
    match = pattern.search(str(body or ""))
    return match.group(1).strip() if match else ""


def normalize_public_url(value):
    raw = str(value or "").strip().split()[0] if str(value or "").strip() else ""
    if not raw:
        return ""
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return urllib.parse.urlunparse(parsed)


def issue_labels(issue):
    return [
        str(label.get("name", "")).strip()
        for label in issue.get("labels", [])
        if isinstance(label, dict) and label.get("name")
    ]


def is_share_proof_issue(issue):
    if "pull_request" in issue:
        return False
    labels = {label.lower() for label in issue_labels(issue)}
    title = str(issue.get("title", ""))
    body = str(issue.get("body", ""))
    return (
        "share-proof" in labels
        or title.startswith("Share proof:")
        or "### Public share URL" in body
    )


def proof_from_issue(issue):
    share_url = normalize_public_url(
        extract_issue_form_field(issue.get("body", ""), "Public share URL")
    )
    source_memory = compact_line(
        extract_issue_form_field(issue.get("body", ""), "Source Noosphere memory or Issue"),
        120,
    )
    share_context = compact_line(
        extract_issue_form_field(issue.get("body", ""), "Share context"),
        180,
    )
    user = issue.get("user") or {}
    reviewable = bool(share_url)

    return {
        "issue_number": issue.get("number"),
        "title": compact_line(issue.get("title"), 120),
        "issue_url": issue.get("html_url") or "",
        "share_url": share_url,
        "source_memory": source_memory,
        "share_context": share_context,
        "submitted_by": user.get("login") or "unknown",
        "created_at": issue.get("created_at") or "",
        "updated_at": issue.get("updated_at") or "",
        "labels": issue_labels(issue),
        "reviewable": reviewable,
        "proof_score": 1 if reviewable else 0,
        "disclaimer": DISCLAIMER,
    }


def build_share_proof_index(issues):
    proofs = [
        proof_from_issue(issue)
        for issue in issues
        if is_share_proof_issue(issue)
    ]
    proofs.sort(
        key=lambda proof: (
            proof.get("updated_at") or proof.get("created_at") or "",
            proof.get("issue_number") or 0,
        ),
        reverse=True,
    )

    reviewable_count = sum(1 for proof in proofs if proof["reviewable"])
    invalid_count = len(proofs) - reviewable_count
    share_card = "\n".join([
        "Noosphere share proof wall",
        f"{reviewable_count} reviewable public share URLs from {len(proofs)} proof issues",
        f"Submit proof: {SHARE_PROOF_FORM_URL}",
        DISCLAIMER,
    ])

    return {
        "generated_at": utc_now_iso(),
        "source": "GitHub Issues",
        "next_action_url": SHARE_PROOF_FORM_URL,
        "summary": {
            "total_proof_issues": len(proofs),
            "reviewable_public_urls": reviewable_count,
            "missing_or_invalid_urls": invalid_count,
            "proof_score_formula": "1 point per reviewable public http(s) URL",
            "disclaimer": DISCLAIMER,
        },
        "share_card": share_card,
        "proofs": proofs,
    }


def fetch_repository_issues():
    owner_repo = GITHUB_REPO.strip()
    issues = []
    page = 1
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Noosphere-Share-Proof-Builder/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    while len(issues) < MAX_ISSUES:
        params = urllib.parse.urlencode({
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": "100",
            "page": str(page),
        })
        url = f"https://api.github.com/repos/{owner_repo}/issues?{params}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                batch = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"  WARN Could not fetch share proof issues: {exc}")
            break

        if not isinstance(batch, list) or not batch:
            break

        issues.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    return issues[:MAX_ISSUES]


def write_share_proof_index(issues=None):
    if issues is None:
        issues = fetch_repository_issues()

    index = build_share_proof_index(issues)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    summary = index["summary"]
    print(
        "OK Built share proof index: "
        f"{summary['reviewable_public_urls']} reviewable URLs from "
        f"{summary['total_proof_issues']} proof issues"
    )
    print(f"   Missing/invalid URLs: {summary['missing_or_invalid_urls']}")
    print(f"   Output: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    return index


if __name__ == "__main__":
    write_share_proof_index()
