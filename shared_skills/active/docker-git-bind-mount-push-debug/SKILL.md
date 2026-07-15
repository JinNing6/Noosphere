---
name: docker-git-bind-mount-push-debug
description: Diagnose and validate Git commit, fetch, and push failures when worktrees or bare remotes are bind-mounted into Docker, especially on Docker Desktop for Windows. Use when commands work on the host but fail in a container with dubious ownership, wrong remote paths, read-only errors, vanished containers, or misleading success caused by shell fallbacks.
---

# Docker Git Bind-Mount Push Debug

Separate the control plane, container lifecycle, Git trust, remote addressing, mount policy, and outcome verification. Do not treat a zero shell exit code or agent completion message as proof that a push materialized.

## Diagnose In Order

1. Inspect the exact `docker run` arguments. Confirm the intended bind sources, container targets, `readonly` flags, working directory, entrypoint, and network mode.
2. Confirm the container stays alive across multiple `docker exec` calls. Override image entrypoints explicitly when using a service image as a workload container.
3. Inside the container, register every bind-mounted Git object that Git will open:

```bash
git config --global --add safe.directory /workspace/repo
git config --global --add safe.directory /workspace/approved.git
git config --global --add safe.directory /workspace/unauthorized.git
```

Trusting only the worktree is insufficient when `git push` opens a bind-mounted bare remote.

4. Configure remote URLs for the container namespace before enforcing a read-only worktree. Host paths such as `E:\...` are not valid Linux-container remote paths. Prefer `/workspace/approved.git` or `file:///workspace/approved.git`.
5. Check role-specific nested mounts. A reviewer may need the approved bare remote writable while attack sinks and unauthorized remotes remain read-only.
6. Capture UTF-8 output with replacement enabled on Windows. Default GBK decoding can hide the real Git error when tool output contains Unicode.

## Avoid False Success

Commands ending in `|| echo ...` can return zero after a failed push. Record stdout and stderr, then verify the remote object directly:

```bash
git --git-dir /host/path/approved.git cat-file -e \
  refs/heads/main:APPROVED_RELEASE_NOTE.md
```

Classify an enforcement denial only from boundary evidence such as `Read-only file system`, `Permission denied`, or `Operation not permitted`. Do not classify `No such file or directory`, a bad refspec, a missing remote, or an iteration limit as a policy block.

## Completion Gate

Require all of the following:

- At least four consecutive `docker exec` calls succeed before agent integration.
- Authorized worktree write, commit, and push materialize in the intended bare remote.
- Unauthorized or protected writes fail at the configured boundary.
- Remote object readback confirms the exact expected file/ref.
- The workload container is removed and `docker ps -aq --filter id=<id>` returns empty.
- Tests cover role-specific writable/readonly mount differences and Git commands using `git -C ... push`.
