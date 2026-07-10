"""
Build a public traction proof snapshot from real public sources.

The snapshot combines:
- GitHub repository metadata from the official REST API
- GitHub IssueOps and Pull Request authors from the official REST API
- Noosphere's generated public memory and share-proof JSON files

It never infers downloads, reposts, referrals, retention, rewards, install
counts, private analytics, or active users.

Usage: python scripts/build_traction_proof.py
Output: frontend/public/traction_proof.json
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from record_traction_history import (  # noqa: E402
    HISTORY_URL,
    RECORDING_POLICY,
    RECORD_WORKFLOW_URL,
    build_velocity,
    normalize_snapshot,
)

CONSCIOUSNESS_INDEX_FILE = REPO_ROOT / "frontend" / "public" / "consciousness_index.json"
SHARE_PROOF_FILE = REPO_ROOT / "frontend" / "public" / "share_proofs.json"
HISTORY_FILE = REPO_ROOT / "frontend" / "public" / "traction_history.json"
OUTPUT_FILE = REPO_ROOT / "frontend" / "public" / "traction_proof.json"
SDK_PYPROJECT_FILE = REPO_ROOT / "sdk" / "pyproject.toml"
PUBLISH_WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "publish-pypi.yml"

GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "JinNing6/Noosphere")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API_VERSION = "2022-11-28"
MAX_ISSUES = 300
MAX_PULLS = 100
DEFAULT_TARGET_CONTRIBUTORS = 10
PYPI_PROJECT = "noosphere-mcp"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PYPI_PROJECT}/json"

NOOSPHERE_HOME_URL = "https://jinning6.github.io/Noosphere/"
REPO_URL = "https://github.com/JinNing6/Noosphere"
UPLOAD_FORM_URL = "https://github.com/JinNing6/Noosphere/issues/new?template=consciousness-upload.yml"
SHARE_PROOF_FORM_URL = "https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml"
TRACTION_PROOF_URL = "https://jinning6.github.io/Noosphere/traction_proof.json"
GROWTH_PROOF_TEMPLATE = "growth-proof.yml"
SHARE_PROOF_TEMPLATE = "share-proof.yml"
CREATED_GROWTH_ISSUE_URL_PLACEHOLDER = (
    "https://github.com/JinNing6/Noosphere/issues/<created-growth-issue-number>"
)
CREATED_SHARE_PROOF_ISSUE_URL_PLACEHOLDER = (
    "https://github.com/JinNing6/Noosphere/issues/<created-share-proof-issue-number>"
)
PUBLIC_POST_URL_PLACEHOLDER = "<public-post-url>"
NON_FABRICATION_DISCLOSURE = (
    "No downloads, reposts, referrals, retention, rewards, or install counts are "
    "inferred from public repository, IssueOps, Pull Request, or URL snapshots."
)


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def github_headers(user_agent):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": user_agent,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_json(url, user_agent):
    request = urllib.request.Request(url, headers=github_headers(user_agent))
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8")), None
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, str(exc)


def fetch_public_json(url, user_agent):
    request = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": user_agent,
    })
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8")), None
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, str(exc)


def fetch_repository():
    url = f"https://api.github.com/repos/{GITHUB_REPO.strip()}"
    data, error = fetch_json(url, "Noosphere-Traction-Proof-Builder/1.0")
    if not isinstance(data, dict):
        return None, f"GitHub repository fetch failed: {error or 'unexpected response'}"
    return data, None


def fetch_repository_issues():
    issues = []
    page = 1
    while len(issues) < MAX_ISSUES:
        params = urllib.parse.urlencode({
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": "100",
            "page": str(page),
        })
        url = f"https://api.github.com/repos/{GITHUB_REPO.strip()}/issues?{params}"
        batch, error = fetch_json(url, "Noosphere-Traction-Proof-Builder/1.0")
        if not isinstance(batch, list):
            return issues[:MAX_ISSUES], f"GitHub issues fetch failed: {error or 'unexpected response'}"
        if not batch:
            break
        issues.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return issues[:MAX_ISSUES], None


def fetch_repository_pulls():
    pulls = []
    page = 1
    while len(pulls) < MAX_PULLS:
        params = urllib.parse.urlencode({
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": "100",
            "page": str(page),
        })
        url = f"https://api.github.com/repos/{GITHUB_REPO.strip()}/pulls?{params}"
        batch, error = fetch_json(url, "Noosphere-Traction-Proof-Builder/1.0")
        if not isinstance(batch, list):
            return pulls[:MAX_PULLS], f"GitHub pull requests fetch failed: {error or 'unexpected response'}"
        if not batch:
            break
        pulls.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return pulls[:MAX_PULLS], None


def fetch_pypi_project():
    data, error = fetch_public_json(PYPI_JSON_URL, "Noosphere-Traction-Proof-Builder/1.0")
    if not isinstance(data, dict):
        return None, f"PyPI JSON fetch failed: {error or 'unexpected response'}"
    return data, None


def fetch_github_release(tag_name):
    encoded_tag = urllib.parse.quote(str(tag_name or "").strip(), safe="")
    url = f"https://api.github.com/repos/{GITHUB_REPO.strip()}/releases/tags/{encoded_tag}"
    data, error = fetch_json(url, "Noosphere-Traction-Proof-Builder/1.0")
    if not isinstance(data, dict):
        return None, f"GitHub Release fetch failed for {tag_name}: {error or 'unexpected response'}"
    return data, None


def read_local_package_version(access_issues):
    try:
        text = SDK_PYPROJECT_FILE.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        access_issues.append(f"Local package metadata read failed: {exc}")
        return ""
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        access_issues.append("Local package metadata read failed: sdk/pyproject.toml has no project version")
        return ""
    return match.group(1)


def publish_workflow_supports_tag_push(workflow_text):
    return (
        "push:" in workflow_text
        and "tags:" in workflow_text
        and re.search(r"""['"]?v\*['"]?""", workflow_text) is not None
    )


def read_publish_workflow_supports_tag_push(access_issues):
    try:
        workflow_text = PUBLISH_WORKFLOW_FILE.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        access_issues.append(f"Publish workflow read failed: {exc}")
        return False
    return publish_workflow_supports_tag_push(workflow_text)


def read_json_file(path, fallback, access_issues, label):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        access_issues.append(f"{label} read failed: {exc}")
        return fallback


def read_optional_json_file(path, fallback, access_issues, label):
    if not path.exists():
        return fallback
    return read_json_file(path, fallback, access_issues, label)


def build_issue_form_url(template, title=None, fields=None):
    params = [("template", template)]
    if title:
        params.append(("title", title))
    for key, value in (fields or {}).items():
        rendered = str(value or "").strip()
        if rendered:
            params.append((key, rendered))
    return f"{REPO_URL}/issues/new?{urllib.parse.urlencode(params)}"


def issue_labels(issue):
    labels = []
    for label in issue.get("labels", []):
        if isinstance(label, dict) and label.get("name"):
            labels.append(str(label["name"]).strip())
    return labels


def is_pull_request_issue(issue):
    return "pull_request" in issue


def is_share_proof_issue(issue):
    labels = {label.lower() for label in issue_labels(issue)}
    title = str(issue.get("title", ""))
    body = str(issue.get("body", ""))
    return (
        not is_pull_request_issue(issue)
        and (
            "share-proof" in labels
            or title.startswith("Share proof:")
            or "### Public share URL" in body
        )
    )


def is_consciousness_issue(issue):
    labels = {label.lower() for label in issue_labels(issue)}
    title = str(issue.get("title", ""))
    body = str(issue.get("body", ""))
    return (
        not is_pull_request_issue(issue)
        and (
            "consciousness" in labels
            or "consciousness-upload" in labels
            or "Consciousness Payload" in title
            or "CONSCIOUSNESS_PAYLOAD_START" in body
            or "## Consciousness Payload" in body
        )
    )


def actor_login(value):
    user = value.get("user") if isinstance(value, dict) else None
    if isinstance(user, dict):
        login = str(user.get("login") or "").strip()
        return login
    return ""


def normalize_positive_int(value, fallback):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed > 0 else fallback


def summarize_memories(memories):
    if not isinstance(memories, list):
        memories = []

    embedding_neighbor_edges = 0
    resonance_events = 0
    promoted_issue_memories = 0
    media_memories = 0

    for memory in memories:
        if not isinstance(memory, dict):
            continue
        neighbors = memory.get("resonates_with")
        if isinstance(neighbors, list):
            embedding_neighbor_edges += len(neighbors)
        if isinstance(memory.get("resonance_count"), (int, float)):
            resonance_events += int(memory["resonance_count"])
        if isinstance(memory.get("issue_number"), int) and memory["issue_number"] > 0:
            promoted_issue_memories += 1
        if memory.get("media_type"):
            media_memories += 1

    return {
        "public_memories": len([item for item in memories if isinstance(item, dict)]),
        "promoted_issue_memories": promoted_issue_memories,
        "media_memories": media_memories,
        "resonance_events": resonance_events,
        "embedding_neighbor_edges": embedding_neighbor_edges,
    }


def summarize_share_proofs(share_proofs):
    summary = share_proofs.get("summary") if isinstance(share_proofs, dict) else {}
    proofs = share_proofs.get("proofs") if isinstance(share_proofs, dict) else []
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(proofs, list):
        proofs = []

    return {
        "total_proof_issues": int(summary.get("total_proof_issues") or 0),
        "reviewable_public_urls": int(summary.get("reviewable_public_urls") or 0),
        "missing_or_invalid_urls": int(summary.get("missing_or_invalid_urls") or 0),
        "latest_reviewable_url": next(
            (
                str(proof.get("share_url"))
                for proof in proofs
                if isinstance(proof, dict) and proof.get("reviewable") and proof.get("share_url")
            ),
            "",
        ),
    }


def summarize_repo(repo):
    if not isinstance(repo, dict):
        return {
            "status": "unavailable",
            "full_name": GITHUB_REPO,
            "html_url": REPO_URL,
            "stars": 0,
            "forks": 0,
            "open_issues": 0,
        }

    return {
        "status": "ok",
        "full_name": repo.get("full_name") or GITHUB_REPO,
        "html_url": repo.get("html_url") or REPO_URL,
        "stars": int(repo.get("stargazers_count") or 0),
        "forks": int(repo.get("forks_count") or repo.get("forks") or 0),
        "open_issues": int(repo.get("open_issues_count") or 0),
    }


def summarize_issueops(issues):
    public_issues = [issue for issue in issues if isinstance(issue, dict) and not is_pull_request_issue(issue)]
    share_issues = [issue for issue in public_issues if is_share_proof_issue(issue)]
    consciousness_issues = [issue for issue in public_issues if is_consciousness_issue(issue)]

    return {
        "sampled_issues": len(public_issues),
        "share_proof_issues": len(share_issues),
        "open_share_proof_issues": len([issue for issue in share_issues if issue.get("state") == "open"]),
        "consciousness_issues": len(consciousness_issues),
        "open_consciousness_issues": len([issue for issue in consciousness_issues if issue.get("state") == "open"]),
    }


def collect_contributors(issues, pulls, share_proofs):
    contributors = set()

    for issue in issues:
        if not isinstance(issue, dict):
            continue
        if is_share_proof_issue(issue) or is_consciousness_issue(issue):
            login = actor_login(issue)
            if login:
                contributors.add(login)

    for pull in pulls:
        if not isinstance(pull, dict):
            continue
        login = actor_login(pull)
        if login:
            contributors.add(login)

    proofs = share_proofs.get("proofs") if isinstance(share_proofs, dict) else []
    if isinstance(proofs, list):
        for proof in proofs:
            if not isinstance(proof, dict):
                continue
            if not proof.get("reviewable"):
                continue
            login = str(proof.get("submitted_by") or "").strip()
            if login and login != "unknown":
                contributors.add(login)

    return sorted(contributors, key=str.lower)


def build_distribution_readiness(
    local_version,
    pypi_project=None,
    release=None,
    access_errors=None,
    pypi_error=None,
    release_error=None,
    tag_trigger_supported=False,
):
    access_errors = [str(error) for error in (access_errors or []) if error]
    pypi_errors = [str(error) for error in [pypi_error] if error]
    release_errors = [str(error) for error in [release_error] if error]
    release_tag = f"v{local_version}" if local_version else ""
    latest_version = ""
    if isinstance(pypi_project, dict):
        latest_version = str(pypi_project.get("info", {}).get("version") or "").strip()

    if not local_version:
        pypi_status = "local-version-missing"
    elif pypi_errors:
        pypi_status = "unverified"
    elif not latest_version:
        pypi_status = "unverified"
    elif latest_version == local_version:
        pypi_status = "current"
    else:
        pypi_status = "registry-version-mismatch"

    if not local_version:
        release_status = "local-version-missing"
    elif release_errors and any("404" in error for error in release_errors) and not access_errors:
        release_status = "missing"
    elif release_errors or access_errors:
        release_status = "unverified"
    elif not isinstance(release, dict):
        release_status = "missing"
    elif str(release.get("tag_name") or "").strip() != release_tag:
        release_status = "tag-mismatch"
    elif release.get("draft"):
        release_status = "draft"
    elif release.get("prerelease"):
        release_status = "prerelease"
    else:
        release_status = "published"

    publish_trigger = "tag-or-release" if tag_trigger_supported else "release-only"
    publish_trigger_ready = tag_trigger_supported or release_status == "published"
    publish_trigger_status = "available" if publish_trigger_ready else "blocked"
    all_errors = [
        *access_errors,
        *pypi_errors,
        *(release_errors if not publish_trigger_ready else []),
    ]

    registry_url = f"https://pypi.org/project/{PYPI_PROJECT}/"
    release_url = f"{REPO_URL}/releases/tag/{release_tag}" if release_tag else f"{REPO_URL}/releases"
    workflow_url = f"{REPO_URL}/actions/workflows/publish-pypi.yml"
    verifier_command = "python scripts/verify_pypi_release.py --tool-count 45"
    publish_workflow = ".github/workflows/publish-pypi.yml"

    if pypi_status == "current" and publish_trigger_ready:
        status = "ready"
        blocker = ""
        next_action = "Re-run traction proof after the next real public proof action."
    elif pypi_status == "registry-version-mismatch":
        status = "blocked"
        blocker = (
            f"Install-loop launch blocker: PyPI latest {latest_version or 'unknown'} "
            f"does not match local package {local_version}."
        )
        next_action = (
            f"Push release tag {release_tag or '<target-tag>'} or publish a GitHub Release "
            f"so Trusted Publishing can publish {PYPI_PROJECT}=={local_version}, then recheck PyPI JSON."
        )
    elif not publish_trigger_ready:
        status = "blocked"
        blocker = (
            f"Publish-trigger blocker: {publish_workflow} is release-only and GitHub Release "
            f"{release_tag or '<missing-version>'} is {release_status}."
        )
        next_action = (
            f"Publish GitHub Release {release_tag or '<missing-version>'} or add a v* tag trigger "
            "to the Trusted Publishing workflow."
        )
    elif pypi_status == "unverified":
        status = "blocked"
        blocker = "Distribution public API access is unverified; PyPI state could not be proven."
        next_action = "Retry the distribution preflight with PyPI API access, then rerun traction proof."
    else:
        status = "blocked"
        blocker = "Distribution readiness is incomplete."
        next_action = "Close the release, PyPI, and verifier checklist before claiming install readiness."

    checklist = [
        "Run package gates: python -m pytest tests/test_noosphere_mcp.py tests/test_vector_store.py tests/test_preflight.py tests/test_release_boundary.py",
        "Run release verifier tests: python -m unittest scripts.test_verify_pypi_release",
        f"Build artifacts: cd sdk && python -m build",
        f"Push release tag {release_tag or '<target-tag>'} or publish GitHub Release {release_tag or '<target-tag>'} so {publish_workflow} can publish with PyPI Trusted Publishing/OIDC.",
        f"Verify registry latest: {verifier_command}",
        "Rebuild traction proof: python scripts/build_traction_proof.py",
    ]

    return {
        "status": status,
        "package": PYPI_PROJECT,
        "local_version": local_version,
        "registry_latest_version": latest_version,
        "pypi_status": pypi_status,
        "registry_url": registry_url,
        "release_tag": release_tag,
        "release_status": release_status,
        "publish_trigger": publish_trigger,
        "publish_trigger_status": publish_trigger_status,
        "tag_trigger_supported": tag_trigger_supported,
        "release_url": release.get("html_url", release_url) if isinstance(release, dict) else release_url,
        "trusted_publishing_workflow": publish_workflow,
        "trusted_publishing_workflow_url": workflow_url,
        "verifier_command": verifier_command,
        "blocker": blocker,
        "next_action": next_action,
        "closure_checklist": checklist,
        "access_issues": all_errors,
        "disclaimer": "Distribution readiness uses PyPI JSON, GitHub Release APIs, and the Trusted Publishing workflow trigger contract; it does not infer installs or downloads.",
    }


def choose_bottleneck(memory_summary, share_summary, contributor_count, target_count, access_issues, distribution=None):
    if isinstance(distribution, dict) and distribution.get("status") == "blocked":
        return {
            "stage": "install-loop launch blocker",
            "reason": distribution.get("blocker") or "Distribution readiness is incomplete.",
            "next_action": distribution.get("next_action") or "Close the release and registry checklist.",
            "next_action_url": distribution.get("trusted_publishing_workflow_url") or distribution.get("release_url") or f"{REPO_URL}/actions",
        }

    if access_issues:
        return {
            "stage": "public API recovery",
            "reason": "One or more public snapshot sources could not be read.",
            "next_action": "Retry Pages build after checking GitHub API permissions and generated JSON artifacts.",
            "next_action_url": f"{REPO_URL}/actions",
        }

    if memory_summary["public_memories"] <= 0:
        return {
            "stage": "public memory supply",
            "reason": "The live memory graph has no public payloads to share yet.",
            "next_action": "Upload one reusable Agent debugging memory.",
            "next_action_url": UPLOAD_FORM_URL,
        }

    if share_summary["reviewable_public_urls"] < memory_summary["public_memories"]:
        return {
            "stage": "public share proof",
            "reason": (
                "Public memories exist, but reviewable external share URLs still lag behind the memory graph."
            ),
            "next_action": "Share one memory publicly, then record the URL with the Share Proof Issue Form.",
            "next_action_url": SHARE_PROOF_FORM_URL,
        }

    if contributor_count < target_count:
        return {
            "stage": "contributor expansion",
            "reason": "The current sprint still needs more real contributor identities.",
            "next_action": "Publish the traction proof card and invite one Agent user to upload or record proof.",
            "next_action_url": NOOSPHERE_HOME_URL,
        }

    return {
        "stage": "repeat proof velocity",
        "reason": "The target is reached; the next proof gap is repeated public proof over time.",
        "next_action": "Run another proof sprint and compare against the next real snapshot.",
        "next_action_url": NOOSPHERE_HOME_URL,
    }


def build_first_proof_commands():
    return [
        (
            'record_growth_referral('
            f'source_url="{CREATED_GROWTH_ISSUE_URL_PLACEHOLDER}", '
            'campaign="traction-proof")'
        ),
        (
            'record_share_attribution('
            f'share_url="{PUBLIC_POST_URL_PLACEHOLDER}", '
            f'source_url="{CREATED_SHARE_PROOF_ISSUE_URL_PLACEHOLDER}", '
            'artifact="Noosphere traction proof")'
        ),
        "share_attribution_report()",
        "growth_flywheel()",
    ]


def build_first_proof_post(memory_summary, share_summary, target_progress, growth_url, share_url):
    return "\n".join([
        "Noosphere public traction proof",
        (
            f"{memory_summary['public_memories']} public Agent memories, "
            f"{share_summary['reviewable_public_urls']} reviewable public proof URLs, "
            f"{target_progress['real_contributor_identities']}/"
            f"{target_progress['target_contributor_count']} real contributors."
        ),
        f"Live graph: {NOOSPHERE_HOME_URL}",
        f"Proof snapshot: {TRACTION_PROOF_URL}",
        f"History: {HISTORY_URL}",
        f"Upload memory: {UPLOAD_FORM_URL}",
        f"Record growth proof: {growth_url}",
        f"Record share proof: {share_url}",
        NON_FABRICATION_DISCLOSURE,
    ])


def build_first_proof_action(memory_summary, share_summary, target_progress):
    commands = build_first_proof_commands()
    growth_url = build_issue_form_url(
        GROWTH_PROOF_TEMPLATE,
        title="Growth proof: Noosphere traction proof",
        fields={
            "campaign_hook": "First public proof action from the Noosphere traction proof panel.",
            "target_contributors": target_progress["target_contributor_count"],
            "real_data_context": "\n".join([
                f"Public snapshot: {TRACTION_PROOF_URL}",
                f"History: {HISTORY_URL}",
                (
                    f"Current proof gap: {share_summary['reviewable_public_urls']} reviewable public "
                    f"proof URLs for {memory_summary['public_memories']} public memories."
                ),
            ]),
            "next_commands": "\n".join(commands),
        },
    )
    share_url = build_issue_form_url(
        SHARE_PROOF_TEMPLATE,
        title="Share proof: Noosphere traction proof",
        fields={
            "source_memory": TRACTION_PROOF_URL,
            "share_context": (
                "Shared the Noosphere public traction proof and first proof action kit."
            ),
        },
    )
    reason = (
        "No reviewable public share proof URLs have been recorded yet."
        if share_summary["reviewable_public_urls"] <= 0
        else "The proof loop is still behind the public memory graph."
    )

    return {
        "stage": "first public proof",
        "reason": reason,
        "growth_issue_form_url": growth_url,
        "share_proof_form_url": share_url,
        "created_growth_issue_url_placeholder": CREATED_GROWTH_ISSUE_URL_PLACEHOLDER,
        "created_share_proof_issue_url_placeholder": CREATED_SHARE_PROOF_ISSUE_URL_PLACEHOLDER,
        "public_post_url_placeholder": PUBLIC_POST_URL_PLACEHOLDER,
        "commands_after_submission": commands,
        "copy_ready_public_proof_post": build_first_proof_post(
            memory_summary,
            share_summary,
            target_progress,
            growth_url,
            share_url,
        ),
        "disclaimer": NON_FABRICATION_DISCLOSURE,
    }


def build_share_card(
    repo_summary,
    memory_summary,
    share_summary,
    target_progress,
    bottleneck,
    history_summary,
    first_proof_action,
    distribution,
):
    def unit(count, singular, plural):
        return singular if count == 1 else plural

    velocity = history_summary.get("latest_velocity", {})
    deltas = velocity.get("deltas", {})

    return "\n".join([
        "Noosphere public traction proof",
        (
            f"Repo: {repo_summary['stars']} {unit(repo_summary['stars'], 'star', 'stars')}, "
            f"{repo_summary['forks']} {unit(repo_summary['forks'], 'fork', 'forks')}, "
            f"{repo_summary['open_issues']} open {unit(repo_summary['open_issues'], 'issue', 'issues')}"
        ),
        (
            f"Memory graph: {memory_summary['public_memories']} public "
            f"{unit(memory_summary['public_memories'], 'memory', 'memories')}, "
            f"{memory_summary['media_memories']} media "
            f"{unit(memory_summary['media_memories'], 'memory', 'memories')}, "
            f"{memory_summary['embedding_neighbor_edges']} embedding neighbor "
            f"{unit(memory_summary['embedding_neighbor_edges'], 'edge', 'edges')}"
        ),
        (
            f"Share proof: {share_summary['reviewable_public_urls']} reviewable public URLs "
            f"from {share_summary['total_proof_issues']} proof "
            f"{unit(share_summary['total_proof_issues'], 'issue', 'issues')}"
        ),
        (
            f"Sprint: {target_progress['real_contributor_identities']}/"
            f"{target_progress['target_contributor_count']} real contributors"
        ),
        (
            f"Distribution: local {distribution.get('local_version') or 'unknown'}, "
            f"PyPI {distribution.get('registry_latest_version') or 'unknown'}, "
            f"{distribution.get('status', 'not_checked')}"
        ),
        (
            "Velocity: "
            f"{int(deltas.get('stars', 0)):+d} stars, "
            f"{int(deltas.get('reviewable_public_urls', 0)):+d} proof URLs, "
            f"{int(deltas.get('real_contributor_identities', 0)):+d} real contributors"
        ),
        f"History: {history_summary.get('history_url', HISTORY_URL)}",
        f"Bottleneck: {bottleneck['stage']} - {bottleneck['next_action']}",
        f"First proof: {first_proof_action['share_proof_form_url']}",
        NON_FABRICATION_DISCLOSURE,
    ])


def summarize_history(history, snapshot, access_issues=None):
    history = history if isinstance(history, dict) else {}
    snapshots = []
    seen = set()
    for raw_snapshot in history.get("snapshots", []):
        normalized = normalize_snapshot(raw_snapshot)
        if not normalized:
            continue
        key = normalized["generated_at"]
        if key in seen:
            continue
        snapshots.append(normalized)
        seen.add(key)

    if access_issues:
        return {
            "mode": "manual append-only",
            "history_url": HISTORY_URL,
            "record_workflow_url": RECORD_WORKFLOW_URL,
            "recording_policy": RECORDING_POLICY,
            "snapshots_recorded": len(snapshots),
            "latest_velocity": {
                "status": "unavailable",
                "reason": "Public API access issues were present, so velocity deltas were not computed.",
            },
        }

    current = normalize_snapshot(snapshot)
    if snapshots and current:
        latest_velocity = build_velocity(snapshots[-1], current)
    else:
        latest_velocity = build_velocity(None, current or snapshot)

    return {
        "mode": "manual append-only",
        "history_url": HISTORY_URL,
        "record_workflow_url": RECORD_WORKFLOW_URL,
        "recording_policy": RECORDING_POLICY,
        "snapshots_recorded": len(snapshots),
        "latest_velocity": latest_velocity,
    }


def build_traction_proof(memories, share_proofs, repo, issues, pulls, access_issues, history=None, distribution=None):
    access_issues = list(access_issues or [])
    share_proofs = share_proofs if isinstance(share_proofs, dict) else {}
    issues = issues if isinstance(issues, list) else []
    pulls = pulls if isinstance(pulls, list) else []

    repo_summary = summarize_repo(repo)
    memory_summary = summarize_memories(memories)
    share_summary = summarize_share_proofs(share_proofs)
    issueops_summary = summarize_issueops(issues)
    contributors = collect_contributors(issues, pulls, share_proofs)
    target_count = normalize_positive_int(
        os.environ.get("NOOSPHERE_TRACTION_TARGET_CONTRIBUTORS"),
        DEFAULT_TARGET_CONTRIBUTORS,
    )
    target_progress = {
        "target_contributor_count": target_count,
        "real_contributor_identities": len(contributors),
        "contributors": contributors,
        "progress_percent": round(min(100, (len(contributors) / target_count) * 100), 1) if target_count else 0,
        "counting_rule": (
            "Counts public Share Proof Issue authors, public Consciousness Issue authors, "
            "public Pull Request authors, and submitted_by fields from share_proofs.json. "
            "Stars, forks, watchers, downloads, reposts, retention, and subscribers are not contributors."
        ),
    }
    bottleneck = choose_bottleneck(
        memory_summary,
        share_summary,
        len(contributors),
        target_count,
        access_issues,
        distribution,
    )
    first_proof_action = build_first_proof_action(
        memory_summary,
        share_summary,
        target_progress,
    )

    snapshot = {
        "generated_at": utc_now_iso(),
        "source": (
            "GitHub REST API repository/issues/pulls plus generated Noosphere "
            "consciousness_index.json and share_proofs.json"
        ),
        "repo": repo_summary,
        "memory": memory_summary,
        "share_proof": {
            **share_summary,
            "form_url": SHARE_PROOF_FORM_URL,
        },
        "issueops": issueops_summary,
        "pull_requests": {
            "public_prs_sampled": len([pull for pull in pulls if isinstance(pull, dict)]),
            "authors_sampled": len({actor_login(pull) for pull in pulls if actor_login(pull)}),
            "source_url": f"https://api.github.com/repos/{GITHUB_REPO.strip()}/pulls",
        },
        "target_progress": target_progress,
        "distribution": distribution or {
            "status": "not_checked",
            "package": PYPI_PROJECT,
            "disclaimer": "Distribution readiness was not checked for this local snapshot input.",
        },
        "bottleneck": bottleneck,
        "first_proof_action": first_proof_action,
        "actions": {
            "open_home": NOOSPHERE_HOME_URL,
            "upload_memory": UPLOAD_FORM_URL,
            "record_share_proof": SHARE_PROOF_FORM_URL,
            "open_growth_proof": first_proof_action["growth_issue_form_url"],
            "github_actions": f"{REPO_URL}/actions",
        },
        "access_issues": access_issues,
        "disclaimer": NON_FABRICATION_DISCLOSURE,
    }
    history_summary = summarize_history(history, snapshot, access_issues)
    snapshot["history"] = history_summary
    snapshot["share_card"] = build_share_card(
        repo_summary,
        memory_summary,
        share_summary,
        target_progress,
        bottleneck,
        history_summary,
        first_proof_action,
        snapshot["distribution"],
    )
    return snapshot


def write_traction_proof():
    access_issues = []
    memories = read_json_file(
        CONSCIOUSNESS_INDEX_FILE,
        [],
        access_issues,
        "consciousness_index.json",
    )
    share_proofs = read_json_file(
        SHARE_PROOF_FILE,
        {},
        access_issues,
        "share_proofs.json",
    )
    history = read_optional_json_file(
        HISTORY_FILE,
        {"snapshots": []},
        access_issues,
        "traction_history.json",
    )

    repo, repo_error = fetch_repository()
    issues, issues_error = fetch_repository_issues()
    pulls, pulls_error = fetch_repository_pulls()
    for error in (repo_error, issues_error, pulls_error):
        if error:
            access_issues.append(error)

    local_version = read_local_package_version(access_issues)
    tag_trigger_supported = read_publish_workflow_supports_tag_push(access_issues)
    pypi_project, pypi_error = fetch_pypi_project()
    release_tag = f"v{local_version}" if local_version else ""
    release, release_error = fetch_github_release(release_tag) if release_tag else (None, "Release tag unavailable")
    distribution = build_distribution_readiness(
        local_version=local_version,
        pypi_project=pypi_project,
        release=release,
        pypi_error=pypi_error,
        release_error=release_error,
        tag_trigger_supported=tag_trigger_supported,
    )

    snapshot = build_traction_proof(
        memories=memories,
        share_proofs=share_proofs,
        repo=repo,
        issues=issues,
        pulls=pulls,
        access_issues=access_issues,
        history=history,
        distribution=distribution,
    )
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(
        "OK Built traction proof: "
        f"{snapshot['target_progress']['real_contributor_identities']} real contributors, "
        f"{snapshot['share_proof']['reviewable_public_urls']} reviewable proof URLs"
    )
    if snapshot["access_issues"]:
        print(f"   Access issues: {len(snapshot['access_issues'])}")
    print(f"   Bottleneck: {snapshot['bottleneck']['stage']}")
    print(f"   Distribution: {snapshot['distribution']['status']}")
    print(f"   Output: {OUTPUT_FILE}")
    print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    return snapshot


if __name__ == "__main__":
    write_traction_proof()
