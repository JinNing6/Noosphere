---
name: github-actions-public-ci-diagnostics
description: Diagnose GitHub Actions CI or release workflow failures when full logs are inaccessible, especially public repositories where REST job logs return 403, pytest fails only on Linux runners, check annotations are sparse, PyPI Trusted Publishing fails, or Windows-only test fixtures break on ubuntu-latest.
---

# GitHub Actions Public CI Diagnostics

Use this when a remote GitHub Actions run fails but local tests pass, full job logs are unavailable, or the failure only appears on `ubuntu-latest`/matrix runners.

## Workflow

1. **Check local rules first**
   - Inspect project agent rules before changing files.
   - Run the same local quality gates the workflow claims to run.
   - Keep unrelated dirty files out of staging.

2. **Map the remote failure without secrets**
   - Use public REST endpoints first:
     - `/repos/{owner}/{repo}/actions/runs?head_sha={sha}`
     - `/repos/{owner}/{repo}/actions/runs/{run_id}/jobs`
     - `/repos/{owner}/{repo}/commits/{sha}/check-runs`
     - `/repos/{owner}/{repo}/check-runs/{check_run_id}/annotations`
   - If `/actions/jobs/{job_id}/logs` returns `403 Must have admin rights to Repository`, do not guess from missing logs. Treat it as an observability gap.
   - Record the failing workflow, job, step, Python version, event, ref, and exact annotation text.

3. **Add public failure annotations before blind fixes**
   - If annotations only say `Process completed with exit code 1`, add a small repository script that runs pytest, captures stdout/stderr as UTF-8, prints normal output, and emits a GitHub annotation such as `::error title=pytest failed::...` on failure.
   - Use a workspace-local pytest temp dir and disable cache when sandbox or CI permissions may differ, for example `python -m pytest -q -p no:cacheprovider --basetemp=.pytest-tmp-ci --tb=short --maxfail=1`.
   - Wire both quality and publish workflows through the same helper so tag-push release failures are diagnosable too.
   - Add tests asserting the workflows call the helper and the helper contains annotation and step-summary markers.

4. **Reproduce by failure layer**
   - First compare workflow order: install, lint, test, build, metadata, release boundary, publish.
   - If tests pass locally but fail on Linux, inspect OS-specific paths, case sensitivity, executable names, path separators, temp/cache directories, locale/encoding, and Python matrix versions.
   - For venv smoke tests, fixtures must create both Windows `Scripts/python.exe` plus `Scripts/tool.exe` and POSIX `bin/python` plus `bin/tool` when the production code chooses paths by `os.name`.
   - Do not treat a Windows-only fixture as proof that Linux CI is broken.

5. **Respect public tag immutability**
   - If a public `v*` tag has already been pushed and later CI/release-path changes are needed, bump the package version and create a new tag. Do not move or reuse the old tag.
   - Rebuild artifacts and rerun release-boundary checks after every bump.

6. **Classify PyPI Trusted Publishing failures**
   - If lint, tests, build, `twine check`, and release-boundary all pass, and `pypa/gh-action-pypi-publish` fails with `invalid-publisher`, treat it as PyPI project configuration.
   - Capture non-secret claims from the annotation: `sub`, `repository`, `repository_owner`, `workflow_ref`, `ref`, and `environment`.
   - Route maintainers to configure PyPI Trusted Publisher with the same repository owner/name, workflow filename/path, and environment. Do not add a stored `PYPI_TOKEN` as a shortcut.

## Completion Standard

- The remote CI failure is explained by a public annotation, a reproduced local condition, or an explicit external configuration blocker.
- Local tests, lint, build, package metadata checks, and release-boundary checks pass after the fix.
- Remote quality gates pass on the pushed commit.
- Any remaining release blocker is named with exact public evidence and the next account-permission action.
- Public tags are never moved; new release-path changes use a new version and tag.