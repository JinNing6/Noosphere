"""Validate Noosphere Experience Records without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORDS_ROOT = REPO_ROOT / "experience_records"
SCHEMA_PATH = REPO_ROOT / "schemas" / "experience-record-v0.1.schema.json"
SKILL_REGISTRY_PATH = REPO_ROOT / "shared_skills" / "registry.json"
MAX_RECORD_BYTES = 64 * 1024

EXPERIENCE_ID_RE = re.compile(r"^exp-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]{8}$")
EVIDENCE_ID_RE = re.compile(r"^ev-[a-z0-9]+(?:-[a-z0-9]+)*$")
CHECK_ID_RE = re.compile(r"^check-[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
URL_RE = re.compile(r"https://[^\s<>\"]+")
GITHUB_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
GITHUB_AUTHOR_REF_RE = re.compile(
    r"^github:[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$"
)
GITHUB_COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")
GITHUB_WORKFLOW_RUN_RE = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/actions/runs/([0-9]+)/?$"
)
SENSITIVE_QUERY_KEY_RE = re.compile(
    r"(?i)(?:^|[?&])(?:access_?token|api_?key|auth|credential|secret|signature)="
)

PRIVATE_HOME_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:\\Users\\(?!<|%)[^\\\s]+"),
    re.compile(r"(?i)(?<![%\w])/(?:Users|home)/(?!<)[^/\s]+"),
)
SECRET_PATTERNS = (
    re.compile(r"\bgh[oprsu]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\b(?:sk|xox[baprs])-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
OVERRIDE_PATTERNS = (
    re.compile(
        r"\b(?:ignore|disregard|override)\b.{0,80}"
        r"\b(?:previous|system|developer|safety)\b.{0,60}\binstructions?\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"\b(?:system|developer)\s+prompt\b", re.IGNORECASE),
    re.compile(
        r"\b(?:exfiltrate|leak|reveal)\b.{0,80}"
        r"\b(?:secret|credential|token|private key)\b",
        re.IGNORECASE | re.DOTALL,
    ),
)
UNSAFE_RESOLUTION_PATTERNS = (
    re.compile(r"\b(?:curl|wget)\b[^\n|]{0,500}\|\s*(?:ba)?sh\b", re.IGNORECASE),
    re.compile(r"\brm\s+-rf\s+(?:/|~|\$HOME)(?:\s|$)", re.IGNORECASE),
    re.compile(
        r"\b(?:powershell|pwsh)\b[^\n]{0,200}\b(?:-enc|-encodedcommand)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bRemove-Item\b[^\n]{0,300}\b-Recurse\b[^\n]{0,300}"
        r"\b-Force\b[^\n]{0,100}(?:\$HOME|~|[A-Za-z]:\\)",
        re.IGNORECASE,
    ),
)

TOP_LEVEL_KEYS = {
    "schema_version",
    "record_kind",
    "experience_id",
    "title",
    "summary",
    "lifecycle",
    "review",
    "screening",
    "context",
    "symptom",
    "attempts",
    "root_cause",
    "resolution",
    "verification",
    "applicability",
    "risks",
    "rollback",
    "evidence",
    "relations",
    "provenance",
    "redaction",
}


def _error(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def _object(
    value: Any,
    path: str,
    errors: list[str],
    *,
    required: Iterable[str],
    allowed: Iterable[str],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        _error(errors, path, "must be an object")
        return None
    required_set = set(required)
    allowed_set = set(allowed)
    for key in sorted(required_set - value.keys()):
        _error(errors, path, f"missing required field {key!r}")
    for key in sorted(value.keys() - allowed_set):
        _error(errors, path, f"unknown field {key!r}")
    return value


def _string(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int = 1,
    maximum: int = 2000,
    pattern: re.Pattern[str] | None = None,
) -> str | None:
    if not isinstance(value, str):
        _error(errors, path, "must be a string")
        return None
    if not minimum <= len(value) <= maximum:
        _error(errors, path, f"length must be between {minimum} and {maximum}")
    if pattern is not None and not pattern.fullmatch(value):
        _error(errors, path, f"must match {pattern.pattern}")
    return value


def _enum(value: Any, path: str, errors: list[str], choices: set[str]) -> str | None:
    if not isinstance(value, str) or value not in choices:
        _error(errors, path, f"must be one of {sorted(choices)}")
        return None
    return value


def _timestamp(value: Any, path: str, errors: list[str]) -> datetime | None:
    text = _string(value, path, errors, maximum=64)
    if text is None:
        return None
    if not RFC3339_RE.fullmatch(text):
        _error(errors, path, "must be an RFC 3339 date-time with timezone")
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        _error(errors, path, "must be an RFC 3339 date-time")
        return None
    if parsed.tzinfo is None:
        _error(errors, path, "must include a timezone")
    return parsed


def _string_list(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum_items: int = 1,
    maximum_items: int = 64,
    maximum_length: int = 1000,
    pattern: re.Pattern[str] | None = None,
) -> list[str]:
    if not isinstance(value, list):
        _error(errors, path, "must be an array")
        return []
    if len(value) < minimum_items:
        _error(errors, path, f"must contain at least {minimum_items} item(s)")
    if len(value) > maximum_items:
        _error(errors, path, f"must contain at most {maximum_items} item(s)")
    output: list[str] = []
    for index, item in enumerate(value):
        text = _string(
            item,
            f"{path}[{index}]",
            errors,
            maximum=maximum_length,
            pattern=pattern,
        )
        if text is not None:
            output.append(text)
    if len(output) != len(set(output)):
        _error(errors, path, "must not contain duplicate values")
    return output


def _all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def _validate_lifecycle(
    record: dict[str, Any], errors: list[str]
) -> tuple[str | None, str | None]:
    lifecycle = _object(
        record.get("lifecycle"),
        "lifecycle",
        errors,
        required={"status", "created_at", "updated_at"},
        allowed={"status", "created_at", "updated_at"},
    )
    review = _object(
        record.get("review"),
        "review",
        errors,
        required={"status"},
        allowed={"status", "reviewer", "reviewed_at", "notes"},
    )
    lifecycle_status = None
    review_status = None
    updated: datetime | None = None
    review_decided_at: datetime | None = None
    if lifecycle:
        lifecycle_status = _enum(
            lifecycle.get("status"),
            "lifecycle.status",
            errors,
            {"candidate", "reviewed", "superseded", "withdrawn"},
        )
        created = _timestamp(
            lifecycle.get("created_at"), "lifecycle.created_at", errors
        )
        updated = _timestamp(
            lifecycle.get("updated_at"), "lifecycle.updated_at", errors
        )
        if created and updated and updated < created:
            _error(errors, "lifecycle.updated_at", "must not precede created_at")
    if review:
        review_status = _enum(
            review.get("status"),
            "review.status",
            errors,
            {"pending", "approved", "changes-requested"},
        )
        if "notes" in review:
            _string(review["notes"], "review.notes", errors, maximum=1000)
        if review_status in {"approved", "changes-requested"}:
            _string(review.get("reviewer"), "review.reviewer", errors, maximum=100)
            review_decided_at = _timestamp(
                review.get("reviewed_at"), "review.reviewed_at", errors
            )
            if review_status == "changes-requested":
                _string(review.get("notes"), "review.notes", errors, maximum=1000)
        elif "reviewer" in review or "reviewed_at" in review:
            _error(
                errors,
                "review",
                "reviewer and reviewed_at are allowed only after a review decision",
            )
    if lifecycle_status in {"reviewed", "superseded"} and review_status != "approved":
        _error(
            errors,
            "review.status",
            f"must be approved when lifecycle.status is {lifecycle_status}",
        )
    if lifecycle_status == "candidate" and review_status == "approved":
        _error(errors, "review.status", "a candidate cannot already be approved")
    if updated and review_decided_at and updated < review_decided_at:
        _error(
            errors,
            "lifecycle.updated_at",
            "must not precede review.reviewed_at",
        )
    return lifecycle_status, review_status


def _validate_screening(record: dict[str, Any], errors: list[str]) -> None:
    screening = _object(
        record.get("screening"),
        "screening",
        errors,
        required={"status", "method", "screened_at", "findings"},
        allowed={"status", "method", "screened_at", "findings"},
    )
    if not screening:
        return
    _enum(screening.get("status"), "screening.status", errors, {"passed"})
    _enum(
        screening.get("method"),
        "screening.method",
        errors,
        {"repository-policy-gate-v1", "github-experience-agent-v1"},
    )
    _timestamp(screening.get("screened_at"), "screening.screened_at", errors)
    _string_list(
        screening.get("findings"),
        "screening.findings",
        errors,
        minimum_items=0,
        maximum_items=32,
        maximum_length=500,
    )


def _validate_context(record: dict[str, Any], errors: list[str]) -> None:
    context = _object(
        record.get("context"),
        "context",
        errors,
        required={"platform", "environment", "constraints", "observed_at"},
        allowed={"platform", "environment", "constraints", "observed_at"},
    )
    if not context:
        return
    _enum(
        context.get("platform"),
        "context.platform",
        errors,
        {"windows", "macos", "linux", "cross-platform", "other"},
    )
    _string_list(context.get("environment"), "context.environment", errors)
    _string_list(context.get("constraints"), "context.constraints", errors)
    _timestamp(context.get("observed_at"), "context.observed_at", errors)


def _validate_narrative(record: dict[str, Any], errors: list[str]) -> None:
    symptom = _object(
        record.get("symptom"),
        "symptom",
        errors,
        required={"summary", "impact", "signals"},
        allowed={"summary", "impact", "signals"},
    )
    if symptom:
        _string(
            symptom.get("summary"), "symptom.summary", errors, minimum=8, maximum=1000
        )
        _string(
            symptom.get("impact"), "symptom.impact", errors, minimum=8, maximum=1000
        )
        _string_list(symptom.get("signals"), "symptom.signals", errors)

    root_cause = _object(
        record.get("root_cause"),
        "root_cause",
        errors,
        required={"summary", "mechanism"},
        allowed={"summary", "mechanism"},
    )
    if root_cause:
        _string(
            root_cause.get("summary"),
            "root_cause.summary",
            errors,
            minimum=8,
            maximum=1000,
        )
        _string(
            root_cause.get("mechanism"),
            "root_cause.mechanism",
            errors,
            minimum=8,
            maximum=2000,
        )

    resolution = _object(
        record.get("resolution"),
        "resolution",
        errors,
        required={"summary", "steps"},
        allowed={"summary", "steps"},
    )
    if resolution:
        _string(
            resolution.get("summary"),
            "resolution.summary",
            errors,
            minimum=8,
            maximum=1000,
        )
        _string_list(resolution.get("steps"), "resolution.steps", errors)


def _validate_attempts(record: dict[str, Any], errors: list[str]) -> set[str]:
    attempts = record.get("attempts")
    refs: set[str] = set()
    if not isinstance(attempts, list):
        _error(errors, "attempts", "must be an array")
        return refs
    if not attempts:
        _error(errors, "attempts", "must contain at least one attempt")
    if len(attempts) > 32:
        _error(errors, "attempts", "must contain at most 32 attempts")
    sequences: list[int] = []
    for index, value in enumerate(attempts):
        path = f"attempts[{index}]"
        attempt = _object(
            value,
            path,
            errors,
            required={
                "sequence",
                "action",
                "rationale",
                "result",
                "observation",
                "evidence_refs",
            },
            allowed={
                "sequence",
                "action",
                "rationale",
                "result",
                "observation",
                "failure_mechanism",
                "evidence_refs",
            },
        )
        if not attempt:
            continue
        sequence = attempt.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            _error(errors, f"{path}.sequence", "must be an integer greater than zero")
        else:
            sequences.append(sequence)
        _string(
            attempt.get("action"), f"{path}.action", errors, minimum=3, maximum=1000
        )
        _string(
            attempt.get("rationale"),
            f"{path}.rationale",
            errors,
            minimum=3,
            maximum=1000,
        )
        result = _enum(
            attempt.get("result"),
            f"{path}.result",
            errors,
            {"failed", "partial", "succeeded", "skipped"},
        )
        _string(
            attempt.get("observation"),
            f"{path}.observation",
            errors,
            minimum=3,
            maximum=1000,
        )
        if result in {"failed", "partial"}:
            _string(
                attempt.get("failure_mechanism"),
                f"{path}.failure_mechanism",
                errors,
                minimum=3,
                maximum=1000,
            )
        elif "failure_mechanism" in attempt:
            _error(
                errors,
                f"{path}.failure_mechanism",
                "is allowed only for failed or partial attempts",
            )
        refs.update(
            _string_list(
                attempt.get("evidence_refs"),
                f"{path}.evidence_refs",
                errors,
                minimum_items=0,
                pattern=EVIDENCE_ID_RE,
            )
        )
    if sequences != list(range(1, len(attempts) + 1)):
        _error(
            errors,
            "attempts",
            "sequence values must be consecutive and match array order",
        )
    return refs


def _validate_workflow_evidence(
    item: dict[str, Any], path: str, errors: list[str]
) -> None:
    source_path = f"{path}.source"
    source = _object(
        item.get("source"),
        source_path,
        errors,
        required={
            "repository_url",
            "commit_sha",
            "workflow_run_url",
            "workflow_job_name",
            "workflow_step_name",
        },
        allowed={
            "repository_url",
            "commit_sha",
            "workflow_run_url",
            "workflow_job_name",
            "workflow_step_name",
            "artifact_sha256",
        },
    )
    verification_path = f"{path}.machine_verification"
    verification = _object(
        item.get("machine_verification"),
        verification_path,
        errors,
        required={
            "status",
            "verified_at",
            "source_repository",
            "commit_sha",
            "workflow_run_id",
            "workflow_run_url",
            "workflow_job_name",
            "workflow_step_name",
            "artifact_sha256",
            "claim_boundary",
        },
        allowed={
            "status",
            "verified_at",
            "source_repository",
            "commit_sha",
            "workflow_run_id",
            "workflow_run_url",
            "workflow_job_name",
            "workflow_step_name",
            "artifact_sha256",
            "claim_boundary",
        },
    )
    if not source or not verification:
        return

    repository_url = _string(
        source.get("repository_url"),
        f"{source_path}.repository_url",
        errors,
        maximum=300,
    )
    repository_identity = ""
    if repository_url:
        parsed_repository = urlsplit(repository_url.rstrip("/"))
        if (
            parsed_repository.scheme != "https"
            or parsed_repository.netloc.lower() != "github.com"
            or parsed_repository.query
            or parsed_repository.fragment
        ):
            _error(
                errors,
                f"{source_path}.repository_url",
                "must be a public GitHub repository URL without query or fragment",
            )
        repository_identity = parsed_repository.path.strip("/")
        if not GITHUB_REPOSITORY_RE.fullmatch(repository_identity):
            _error(
                errors,
                f"{source_path}.repository_url",
                "must identify exactly one GitHub owner/repository",
            )
    source_commit = _string(
        source.get("commit_sha"),
        f"{source_path}.commit_sha",
        errors,
        pattern=GITHUB_COMMIT_RE,
    )
    run_url = _string(
        source.get("workflow_run_url"),
        f"{source_path}.workflow_run_url",
        errors,
        maximum=300,
    )
    run_identity = ""
    run_id: int | None = None
    if run_url:
        match = GITHUB_WORKFLOW_RUN_RE.fullmatch(run_url)
        if not match:
            _error(
                errors,
                f"{source_path}.workflow_run_url",
                "must identify one public GitHub Actions workflow run",
            )
        else:
            run_identity = f"{match.group(1)}/{match.group(2)}"
            run_id = int(match.group(3))
            if (
                repository_identity
                and run_identity.lower() != repository_identity.lower()
            ):
                _error(
                    errors,
                    f"{source_path}.workflow_run_url",
                    "must belong to source.repository_url",
                )
    source_job = _string(
        source.get("workflow_job_name"),
        f"{source_path}.workflow_job_name",
        errors,
        maximum=200,
    )
    source_step = _string(
        source.get("workflow_step_name"),
        f"{source_path}.workflow_step_name",
        errors,
        maximum=200,
    )
    source_artifact = source.get("artifact_sha256")
    if source_artifact is not None:
        source_artifact = _string(
            source_artifact,
            f"{source_path}.artifact_sha256",
            errors,
            maximum=80,
        )
        if isinstance(source_artifact, str):
            normalized = source_artifact.removeprefix("sha256:")
            if not SHA256_RE.fullmatch(normalized):
                _error(
                    errors,
                    f"{source_path}.artifact_sha256",
                    "must be a SHA-256 digest",
                )
            source_artifact = f"sha256:{normalized}"

    _enum(
        verification.get("status"),
        f"{verification_path}.status",
        errors,
        {"workflow-verified"},
    )
    _timestamp(
        verification.get("verified_at"),
        f"{verification_path}.verified_at",
        errors,
    )
    verified_repository = _string(
        verification.get("source_repository"),
        f"{verification_path}.source_repository",
        errors,
        maximum=200,
        pattern=GITHUB_REPOSITORY_RE,
    )
    verified_commit = _string(
        verification.get("commit_sha"),
        f"{verification_path}.commit_sha",
        errors,
        pattern=GITHUB_COMMIT_RE,
    )
    verified_run_id = verification.get("workflow_run_id")
    if (
        not isinstance(verified_run_id, int)
        or isinstance(verified_run_id, bool)
        or verified_run_id < 1
    ):
        _error(
            errors,
            f"{verification_path}.workflow_run_id",
            "must be a positive integer",
        )
    verified_run_url = _string(
        verification.get("workflow_run_url"),
        f"{verification_path}.workflow_run_url",
        errors,
        maximum=300,
    )
    verified_job = _string(
        verification.get("workflow_job_name"),
        f"{verification_path}.workflow_job_name",
        errors,
        maximum=200,
    )
    verified_step = _string(
        verification.get("workflow_step_name"),
        f"{verification_path}.workflow_step_name",
        errors,
        maximum=200,
    )
    verified_artifact = verification.get("artifact_sha256")
    if verified_artifact is not None:
        verified_artifact = _string(
            verified_artifact,
            f"{verification_path}.artifact_sha256",
            errors,
            maximum=80,
        )
        if isinstance(verified_artifact, str) and not re.fullmatch(
            r"sha256:[a-f0-9]{64}", verified_artifact
        ):
            _error(
                errors,
                f"{verification_path}.artifact_sha256",
                "must use sha256:<64 lowercase hex>",
            )
    claim_boundary = _string(
        verification.get("claim_boundary"),
        f"{verification_path}.claim_boundary",
        errors,
        minimum=20,
        maximum=500,
    )

    comparisons = (
        (
            verified_repository,
            repository_identity,
            f"{verification_path}.source_repository",
        ),
        (verified_commit, source_commit, f"{verification_path}.commit_sha"),
        (verified_run_url, run_url, f"{verification_path}.workflow_run_url"),
        (verified_job, source_job, f"{verification_path}.workflow_job_name"),
        (verified_step, source_step, f"{verification_path}.workflow_step_name"),
        (
            verified_artifact,
            source_artifact,
            f"{verification_path}.artifact_sha256",
        ),
    )
    for actual, expected, field_path in comparisons:
        if actual != expected:
            _error(errors, field_path, "must match the canonical workflow source")
    if isinstance(verified_run_id, int) and run_id and verified_run_id != run_id:
        _error(
            errors,
            f"{verification_path}.workflow_run_id",
            "must match source.workflow_run_url",
        )
    if item.get("url") != run_url:
        _error(errors, f"{path}.url", "must match source.workflow_run_url")
    if (
        claim_boundary
        and "semantic reproduction remains a separate review gate"
        not in claim_boundary.lower()
    ):
        _error(
            errors,
            f"{verification_path}.claim_boundary",
            "must preserve the semantic-reproduction boundary",
        )


def _validate_evidence(
    record: dict[str, Any], errors: list[str]
) -> tuple[set[str], dict[str, str]]:
    values = record.get("evidence")
    ids: set[str] = set()
    visibility: dict[str, str] = {}
    if not isinstance(values, list):
        _error(errors, "evidence", "must be an array")
        return ids, visibility
    if not values:
        _error(errors, "evidence", "must contain at least one evidence item")
    if len(values) > 64:
        _error(errors, "evidence", "must contain at most 64 evidence items")
    for index, value in enumerate(values):
        path = f"evidence[{index}]"
        item = _object(
            value,
            path,
            errors,
            required={"evidence_id", "kind", "visibility", "summary", "captured_at"},
            allowed={
                "evidence_id",
                "kind",
                "visibility",
                "summary",
                "captured_at",
                "url",
                "sha256",
                "source",
                "machine_verification",
            },
        )
        if not item:
            continue
        evidence_id = _string(
            item.get("evidence_id"),
            f"{path}.evidence_id",
            errors,
            pattern=EVIDENCE_ID_RE,
        )
        if evidence_id:
            if evidence_id in ids:
                _error(errors, f"{path}.evidence_id", "must be unique")
            ids.add(evidence_id)
        evidence_kind = _enum(
            item.get("kind"),
            f"{path}.kind",
            errors,
            {
                "user-attestation",
                "filesystem-metadata",
                "command-receipt",
                "public-url",
                "artifact-digest",
                "workflow-run",
            },
        )
        item_visibility = _enum(
            item.get("visibility"),
            f"{path}.visibility",
            errors,
            {"public", "private-redacted", "local-only"},
        )
        if evidence_id and item_visibility:
            visibility[evidence_id] = item_visibility
        _string(item.get("summary"), f"{path}.summary", errors, minimum=8, maximum=2000)
        _timestamp(item.get("captured_at"), f"{path}.captured_at", errors)
        if "url" in item:
            url = _string(item["url"], f"{path}.url", errors, maximum=2000)
            if url:
                parsed = urlsplit(url)
                if parsed.scheme != "https" or not parsed.netloc:
                    _error(errors, f"{path}.url", "must be an absolute HTTPS URL")
                if (
                    parsed.username
                    or parsed.password
                    or parsed.query
                    or parsed.fragment
                ):
                    _error(
                        errors,
                        f"{path}.url",
                        "must not include credentials, query, or fragment",
                    )
        if "sha256" in item:
            _string(item["sha256"], f"{path}.sha256", errors, pattern=SHA256_RE)
        if evidence_kind in {"public-url", "workflow-run"}:
            if "url" not in item:
                _error(
                    errors, f"{path}.url", f"is required for {evidence_kind} evidence"
                )
            if item_visibility != "public":
                _error(
                    errors,
                    f"{path}.visibility",
                    f"must be public for {evidence_kind} evidence",
                )
        if evidence_kind == "workflow-run":
            _validate_workflow_evidence(item, path, errors)
        elif "source" in item or "machine_verification" in item:
            _error(
                errors,
                path,
                "source and machine_verification are allowed only for workflow-run evidence",
            )
        if evidence_kind == "artifact-digest" and "sha256" not in item:
            _error(errors, f"{path}.sha256", "is required for artifact-digest evidence")
    return ids, visibility


def _validate_verification(
    record: dict[str, Any], errors: list[str]
) -> tuple[str | None, set[str]]:
    verification = _object(
        record.get("verification"),
        "verification",
        errors,
        required={"level", "summary", "checks"},
        allowed={"level", "summary", "checks"},
    )
    refs: set[str] = set()
    if not verification:
        return None, refs
    level = _enum(
        verification.get("level"),
        "verification.level",
        errors,
        {"self-observed", "locally-verified", "independently-reproduced"},
    )
    _string(
        verification.get("summary"),
        "verification.summary",
        errors,
        minimum=8,
        maximum=1000,
    )
    checks = verification.get("checks")
    if not isinstance(checks, list):
        _error(errors, "verification.checks", "must be an array")
        return level, refs
    if not checks:
        _error(errors, "verification.checks", "must contain at least one check")
    if len(checks) > 64:
        _error(errors, "verification.checks", "must contain at most 64 checks")
    check_ids: set[str] = set()
    pass_count = 0
    external_pass_count = 0
    for index, value in enumerate(checks):
        path = f"verification.checks[{index}]"
        check = _object(
            value,
            path,
            errors,
            required={
                "check_id",
                "method",
                "result",
                "observed_at",
                "summary",
                "evidence_refs",
            },
            allowed={
                "check_id",
                "method",
                "result",
                "observed_at",
                "summary",
                "evidence_refs",
            },
        )
        if not check:
            continue
        check_id = _string(
            check.get("check_id"), f"{path}.check_id", errors, pattern=CHECK_ID_RE
        )
        if check_id:
            if check_id in check_ids:
                _error(errors, f"{path}.check_id", "must be unique")
            check_ids.add(check_id)
        method = _enum(
            check.get("method"),
            f"{path}.method",
            errors,
            {"command", "inspection", "measurement", "external-run"},
        )
        result = _enum(
            check.get("result"), f"{path}.result", errors, {"pass", "fail", "partial"}
        )
        if result == "pass":
            pass_count += 1
            if method == "external-run":
                external_pass_count += 1
        _timestamp(check.get("observed_at"), f"{path}.observed_at", errors)
        _string(
            check.get("summary"), f"{path}.summary", errors, minimum=8, maximum=1000
        )
        refs.update(
            _string_list(
                check.get("evidence_refs"),
                f"{path}.evidence_refs",
                errors,
                minimum_items=1,
                pattern=EVIDENCE_ID_RE,
            )
        )
    if pass_count == 0:
        _error(errors, "verification.checks", "must contain at least one passing check")
    if level == "independently-reproduced" and external_pass_count == 0:
        _error(
            errors,
            "verification.level",
            "independently-reproduced requires a passing external-run check",
        )
    return level, refs


def _validate_safety_and_relations(
    record: dict[str, Any], errors: list[str]
) -> set[str]:
    refs: set[str] = set()
    applicability = _object(
        record.get("applicability"),
        "applicability",
        errors,
        required={"applies_when", "avoid_when"},
        allowed={"applies_when", "avoid_when"},
    )
    if applicability:
        _string_list(
            applicability.get("applies_when"), "applicability.applies_when", errors
        )
        _string_list(
            applicability.get("avoid_when"), "applicability.avoid_when", errors
        )

    risks = record.get("risks")
    if not isinstance(risks, list):
        _error(errors, "risks", "must be an array")
    else:
        if not risks:
            _error(errors, "risks", "must contain at least one risk")
        if len(risks) > 32:
            _error(errors, "risks", "must contain at most 32 risks")
        for index, value in enumerate(risks):
            path = f"risks[{index}]"
            risk = _object(
                value,
                path,
                errors,
                required={"severity", "description", "mitigation"},
                allowed={"severity", "description", "mitigation"},
            )
            if risk:
                _enum(
                    risk.get("severity"),
                    f"{path}.severity",
                    errors,
                    {"low", "medium", "high"},
                )
                _string(
                    risk.get("description"),
                    f"{path}.description",
                    errors,
                    minimum=8,
                    maximum=1000,
                )
                _string(
                    risk.get("mitigation"),
                    f"{path}.mitigation",
                    errors,
                    minimum=8,
                    maximum=1000,
                )

    rollback = _object(
        record.get("rollback"),
        "rollback",
        errors,
        required={"available", "conditions", "steps"},
        allowed={"available", "conditions", "steps", "notes"},
    )
    if rollback:
        available = rollback.get("available")
        if not isinstance(available, bool):
            _error(errors, "rollback.available", "must be a boolean")
        minimum_items = 1 if available is True else 0
        conditions = _string_list(
            rollback.get("conditions"),
            "rollback.conditions",
            errors,
            minimum_items=minimum_items,
        )
        steps = _string_list(
            rollback.get("steps"),
            "rollback.steps",
            errors,
            minimum_items=minimum_items,
        )
        if available is False:
            if conditions or steps:
                _error(
                    errors,
                    "rollback",
                    "conditions and steps must be empty when rollback is unavailable",
                )
            _string(
                rollback.get("notes"),
                "rollback.notes",
                errors,
                minimum=8,
                maximum=1000,
            )
        elif "notes" in rollback:
            _string(
                rollback.get("notes"),
                "rollback.notes",
                errors,
                minimum=8,
                maximum=1000,
            )

    relations = _object(
        record.get("relations"),
        "relations",
        errors,
        required={
            "related_experiences",
            "related_skills",
            "derived_skill_candidates",
            "supersedes",
        },
        allowed={
            "related_experiences",
            "related_skills",
            "derived_skill_candidates",
            "supersedes",
        },
    )
    if relations:
        _string_list(
            relations.get("related_experiences"),
            "relations.related_experiences",
            errors,
            minimum_items=0,
            pattern=EXPERIENCE_ID_RE,
        )
        _string_list(
            relations.get("derived_skill_candidates"),
            "relations.derived_skill_candidates",
            errors,
            minimum_items=0,
            pattern=SKILL_NAME_RE,
        )
        _string_list(
            relations.get("supersedes"),
            "relations.supersedes",
            errors,
            minimum_items=0,
            pattern=EXPERIENCE_ID_RE,
        )
        skills = relations.get("related_skills")
        if not isinstance(skills, list):
            _error(errors, "relations.related_skills", "must be an array")
        else:
            if len(skills) > 32:
                _error(
                    errors,
                    "relations.related_skills",
                    "must contain at most 32 Skill references",
                )
            for index, value in enumerate(skills):
                path = f"relations.related_skills[{index}]"
                skill = _object(
                    value,
                    path,
                    errors,
                    required={"name", "version", "sha256"},
                    allowed={"name", "version", "sha256"},
                )
                if skill:
                    _string(
                        skill.get("name"), f"{path}.name", errors, pattern=SKILL_NAME_RE
                    )
                    _string(
                        skill.get("version"),
                        f"{path}.version",
                        errors,
                        pattern=SEMVER_RE,
                    )
                    _string(
                        skill.get("sha256"), f"{path}.sha256", errors, pattern=SHA256_RE
                    )

    provenance = _object(
        record.get("provenance"),
        "provenance",
        errors,
        required={"source_type", "author_ref", "captured_at", "source_evidence_refs"},
        allowed={
            "source_type",
            "author_ref",
            "captured_at",
            "source_evidence_refs",
            "source_issue",
        },
    )
    if provenance:
        _enum(
            provenance.get("source_type"),
            "provenance.source_type",
            errors,
            {
                "user-report",
                "maintainer-observation",
                "public-issue",
                "external-reference",
            },
        )
        author_ref = _string(
            provenance.get("author_ref"), "provenance.author_ref", errors, maximum=100
        )
        _timestamp(provenance.get("captured_at"), "provenance.captured_at", errors)
        refs.update(
            _string_list(
                provenance.get("source_evidence_refs"),
                "provenance.source_evidence_refs",
                errors,
                minimum_items=1,
                pattern=EVIDENCE_ID_RE,
            )
        )
        if "source_issue" in provenance:
            source_issue = _object(
                provenance.get("source_issue"),
                "provenance.source_issue",
                errors,
                required={"provider", "repository", "issue_number", "url"},
                allowed={"provider", "repository", "issue_number", "url"},
            )
            if source_issue:
                if source_issue.get("provider") != "github":
                    _error(
                        errors,
                        "provenance.source_issue.provider",
                        "must equal 'github'",
                    )
                repository = _string(
                    source_issue.get("repository"),
                    "provenance.source_issue.repository",
                    errors,
                    maximum=200,
                    pattern=GITHUB_REPOSITORY_RE,
                )
                issue_number = source_issue.get("issue_number")
                if (
                    not isinstance(issue_number, int)
                    or isinstance(issue_number, bool)
                    or issue_number < 1
                ):
                    _error(
                        errors,
                        "provenance.source_issue.issue_number",
                        "must be a positive integer",
                    )
                issue_url = _string(
                    source_issue.get("url"),
                    "provenance.source_issue.url",
                    errors,
                    maximum=300,
                )
                expected_url = (
                    f"https://github.com/{repository}/issues/{issue_number}"
                    if repository and isinstance(issue_number, int)
                    else ""
                )
                if issue_url and issue_url != expected_url:
                    _error(
                        errors,
                        "provenance.source_issue.url",
                        "must match repository and issue_number",
                    )
                if author_ref and not GITHUB_AUTHOR_REF_RE.fullmatch(author_ref):
                    _error(
                        errors,
                        "provenance.author_ref",
                        "must be bound to github:<authenticated-login> for Issue intake",
                    )

    redaction = _object(
        record.get("redaction"),
        "redaction",
        errors,
        required={"status", "removed_categories", "notes"},
        allowed={"status", "removed_categories", "notes"},
    )
    if redaction:
        status = _enum(
            redaction.get("status"),
            "redaction.status",
            errors,
            {"applied", "not-required", "pending"},
        )
        if status == "pending":
            _error(
                errors,
                "redaction.status",
                "tracked Experience Records cannot have pending redaction",
            )
        categories = _string_list(
            redaction.get("removed_categories"),
            "redaction.removed_categories",
            errors,
            minimum_items=0,
        )
        allowed_categories = {
            "personal-identifiers",
            "absolute-user-paths",
            "session-identifiers",
            "raw-content",
            "secrets",
            "other",
        }
        for category in categories:
            if category not in allowed_categories:
                _error(
                    errors,
                    "redaction.removed_categories",
                    f"unknown category {category!r}",
                )
        if status == "applied" and not categories:
            _error(
                errors,
                "redaction.removed_categories",
                "must identify at least one category when redaction is applied",
            )
        if status == "not-required" and categories:
            _error(
                errors,
                "redaction.removed_categories",
                "must be empty when redaction is not required",
            )
        _string(
            redaction.get("notes"), "redaction.notes", errors, minimum=8, maximum=1000
        )
    return refs


def validate_record(record: Any, *, relative_path: Path | None = None) -> list[str]:
    """Return every validation error for one decoded Experience Record."""

    errors: list[str] = []
    top = _object(
        record,
        "$",
        errors,
        required=TOP_LEVEL_KEYS,
        allowed=TOP_LEVEL_KEYS,
    )
    if top is None:
        return errors
    canonical_size = len(
        json.dumps(top, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    if canonical_size > MAX_RECORD_BYTES:
        _error(
            errors,
            "$",
            f"canonical JSON exceeds the {MAX_RECORD_BYTES}-byte record limit",
        )

    if top.get("schema_version") != "0.1":
        _error(errors, "schema_version", "must equal '0.1'")
    if top.get("record_kind") != "experience":
        _error(errors, "record_kind", "must equal 'experience'")
    experience_id = _string(
        top.get("experience_id"),
        "experience_id",
        errors,
        pattern=EXPERIENCE_ID_RE,
    )
    _string(top.get("title"), "title", errors, minimum=8, maximum=160)
    _string(top.get("summary"), "summary", errors, minimum=20, maximum=1000)

    lifecycle_status, _ = _validate_lifecycle(top, errors)
    _validate_screening(top, errors)
    _validate_context(top, errors)
    context = top.get("context")
    if (
        experience_id
        and isinstance(context, dict)
        and isinstance(context.get("observed_at"), str)
    ):
        observed_date = context["observed_at"][:10].replace("-", "")
        if experience_id[-8:] != observed_date:
            _error(
                errors,
                "experience_id",
                "date suffix must match context.observed_at",
            )
    _validate_narrative(top, errors)
    referenced = _validate_attempts(top, errors)
    evidence_ids, visibility = _validate_evidence(top, errors)
    verification_level, verification_refs = _validate_verification(top, errors)
    referenced.update(verification_refs)
    referenced.update(_validate_safety_and_relations(top, errors))

    relations = top.get("relations")
    if isinstance(relations, dict) and experience_id:
        for relation_name in ("related_experiences", "supersedes"):
            relation_values = relations.get(relation_name)
            if isinstance(relation_values, list) and experience_id in relation_values:
                _error(
                    errors,
                    f"relations.{relation_name}",
                    "must not contain the current experience_id",
                )

    unknown_refs = sorted(referenced - evidence_ids)
    for evidence_ref in unknown_refs:
        _error(errors, "evidence_refs", f"unknown evidence reference {evidence_ref!r}")

    if verification_level == "independently-reproduced":
        non_public = sorted(
            ref for ref in verification_refs if visibility.get(ref) != "public"
        )
        if non_public:
            _error(
                errors,
                "verification.level",
                "independently-reproduced checks may reference only public evidence; "
                f"non-public: {non_public}",
            )
    provenance = top.get("provenance")
    if isinstance(provenance, dict) and provenance.get("source_type") == "public-issue":
        source_refs = provenance.get("source_evidence_refs")
        if isinstance(source_refs, list):
            non_public_sources = sorted(
                ref
                for ref in source_refs
                if isinstance(ref, str) and visibility.get(ref) != "public"
            )
            if non_public_sources:
                _error(
                    errors,
                    "provenance.source_evidence_refs",
                    "public-issue provenance may reference only public evidence; "
                    f"non-public: {non_public_sources}",
                )

    if relative_path is not None and experience_id:
        if relative_path.stem != experience_id:
            _error(errors, "experience_id", "must match the record filename")
        directory = relative_path.parent.name
        allowed_statuses = {
            "candidates": {"candidate", "withdrawn"},
            "reviewed": {"reviewed", "superseded", "withdrawn"},
        }.get(directory)
        if allowed_statuses is None:
            _error(
                errors,
                "$path",
                "record must be directly under candidates/ or reviewed/",
            )
        elif lifecycle_status not in allowed_statuses:
            _error(
                errors,
                "lifecycle.status",
                f"must be one of {sorted(allowed_statuses)} for a record stored under "
                f"{directory}/",
            )

    serialized_strings = "\n".join(_all_strings(top))
    for pattern in PRIVATE_HOME_PATTERNS:
        if pattern.search(serialized_strings):
            _error(errors, "redaction", "contains an absolute user-home path")
            break
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized_strings):
            _error(errors, "redaction", "contains a credential-like secret")
            break
    for pattern in OVERRIDE_PATTERNS:
        if pattern.search(serialized_strings):
            _error(
                errors,
                "screening",
                "contains instruction-override or credential-exfiltration language",
            )
            break
    resolution = top.get("resolution")
    resolution_steps = (
        "\n".join(resolution.get("steps", []))
        if isinstance(resolution, dict) and isinstance(resolution.get("steps"), list)
        else ""
    )
    for pattern in UNSAFE_RESOLUTION_PATTERNS:
        if pattern.search(resolution_steps):
            _error(errors, "resolution.steps", "contains an unsafe command pattern")
            break
    for url in URL_RE.findall(serialized_strings):
        parsed_url = urlsplit(url.rstrip(".,);]"))
        if SENSITIVE_QUERY_KEY_RE.search(f"?{parsed_url.query}"):
            _error(
                errors, "redaction", "contains a URL with a sensitive query parameter"
            )
            break

    return errors


def _load_skill_release_refs(
    registry_path: Path,
) -> tuple[set[tuple[str, str, str]], str | None]:
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return set(), f"{registry_path}: invalid or unreadable Skill registry: {exc}"
    skills = registry.get("skills") if isinstance(registry, dict) else None
    if not isinstance(skills, list):
        return set(), f"{registry_path}: Skill registry must contain a skills array"
    releases: set[tuple[str, str, str]] = set()
    for skill in skills:
        if not isinstance(skill, dict) or not isinstance(skill.get("name"), str):
            continue
        for release in skill.get("releases", []):
            if not isinstance(release, dict):
                continue
            artifact = release.get("artifact")
            if (
                isinstance(release.get("version"), str)
                and isinstance(artifact, dict)
                and isinstance(artifact.get("sha256"), str)
            ):
                releases.add((skill["name"], release["version"], artifact["sha256"]))
    return releases, None


def _validate_related_skill_references(
    record: Any,
    *,
    known_releases: set[tuple[str, str, str]],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return errors
    relations = record.get("relations")
    skill_refs = (
        relations.get("related_skills") if isinstance(relations, dict) else None
    )
    if not isinstance(skill_refs, list):
        return errors
    for index, skill_ref in enumerate(skill_refs):
        if not isinstance(skill_ref, dict):
            continue
        key = (
            skill_ref.get("name"),
            skill_ref.get("version"),
            skill_ref.get("sha256"),
        )
        if all(isinstance(value, str) for value in key) and key not in known_releases:
            errors.append(
                f"relations.related_skills[{index}]: does not identify an exact "
                "immutable release in shared_skills/registry.json"
            )
    return errors


def validate_repository(
    *,
    records_root: Path = RECORDS_ROOT,
    schema_path: Path = SCHEMA_PATH,
    registry_path: Path = SKILL_REGISTRY_PATH,
) -> list[str]:
    """Validate the schema artifact and every tracked Experience Record."""

    errors: list[str] = []
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{schema_path}: invalid or unreadable JSON Schema: {exc}"]
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{schema_path}: $schema must select JSON Schema Draft 2020-12")
    if schema.get("additionalProperties") is not False:
        errors.append(f"{schema_path}: top-level additionalProperties must be false")

    known_releases, registry_error = _load_skill_release_refs(registry_path)
    if registry_error:
        errors.append(registry_error)
        return errors

    record_paths = sorted(records_root.glob("*/*.json"))
    if not record_paths:
        errors.append(f"{records_root}: no Experience Records found")
        return errors

    seen_ids: dict[str, Path] = {}
    decoded_records: list[tuple[Path, dict[str, Any]]] = []
    for path in record_paths:
        relative_path = path.relative_to(records_root)
        if path.is_symlink() or path.parent.is_symlink():
            errors.append(
                f"{relative_path}: symlinked Experience Records are not allowed"
            )
            continue
        try:
            file_size = path.stat().st_size
        except OSError as exc:
            errors.append(f"{relative_path}: cannot inspect record size: {exc}")
            continue
        if file_size > MAX_RECORD_BYTES:
            errors.append(
                f"{relative_path}: file exceeds the {MAX_RECORD_BYTES}-byte record limit"
            )
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative_path}: invalid or unreadable JSON: {exc}")
            continue
        record_errors = validate_record(record, relative_path=relative_path)
        record_errors.extend(
            _validate_related_skill_references(
                record,
                known_releases=known_releases,
            )
        )
        errors.extend(f"{relative_path}: {error}" for error in record_errors)
        experience_id = (
            record.get("experience_id") if isinstance(record, dict) else None
        )
        if isinstance(record, dict):
            decoded_records.append((relative_path, record))
        if isinstance(experience_id, str):
            if experience_id in seen_ids:
                errors.append(
                    f"{relative_path}: duplicate experience_id also used by "
                    f"{seen_ids[experience_id].relative_to(records_root)}"
                )
            else:
                seen_ids[experience_id] = path
    known_experience_ids = set(seen_ids)
    for relative_path, record in decoded_records:
        relations = record.get("relations")
        if not isinstance(relations, dict):
            continue
        for relation_name in ("related_experiences", "supersedes"):
            values = relations.get(relation_name)
            if not isinstance(values, list):
                continue
            for index, related_id in enumerate(values):
                if (
                    isinstance(related_id, str)
                    and related_id not in known_experience_ids
                ):
                    errors.append(
                        f"{relative_path}: relations.{relation_name}[{index}]: "
                        f"unknown Experience Record {related_id!r}"
                    )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    errors = validate_repository()
    if errors:
        print("Experience Record validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    count = len(list(RECORDS_ROOT.glob("*/*.json")))
    print(f"Experience Protocol v0.1 is valid ({count} record(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
