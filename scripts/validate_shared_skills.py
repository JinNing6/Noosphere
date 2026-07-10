#!/usr/bin/env python
"""Validate Noosphere plugin Skills and the versioned shared Skill registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


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
    if not NAME_RE.fullmatch(expected_name):
        errors.append(f"Invalid expected Skill name: {expected_name}")
    if name != expected_name:
        errors.append(
            f"Skill frontmatter name {name!r} does not match parent directory {expected_name!r}: {path}"
        )
    if not description or len(description) > 1024:
        errors.append(f"Skill description must contain 1-1024 characters: {path}")
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
            data = artifact_path.read_bytes()
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
                elif (
                    release_path.is_file()
                    and active_path.read_bytes() != release_path.read_bytes()
                ):
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


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    registry_path = root / "shared_skills" / "registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot read shared Skill registry: {exc}"]
    errors.extend(validate_registry(root, registry))
    for plugin_root in [
        root / "plugins" / "noosphere" / "skills",
        root / "plugins" / "claude-noosphere" / "skills",
    ]:
        for skill_dir in sorted(plugin_root.iterdir()):
            if skill_dir.is_dir():
                errors.extend(
                    validate_skill_file(skill_dir / "SKILL.md", skill_dir.name)
                )
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
