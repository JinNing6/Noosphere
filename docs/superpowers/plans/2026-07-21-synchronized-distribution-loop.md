# Synchronized Distribution Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a claim-bounded evidence packet and operating loop that turns each verified Noosphere event into coordinated, channel-native distribution and routes real use back into Outcomes.

**Architecture:** GitHub remains the canonical evidence and conversion surface. One wave document holds the fact set, platform-specific variants, execution ledger, and measurement checkpoints; launch documents point to that operating loop, and a repository test prevents trust or status drift.

**Tech Stack:** Markdown, Python 3 `unittest`, GitHub Issues/traffic API, existing Noosphere launch assets.

---

### Task 1: Lock the first-wave truth contract

**Files:**
- Modify: `scripts/test_launch_surface.py`
- Create: `docs/distribution-waves/live-skill-proof-20260721.md`

- [x] **Step 1: Add the failing distribution-wave test**

Add this test to `LaunchSurfaceTests`:

```python
def test_first_distribution_wave_preserves_proof_and_channel_boundaries(self):
    wave = (
        REPO_ROOT / "docs" / "distribution-waves" / "live-skill-proof-20260721.md"
    ).read_text(encoding="utf-8")

    for required in (
        "okflint==0.3.0",
        "okflint==0.3.1",
        "https://github.com/JinNing6/Noosphere/issues/57",
        "https://github.com/TSchonleber/brainctl/pull/170",
        "https://github.com/guardiatechnology/ahrena/pull/376",
        "maintainer-validated",
        "Weekly External Verified Reuses",
        "X / LinkedIn",
        "Show HN",
        "Reddit",
        "V2EX",
        "掘金 / DEV",
        "24-hour",
        "72-hour",
    ):
        self.assertIn(required, wave)

    self.assertNotIn("independently validated", wave)
    self.assertNotIn("CI passed", wave)
```

- [x] **Step 2: Run the test and verify it fails**

Run:

```powershell
python -m unittest scripts.test_launch_surface.LaunchSurfaceTests.test_first_distribution_wave_preserves_proof_and_channel_boundaries -v
```

Expected: `ERROR` because the wave document does not exist.

- [x] **Step 3: Create the canonical evidence packet**

Create `docs/distribution-waves/live-skill-proof-20260721.md` with:

- campaign ID `live-skill-proof-20260721`;
- the one-pattern/three-project hook;
- exact okflint, brainctl, and Ahrena evidence and claim boundaries;
- one install CTA;
- native copy for X/LinkedIn, Reddit, V2EX, and 掘金/DEV;
- a fact-only Show HN outline that requires the maintainer's own writing;
- a public URL ledger and 24-/72-hour evidence checkpoints.

- [x] **Step 4: Run the focused test and verify it passes**

Run the command from Step 2.

Expected: one test passes.

### Task 2: Replace the one-off launch sequence with an operating loop

**Files:**
- Modify: `docs/launch-pack.md`
- Modify: `docs/launch-copy.md`

- [x] **Step 1: Update the launch pack**

Add a `Synchronized Distribution Loop` section defining:

```text
verified event -> evidence packet -> channel-native wave -> install/use -> Outcome -> next event
```

State that active issue search is a cold-start proof method, identical cross-posting is prohibited, and the first wave is `docs/distribution-waves/live-skill-proof-20260721.md`.

- [x] **Step 2: Update the launch copy index**

Add the current proof wave hook and link. Preserve the existing v0.9.0 launch copy as a historical release asset and require future posts to use current facts from the wave packet.

- [x] **Step 3: Verify the launch documents**

Run:

```powershell
rg -n "Synchronized Distribution Loop|live-skill-proof-20260721|cold-start|channel-native" docs/launch-pack.md docs/launch-copy.md
```

Expected: all four concepts appear in the launch documents.

### Task 3: Synchronize project memory

**Files:**
- Modify: `docs/project-memory-snapshot.md`

- [x] **Step 1: Record the strategic transition**

Add a `Synchronized Distribution Strategy` section recording only verified facts:

- active issue discovery is retained as cold-start proof production, not the long-term acquisition engine;
- the north star is `Weekly External Verified Reuses`;
- the baseline is 18 Stars, 39 views / 19 unique visitors in the current GitHub 14-day window, and zero Share/Growth Proof Issues;
- the first wave uses Outcome #57 and upstream PRs #170/#376 without upgrading trust;
- no tracking SDK is introduced.

- [x] **Step 2: Verify no claim drift**

Run:

```powershell
rg -n "18 Stars|39.*19|0.*Share Proof|maintainer-validated|Weekly External Verified Reuses" docs/project-memory-snapshot.md
```

Expected: all baseline and trust-boundary markers are present.

### Task 4: Run repository verification and publish the branch

**Files:**
- Verify all modified files.

- [x] **Step 1: Run launch-surface tests**

```powershell
python -m unittest scripts.test_launch_surface -v
```

Expected: all launch-surface tests pass.

- [x] **Step 2: Check Markdown links and whitespace**

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [x] **Step 3: Self-review the diff**

```powershell
git diff --stat
git diff -- docs/distribution-waves/live-skill-proof-20260721.md docs/launch-pack.md docs/launch-copy.md docs/project-memory-snapshot.md scripts/test_launch_surface.py
```

Expected: no fabricated adoption metrics, no trust upgrade, and no unrelated changes.

- [x] **Step 4: Commit, push, and open a pull request**

```powershell
git add docs scripts/test_launch_surface.py
git commit -m "docs: establish synchronized distribution loop"
git push -u origin codex/synchronized-distribution-loop
gh pr create --repo JinNing6/Noosphere --base main --head codex/synchronized-distribution-loop --title "docs: establish synchronized distribution loop" --body "Adds the first claim-bounded distribution wave, channel-native publication assets, a public execution ledger, project-memory alignment, and a launch-surface regression test."
```

Expected: a ready-for-review pull request containing only the synchronized distribution work.

### Task 5: Execute the first public wave

**Files:**
- Update after each external action: `docs/distribution-waves/live-skill-proof-20260721.md`

- [x] **Step 1: Publish GitHub as the canonical anchor**

After the repository changes reach `main`, publish the factual wave link on the existing launch/proof surface. Record the exact public URL.

- [x] **Step 2: Stage channel-native posts**

Prepare X/LinkedIn, one rules-compliant Reddit community, V2EX, and one long-form platform from the wave packet. Do not submit any browser form until the exact destination, account, and post are confirmed at action time.

- [x] **Step 3: Keep HN human-authored**

Provide only the fact outline and product link. The maintainer writes and submits the HN explanation personally and does not coordinate votes or comments.

- [ ] **Step 4: Record 24-hour and 72-hour evidence**

Record public post URLs, GitHub traffic/referrers, maintainer responses, and exact Outcomes. Do not infer adoption from reach.
