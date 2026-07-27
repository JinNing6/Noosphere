"""Pure validation and version-selection logic for shared Skill artifacts."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import Any

_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def validate_skill_name(name: str) -> bool:
    """Return whether *name* is a safe Agent Skills-compatible identifier."""
    return bool(isinstance(name, str) and 1 <= len(name) <= 64 and _SKILL_NAME_RE.fullmatch(name))


def _find_skill(registry: Mapping[str, Any], skill_name: str) -> Mapping[str, Any]:
    if not validate_skill_name(skill_name):
        raise ValueError("Invalid Skill name")

    skills = registry.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("Invalid shared Skill registry")

    for skill in skills:
        if isinstance(skill, Mapping) and skill.get("name") == skill_name:
            return skill
    raise KeyError(f"Unknown shared Skill: {skill_name}")


def select_skill_release(
    registry: Mapping[str, Any],
    skill_name: str,
    version: str | None = None,
) -> Mapping[str, Any]:
    """Select an active, registry-whitelisted release for a shared Skill."""
    skill = _find_skill(registry, skill_name)
    selected_version = version or skill.get("latest")
    releases = skill.get("releases", [])
    if not isinstance(selected_version, str) or not isinstance(releases, list):
        raise ValueError(f"Invalid registry entry for {skill_name}")

    for release in releases:
        if not isinstance(release, Mapping) or release.get("version") != selected_version:
            continue
        if release.get("status") != "active":
            raise ValueError(f"Shared Skill {skill_name}@{selected_version} is not active")
        artifact = release.get("artifact")
        if not isinstance(artifact, Mapping):
            raise ValueError(f"Missing artifact for {skill_name}@{selected_version}")
        if not _VERSION_RE.fullmatch(selected_version):
            raise ValueError(f"Invalid release version for {skill_name}")
        expected_path = f"shared_skills/releases/{selected_version}/{skill_name}/SKILL.md"
        if artifact.get("path") != expected_path:
            raise ValueError(f"Invalid artifact path for {skill_name}@{selected_version}")
        return release
    raise KeyError(f"Unknown shared Skill release: {skill_name}@{selected_version}")


def verify_skill_artifact(content: str, release: Mapping[str, Any]) -> bool:
    """Verify the exact UTF-8 artifact bytes against registry metadata."""
    artifact = release.get("artifact")
    if not isinstance(content, str) or not isinstance(artifact, Mapping):
        return False
    expected_sha = artifact.get("sha256")
    expected_size = artifact.get("size_bytes")
    if not isinstance(expected_sha, str) or not isinstance(expected_size, int):
        return False

    encoded = content.encode("utf-8")
    return len(encoded) == expected_size and hashlib.sha256(encoded).hexdigest() == expected_sha.lower()


def summarize_release_usage(release: Mapping[str, Any]) -> dict[str, Any]:
    """Return the reviewed Outcome count for one immutable Skill release.

    This is deliberately a lower-bound metric. Noosphere does not silently
    track discovery, downloads, or unreported executions; only trusted-review
    Outcome records are counted.
    """
    verification = release.get("verification", {})
    if not isinstance(verification, Mapping):
        raise ValueError("Invalid shared Skill verification metadata")

    def _counter(name: str) -> int:
        value = verification.get(name, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid shared Skill Outcome counter: {name}")
        return value

    successful = _counter("verified_outcomes")
    non_successful = _counter("failed_outcomes")
    return {
        "reported_usage_count": successful + non_successful,
        "successful_usage_count": successful,
        "non_successful_usage_count": non_successful,
        "counting_basis": "approved-outcome-reports",
        "lower_bound": True,
    }


def summarize_skill_usage(skill: Mapping[str, Any]) -> dict[str, Any]:
    """Aggregate reviewed Outcome counts across every immutable release."""
    releases = skill.get("releases", [])
    if not isinstance(releases, list):
        raise ValueError("Invalid shared Skill releases metadata")

    usage = {
        "reported_usage_count": 0,
        "successful_usage_count": 0,
        "non_successful_usage_count": 0,
        "counting_basis": "approved-outcome-reports",
        "lower_bound": True,
    }
    for release in releases:
        if not isinstance(release, Mapping):
            raise ValueError("Invalid shared Skill release metadata")
        release_usage = summarize_release_usage(release)
        for field in (
            "reported_usage_count",
            "successful_usage_count",
            "non_successful_usage_count",
        ):
            usage[field] += release_usage[field]
    return usage


def is_release_originator(
    skill: Mapping[str, Any],
    release: Mapping[str, Any],
    github_login: str,
) -> bool:
    """Return whether an authenticated GitHub login contributed this release."""
    login = github_login.strip().casefold()
    if not login:
        return False

    identities: list[Any] = []
    originators = skill.get("originators", [])
    if isinstance(originators, list):
        identities.extend(originators)

    provenance = release.get("provenance", {})
    if isinstance(provenance, Mapping):
        author = provenance.get("author")
        if author:
            identities.append(author)
        authors = provenance.get("authors", [])
        if isinstance(authors, list):
            identities.extend(authors)

    return any(isinstance(identity, str) and identity.strip().casefold() == login for identity in identities)


def check_installed_skill_versions(
    registry: Mapping[str, Any],
    installed_versions: Mapping[str, str],
) -> dict[str, dict[str, Any]]:
    """Compare installed version or digest identifiers with the active registry."""
    if not isinstance(installed_versions, Mapping):
        raise ValueError("installed_versions must be an object")

    results: dict[str, dict[str, Any]] = {}
    registry_names: set[str] = set()
    for skill in registry.get("skills", []):
        if not isinstance(skill, Mapping):
            continue
        name = skill.get("name")
        latest = skill.get("latest")
        if not isinstance(name, str) or not validate_skill_name(name):
            continue
        registry_names.add(name)
        installed = installed_versions.get(name)
        try:
            release = select_skill_release(registry, name)
        except (KeyError, ValueError):
            if installed is not None:
                results[name] = {
                    "status": "retired",
                    "installed": installed,
                    "latest": None,
                    "sha256": None,
                }
            continue

        artifact = release["artifact"]
        digest = artifact["sha256"]
        if installed is None:
            status = "available"
        elif installed in {latest, digest}:
            status = "current"
        else:
            status = "update-available"
        results[name] = {
            "status": status,
            "installed": installed,
            "latest": latest,
            "sha256": digest,
        }

    for name, installed in installed_versions.items():
        if name not in registry_names:
            results[name] = {
                "status": "unregistered",
                "installed": installed,
                "latest": None,
                "sha256": None,
            }
    return results
