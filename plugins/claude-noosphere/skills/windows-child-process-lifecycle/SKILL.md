---
name: windows-child-process-lifecycle
description: Prevent and recover orphaned child processes, concurrent writers, and post-timeout output corruption on Windows. Use when a PowerShell harness launches long-running Python, Node, benchmark, model, build, or test processes; when a tool timeout or terminal close may kill only the parent shell; or when output files change after a command was reported terminated.
---

# Windows Child Process Lifecycle

Treat the actual child process tree, not the parent shell result, as the lifecycle authority.

## Before launch

1. Use one foreground process for a single-writer workflow.
2. Give the outer command a timeout longer than the expected child runtime. Prefer a yielded/waitable execution cell for long jobs.
3. Store resumable checkpoints outside the authoritative output directory.
4. Write authoritative outputs only after full validation; keep partial results in checkpoints.
5. Bind checkpoints to code/config/freeze hashes so changed implementations cannot silently reuse stale rows.

## After timeout, cancellation, or terminal loss

1. Do not immediately relaunch.
2. Query `Win32_Process` by the distinctive command line and inspect PID, parent PID, creation time, CPU time, and working set.
3. Exclude the current diagnostic PowerShell process from matches.
4. If a child remains, declare it the sole writer and monitor it read-only. Do not start another writer.
5. Check progress through structural metadata only: checkpoint modification time, file size, unique successful identity count, and freeze hash. Avoid printing payloads or secrets.
6. Let a healthy child finish naturally when safe. If termination is necessary, terminate the verified child process tree and confirm every descendant is gone before relaunching.

## Recovery and integrity

1. Detect authoritative-file writes that occurred after the parent command ended.
2. Compare generation timestamps, history backups, freeze hashes, and outcome counts to identify concurrent overwrite.
3. Reject mixed or stale checkpoints whose execution freeze differs from the current code/config freeze.
4. For append-only retry logs, freeze the first successful record per identity. Do not let later stochastic retries replace an established success unless the protocol explicitly pre-registers another rule.
5. If concurrent writers touched the same latest view, discard that execution as clean-run evidence. Run once under a new freeze with one writer.

## Completion standard

- Exactly one intended writer ran for the accepted execution freeze.
- The accepted run reports complete unique identity coverage and zero failed required identities.
- No matching child process remains.
- Checkpoint and authoritative output hashes are consistent.
- Data/index/claim gates run after the final writer exits.
- The incident and clean-run replacement are recorded without secrets or raw model content.

## Common false conclusions

- A parent PowerShell timeout does not prove the Python child stopped.
- A command cell marked terminated does not prove descendants were killed.
- A valid API key metadata response does not prove a requested model is callable.
- A growing append-only row count does not equal unique completed identities.
- A latest file that passes schema validation may still have been overwritten by a second valid-but-concurrent run.
