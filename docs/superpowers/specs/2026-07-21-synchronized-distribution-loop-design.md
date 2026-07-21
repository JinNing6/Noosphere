# Synchronized Distribution Loop Design

Status: approved for execution on 2026-07-21

## Problem

Noosphere has a credible product promise, public artifacts, and a real external proof chain, but its current launch documents still describe a finite sequence of posts. The external proof sprint also depends on the maintainer manually finding issues. Neither becomes a durable acquisition system on its own.

The missing system is a synchronized loop that turns each verified product event into channel-native distribution, routes attention into one activation path, and converts real use back into public evidence.

## Decision

Use a proof-led synchronized distribution loop:

```text
verified product event
-> canonical evidence packet
-> channel-native media wave
-> one install-and-try path
-> public Outcome or maintainer response
-> next verified product event
```

This is deliberately different from two rejected alternatives:

1. Simultaneous identical cross-posting is fast but creates spam risk, weak community fit, and no durable evidence loop.
2. Building a full analytics and owned-media stack before publishing delays learning and conflicts with Noosphere's current zero-tracking posture.

## North Star And Measurement

The north star remains `Weekly External Verified Reuses`.

The first-wave public baseline, verified through GitHub on 2026-07-21, is:

- 18 Stars and 1 fork.
- 39 repository views from 19 unique visitors in GitHub's current 14-day traffic window.
- Top referrers: `github.com` 6 views / 1 unique, Baidu 1 / 1, Google 1 / 1.
- 0 recorded Share Proof Issues and 0 recorded Growth Proof Issues.
- 1 recorded Skill Outcome, reported and approved by the maintainer, so the Skill remains `maintainer-validated`.

Do not infer users, installs, reuse, or success from views, Stars, clones, downloads, or public post impressions. Channel reporting uses public post URLs, GitHub's 14-day traffic/referrer data, upstream maintainer responses, and exact Outcome evidence.

## Canonical Evidence Packet

Every distribution wave starts with one repository document containing:

- the exact verified event and claim boundary;
- primary public evidence URLs;
- commands and observed exit states when relevant;
- one product promise and one call to action;
- channel-native copy or, where platform rules require it, a human-authored outline;
- a public execution ledger with scheduled, published, and measured states.

The first packet is `docs/distribution-waves/live-skill-proof-20260721.md`.

Its hook is factual:

```text
One runtime packaging pattern. Three real projects. One released upstream repair and two regression-tested fixes under review.
```

The packet must preserve these boundaries:

- `okflint==0.3.0` failed and `0.3.1` passed; the upstream maintainer landed an equivalent fix independently.
- brainctl PR #170 and Ahrena PR #376 are open and mergeable, but are awaiting maintainer review and workflow approval.
- `action_required` with zero jobs is not a failed test run and is not green CI.
- No external third-party Agent reuse of the Noosphere Skill digest has been proven.

## Channel Roles

| Surface | Function | Required form | Primary next action |
|---|---|---|---|
| GitHub evidence packet, Issue #51, Outcome #57 | Source of truth and trust | Exact commands, links, claim boundaries | Install and try the Skill |
| X | Fast evidence propagation | Short thread with demo and proof links | Open the repository |
| LinkedIn | Engineering narrative and professional reach | One concise case post | Open the repository |
| Show HN | Product trial and technical challenge | Human-authored explanation; product must be directly usable | Run the zero-token query or install |
| Reddit | Community-specific problem discussion | One community only after checking its current rules; no identical cross-post | Reproduce or critique the boundary |
| V2EX | Chinese technical discussion | Concrete failure story, not a brand announcement | Run the query/install path |
| 掘金 / DEV | Searchable long-form knowledge | Technical case study with exact evidence | Install and apply the method |

Synchronization means one fact set and one conversion path, not identical wording or simultaneous mass posting.

## Sequence

1. Publish the canonical evidence packet and update launch documents.
2. Use GitHub as the first public anchor.
3. Publish the English fast-media wave during the same evidence window.
4. Stagger Show HN and Reddit so the maintainer can answer substantive replies; do not coordinate votes.
5. Publish the Chinese forum post and long-form case from the same evidence packet.
6. At 24 and 72 hours, record only verifiable public URLs, traffic/referrer snapshots, maintainer responses, and Outcomes.
7. Publish a follow-up only when new evidence exists.

## Platform And Trust Constraints

- Hacker News requires something people can try, prohibits vote coordination, and currently prohibits generated or AI-edited comment text. Noosphere will provide a fact outline, but the maintainer must write and post the HN explanation personally.
- Reddit prohibits repetitive mass posting and requires checking each community's rules. Select one relevant community per evidence wave.
- GitHub traffic referrers cover only the latest 14 days and the top 10 sources. They are directional channel evidence, not an attribution ledger.
- No tracking SDK, cookies, fingerprinting, or inferred adoption metrics are introduced by this design.
- All public copy must keep `maintainer-validated` until independent evidence satisfies the existing gates.

## Completion Criteria

The first synchronized wave is complete only when:

- the canonical evidence packet is public on `main`;
- every published surface has its public URL recorded;
- at least one English and one Chinese channel have been used without violating platform rules;
- the 24-hour and 72-hour evidence snapshots are recorded;
- replies are answered with primary evidence;
- any real external use is routed into an exact-version Outcome instead of being inferred from reach.
