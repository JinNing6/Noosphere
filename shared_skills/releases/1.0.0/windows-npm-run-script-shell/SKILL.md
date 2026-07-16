---
name: windows-npm-run-script-shell
description: Use when Windows npm run, npm test, npm run build, or npm run-script exits before running the script with ERR_INVALID_ARG_TYPE, "file argument must be of type string", missing ComSpec, broken script-shell, stripped CLI flags, sandboxed npm cache/log EPERM, or silent npm script output.
---

# Windows Npm Run Script Shell

## Overview

Windows npm scripts need a shell. If `ComSpec` is missing or npm cannot infer a script shell, `npm run ...` can fail inside npm before `tsc`, Vite, Vitest, or Playwright actually runs.

## Triage

Use this flow before changing app code:

1. Run the target tool directly with `npx`, for example `npx tsc -b --pretty false`, `npx vite build`, or `npx vitest run`.
2. Run `npm run <script> --loglevel verbose`.
3. Open the npm debug log if output is empty.
4. Check shell config:

```powershell
npm config get script-shell
npm config get cache
npm config get update-notifier
Write-Host "ComSpec=[$env:ComSpec]"
Write-Host "SHELL=[$env:SHELL]"
```

If direct `npx` commands pass but `npm run` fails with `ERR_INVALID_ARG_TYPE: The "file" argument must be of type string. Received undefined`, treat it as npm shell configuration, not a project build failure.

If direct `node <script>` succeeds but `npm test`/`npm run` exits silently in a sandbox, rerun with `--loglevel verbose`. When npm reports `EPERM` creating `%LocalAppData%\npm-cache\_logs` or attempts registry access only for update checks, treat it as npm runtime side effects, not a test failure.

## Fix

Prefer a project-local `.npmrc` so the fix travels with the repo:

```ini
script-shell=C:\Windows\System32\cmd.exe
```

For sandboxed Windows workspaces where npm cannot write the user cache/log directory, keep npm side effects inside the repo and disable network-prone notices:

```ini
cache=.npm-cache
update-notifier=false
fund=false
audit=false
script-shell=cmd.exe
```

Then rerun:

```powershell
npm run build
npm test -- --run
```

If the project requires PowerShell syntax in scripts, set `script-shell` to PowerShell and avoid `&&` in package scripts, because Windows PowerShell 5 does not support `&&`.

## Common Mistakes

- Do not rewrite TypeScript, Vite, Vitest, or React code when `npx <tool>` succeeds and only `npm run` fails.
- Do not treat silent npm output as proof that the build tool produced no diagnostics; inspect the npm debug log.
- Do not ignore npm cache/log `EPERM` in sandboxed workspaces; set a project-local cache before escalating.
- Do not set a global npm config unless the user asked for machine-wide changes.
- Do not assume `SHELL` replaces `ComSpec` for npm on Windows.

## Completion Standard

The issue is fixed only when:

- The original `npm run <script>` command succeeds.
- The direct tool command still succeeds.
- Tests/builds that previously passed via `npx` also pass through npm scripts.
