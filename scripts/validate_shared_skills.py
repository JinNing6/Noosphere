#!/usr/bin/env python
"""Validate the versioned Noosphere Skill registry and Agent plugins."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
VERIFICATION_LEVELS = {
    "maintainer-validated",
    "independently-reproduced",
    "outcome-proven",
    "established",
}


def _canonical_artifact_bytes(path: Path) -> bytes:
    """Return the LF-normalized bytes stored by Git for text Skill artifacts."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    if value.startswith('"'):
        try:
            return str(json.loads(value))
        except json.JSONDecodeError:
            return ""
    return value


def validate_skill_file(path: Path, expected_name: str) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"Missing Skill artifact: {path}"]
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"Skill artifact is not UTF-8: {path}"]
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        return [f"Skill artifact has invalid YAML frontmatter: {path}"]
    frontmatter = content.split("\n---\n", 1)[0][4:]
    name = _frontmatter_value(frontmatter, "name")
    description = _frontmatter_value(frontmatter, "description")
    if len(expected_name) > 64 or not NAME_RE.fullmatch(expected_name):
        errors.append(f"Invalid expected Skill name: {expected_name}")
    if name != expected_name:
        errors.append(
            f"Skill frontmatter name {name!r} does not match parent directory {expected_name!r}: {path}"
        )
    if not description or len(description) > 1024:
        errors.append(f"Skill description must contain 1-1024 characters: {path}")
    if re.search(r"[A-Za-z]:\\+Users\\+", content):
        errors.append(f"Skill artifact contains a private Windows user path: {path}")
    return errors


def validate_registry(root: Path, registry: dict) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != "1.0":
        errors.append("Registry schema_version must be 1.0")
    skills = registry.get("skills")
    if not isinstance(skills, list):
        return [*errors, "Registry skills must be an array"]

    names: set[str] = set()
    registered_paths: set[str] = set()
    for skill in skills:
        if not isinstance(skill, dict):
            errors.append("Registry Skill entries must be objects")
            continue
        name = skill.get("name")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            errors.append(f"Invalid registry Skill name: {name!r}")
            continue
        if name in names:
            errors.append(f"Duplicate registry Skill name: {name}")
        names.add(name)
        releases = skill.get("releases")
        if not isinstance(releases, list) or not releases:
            errors.append(f"Registry Skill has no releases: {name}")
            continue

        versions: set[str] = set()
        release_by_version: dict[str, dict] = {}
        for release in releases:
            version = release.get("version") if isinstance(release, dict) else None
            if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
                errors.append(f"Invalid release version for {name}: {version!r}")
                continue
            if version in versions:
                errors.append(f"Duplicate release version: {name}@{version}")
            versions.add(version)
            release_by_version[version] = release
            status = release.get("status")
            if status not in {"active", "withdrawn"}:
                errors.append(f"Invalid release status: {name}@{version}")
            if status == "withdrawn" and not isinstance(
                release.get("withdrawal"), dict
            ):
                errors.append(
                    f"Withdrawn release lacks audit metadata: {name}@{version}"
                )

            verification = release.get("verification")
            level = (
                verification.get("level") if isinstance(verification, dict) else None
            )
            if level not in VERIFICATION_LEVELS:
                errors.append(f"Invalid verification level: {name}@{version}")
            if level in {
                "independently-reproduced",
                "outcome-proven",
                "established",
            } and (
                int(release.get("source_count") or 0) < 2
                or int(release.get("publisher_count") or 0) < 2
                or int(verification.get("independent_reproductions") or 0) < 2
            ):
                errors.append(
                    f"Independently verified release lacks source reproduction: {name}@{version}"
                )
            if not isinstance(release.get("provenance"), dict):
                errors.append(f"Release lacks provenance metadata: {name}@{version}")

            artifact = release.get("artifact")
            expected = f"shared_skills/releases/{version}/{name}/SKILL.md"
            if not isinstance(artifact, dict) or artifact.get("path") != expected:
                errors.append(f"Non-canonical artifact path: {name}@{version}")
                continue
            registered_paths.add(expected)
            artifact_path = root / expected
            errors.extend(validate_skill_file(artifact_path, name))
            if not artifact_path.is_file():
                continue
            data = _canonical_artifact_bytes(artifact_path)
            if hashlib.sha256(data).hexdigest() != artifact.get("sha256"):
                errors.append(f"Artifact SHA-256 mismatch: {name}@{version}")
            if len(data) != artifact.get("size_bytes"):
                errors.append(f"Artifact byte-size mismatch: {name}@{version}")

        latest = skill.get("latest")
        if latest is not None:
            latest_release = release_by_version.get(latest)
            if not latest_release or latest_release.get("status") != "active":
                errors.append(f"latest does not reference an active release: {name}")
            else:
                release_path = root / latest_release["artifact"]["path"]
                active_path = root / f"shared_skills/active/{name}/SKILL.md"
                if not active_path.is_file():
                    errors.append(f"Missing active Skill mirror: {name}")
                elif release_path.is_file() and _canonical_artifact_bytes(
                    active_path
                ) != _canonical_artifact_bytes(release_path):
                    errors.append(f"Active Skill mirror drift: {name}")
        else:
            if any(release.get("status") == "active" for release in releases):
                errors.append(f"Skill with active releases must declare latest: {name}")
            active_path = root / f"shared_skills/active/{name}/SKILL.md"
            if active_path.exists():
                errors.append(f"Withdrawn-only Skill retains an active mirror: {name}")

    releases_root = root / "shared_skills" / "releases"
    if releases_root.exists():
        for artifact_path in releases_root.glob("*/*/SKILL.md"):
            relative = artifact_path.relative_to(root).as_posix()
            if relative not in registered_paths:
                errors.append(f"Unregistered Skill artifact: {relative}")
    return errors


def validate_outcomes(registry: dict, ledger: dict) -> list[str]:
    errors: list[str] = []
    if ledger.get("schema_version") != "1.0" or not isinstance(
        ledger.get("outcomes"), list
    ):
        return ["Outcome ledger must use schema version 1.0 and an outcomes array"]
    releases = {
        (
            skill.get("name"),
            release.get("version"),
            release.get("artifact", {}).get("sha256"),
        ): (
            skill,
            release,
        )
        for skill in registry.get("skills", [])
        for release in skill.get("releases", [])
    }
    seen: set[str] = set()
    grouped: dict[tuple[str, str, str], list[dict]] = {}
    for outcome in ledger["outcomes"]:
        if not isinstance(outcome, dict):
            errors.append("Outcome ledger entries must be objects")
            continue
        outcome_id = outcome.get("outcome_id")
        if not isinstance(outcome_id, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", outcome_id
        ):
            errors.append(f"Invalid outcome_id: {outcome_id!r}")
            continue
        if outcome_id in seen:
            errors.append(f"Duplicate outcome_id: {outcome_id}")
        seen.add(outcome_id)
        key = (
            outcome.get("skill_name"),
            outcome.get("skill_version"),
            outcome.get("skill_sha256"),
        )
        if key not in releases:
            errors.append(
                f"Outcome references an unknown immutable release: {outcome_id}"
            )
        grouped.setdefault(key, []).append(outcome)
        if outcome.get("outcome") not in {"success", "partial", "failure"}:
            errors.append(f"Invalid outcome value: {outcome_id}")
        for field in (
            "reporter",
            "approved_by",
            "approved_at",
            "task_summary",
            "verification_summary",
        ):
            if not isinstance(outcome.get(field), str) or not outcome[field].strip():
                errors.append(f"Outcome {outcome_id} lacks {field}")
        if (
            not isinstance(outcome.get("issue_number"), int)
            or outcome["issue_number"] <= 0
        ):
            errors.append(f"Outcome {outcome_id} lacks a valid issue_number")
        issue_url = outcome.get("issue_url")
        if not isinstance(issue_url, str) or not issue_url.strip():
            errors.append(f"Outcome {outcome_id} lacks issue_url")
        evidence_urls = outcome.get("evidence_urls")
        if not isinstance(evidence_urls, list):
            errors.append(f"Outcome {outcome_id} evidence_urls must be an array")
            evidence_urls = []
        for value in [issue_url, *evidence_urls]:
            parsed = urlsplit(str(value))
            sensitive_query = any(
                re.search(
                    r"(?:token|secret|signature|credential|auth|api[_-]?key)",
                    key,
                    re.IGNORECASE,
                )
                for key, _ in parse_qsl(parsed.query, keep_blank_values=True)
            )
            if (
                parsed.scheme != "https"
                or not parsed.netloc
                or parsed.username
                or parsed.password
                or sensitive_query
            ):
                errors.append(f"Outcome {outcome_id} has a non-public evidence URL")

    for key, (skill, release) in releases.items():
        outcomes = grouped.get(key, [])
        successes = [item for item in outcomes if item.get("outcome") == "success"]
        failures = [item for item in outcomes if item.get("outcome") != "success"]
        verification = release.get("verification", {})
        if int(verification.get("verified_outcomes") or 0) != len(successes):
            errors.append(
                f"Outcome success count drift: {skill['name']}@{release['version']}"
            )
        if int(verification.get("failed_outcomes") or 0) != len(failures):
            errors.append(
                f"Outcome failure count drift: {skill['name']}@{release['version']}"
            )
        if bool(verification.get("update_needed")) != bool(failures):
            errors.append(
                f"Outcome update-needed drift: {skill['name']}@{release['version']}"
            )
        if verification.get("level") in {"outcome-proven", "established"}:
            authors = {
                str(value).lower()
                for value in [
                    *(skill.get("originators") or []),
                    *(release.get("provenance", {}).get("authors") or []),
                    release.get("provenance", {}).get("author"),
                ]
                if value
            }
            if not any(
                str(item.get("reporter", "")).lower() not in authors
                and bool(item.get("evidence_urls"))
                for item in successes
            ):
                errors.append(
                    "Outcome-proven release lacks independent success with public evidence: "
                    f"{skill['name']}@{release['version']}"
                )
    return errors


def validate_plugin_bootstrap(root: Path) -> list[str]:
    """Allow one shared control Skill while rejecting bundled dynamic artifacts."""
    errors: list[str] = []
    plugin_roots = [
        root / "plugins" / "noosphere",
        root / "plugins" / "claude-noosphere",
    ]
    control_paths: list[Path] = []
    for plugin_root in plugin_roots:
        skills_root = plugin_root / "skills"
        discovered = (
            {path.parent.name for path in skills_root.glob("*/SKILL.md")}
            if skills_root.is_dir()
            else set()
        )
        unexpected = sorted(discovered - {"using-noosphere"})
        if unexpected:
            errors.append(
                "Plugin must not bundle dynamic Skill copies: "
                f"{plugin_root}: {', '.join(unexpected)}"
            )
        control_path = skills_root / "using-noosphere" / "SKILL.md"
        control_paths.append(control_path)
        errors.extend(validate_skill_file(control_path, "using-noosphere"))

    if all(path.is_file() for path in control_paths) and (
        _canonical_artifact_bytes(control_paths[0])
        != _canonical_artifact_bytes(control_paths[1])
    ):
        errors.append("Codex and Claude Code control Skill drift")

    codex_metadata = (
        root
        / "plugins"
        / "noosphere"
        / "skills"
        / "using-noosphere"
        / "agents"
        / "openai.yaml"
    )
    try:
        metadata = codex_metadata.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Cannot read Codex control Skill metadata: {exc}")
    else:
        if not re.search(r"allow_implicit_invocation:\s*true\b", metadata):
            errors.append("Codex control Skill must allow implicit invocation")

    manifest_contracts = [
        (
            root / "plugins" / "noosphere" / ".codex-plugin" / "plugin.json",
            {"skills": "./skills/"},
        ),
        (
            root / "plugins" / "claude-noosphere" / ".claude-plugin" / "plugin.json",
            {"skills": "./skills/", "hooks": "./hooks/hooks.json"},
        ),
    ]
    for manifest_path, expected in manifest_contracts:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(
                f"Cannot parse plugin bootstrap manifest {manifest_path}: {exc}"
            )
            continue
        for field, value in expected.items():
            if manifest.get(field) != value:
                errors.append(
                    f"Plugin bootstrap manifest must set {field}={value!r}: "
                    f"{manifest_path}"
                )

    hook_path = root / "plugins" / "claude-noosphere" / "hooks" / "hooks.json"
    script_path = (
        root
        / "plugins"
        / "claude-noosphere"
        / "scripts"
        / "noosphere-session-start.cjs"
    )
    for path in (hook_path, script_path):
        if not path.is_file():
            errors.append(f"Missing Claude Code automatic bootstrap artifact: {path}")
    return errors


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    registry_path = root / "shared_skills" / "registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot read shared Skill registry: {exc}"]
    errors.extend(validate_registry(root, registry))
    outcomes_path = root / "shared_skills" / "outcomes.json"
    try:
        outcomes = json.loads(outcomes_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot read shared Skill outcome ledger: {exc}")
    else:
        errors.extend(validate_outcomes(registry, outcomes))
    errors.extend(validate_plugin_bootstrap(root))
    manifest_paths = [
        root / "plugins" / "noosphere" / ".codex-plugin" / "plugin.json",
        root / "plugins" / "claude-noosphere" / ".claude-plugin" / "plugin.json",
        root / ".claude-plugin" / "marketplace.json",
    ]
    if all(path.is_file() for path in manifest_paths):
        try:
            manifests = [
                json.loads(path.read_text(encoding="utf-8")) for path in manifest_paths
            ]
        except json.JSONDecodeError as exc:
            return [*errors, f"Cannot parse plugin manifest: {exc}"]
        versions = {
            manifests[0].get("version"),
            manifests[1].get("version"),
            manifests[2].get("version"),
            manifests[2].get("plugins", [{}])[0].get("version"),
        }
        if len(versions) != 1:
            errors.append(
                f"Plugin manifest versions diverge: {sorted(str(value) for value in versions)}"
            )
        sdk_init = root / "sdk" / "noosphere" / "__init__.py"
        try:
            sdk_init_text = sdk_init.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"Cannot read SDK version metadata: {exc}")
        else:
            sdk_version_match = re.search(
                r'^__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
                sdk_init_text,
                re.MULTILINE,
            )
            if not sdk_version_match:
                errors.append("Cannot parse SDK version metadata")
            elif versions != {sdk_version_match.group(1)}:
                errors.append(
                    "Plugin manifests must match the public SDK version: "
                    f"sdk={sdk_version_match.group(1)}, "
                    f"plugins={sorted(str(value) for value in versions)}"
                )

        active_skill_count = sum(
            1
            for skill in registry.get("skills", [])
            if isinstance(skill, dict) and skill.get("latest")
        )
        codex_description = manifests[0].get("interface", {}).get("longDescription", "")
        expected_description = f"Discover {active_skill_count} versioned"
        if expected_description not in codex_description:
            errors.append(
                f"Codex plugin Skill count drift: expected `{expected_description}`"
            )

        count_copy = [
            (
                root / "plugins" / "noosphere" / "README.md",
                f"containing {active_skill_count} Agent Skills",
            ),
            (
                root / "plugins" / "claude-noosphere" / "README.md",
                f"containing {active_skill_count} Agent Skills",
            ),
            (
                root / "plugins" / "claude-noosphere" / "SUBMISSION.md",
                f"discover {active_skill_count} versioned foundational Skills",
            ),
        ]
        for path, expected in count_copy:
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"Cannot read plugin launch metadata {path}: {exc}")
                continue
            if expected not in text:
                errors.append(
                    f"Plugin Skill count drift in {path}: expected `{expected}`"
                )
    codex_mcp_path = root / "plugins" / "noosphere" / ".mcp.json"
    try:
        codex_mcp = json.loads(codex_mcp_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot parse Codex plugin MCP configuration: {exc}")
    else:
        if set(codex_mcp) != {"mcpServers"}:
            errors.append(
                "Codex plugin .mcp.json must contain only the current `mcpServers` field"
            )
        elif not isinstance(codex_mcp["mcpServers"].get("noosphere"), dict):
            errors.append("Codex plugin .mcp.json is missing the noosphere server")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args(argv)
    errors = validate_repository(args.root.resolve())
    if errors:
        print("Shared Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Shared Skill registry and plugin artifacts are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
