---
name: debug-async-ui
description: Use when UI state or returned content disappears, flashes, rolls back, saves but loses state, menus fail intermittently, or real browser behavior differs from tests in async frontend flows.
---

# Debug Async UI

Use this skill before changing visuals for async interaction bugs. Prove which layer owns the failure: event, state, data, lifecycle, or render.

## Workflow

1. Reproduce the original symptom first. Capture the user action, the immediate UI state, and the final UI state after async work completes.
2. Add a slow-request regression test before the fix. Simulate 200-500 ms API, database, provider, or store delay. Assert:
   - the immediate intermediate state is visible after the action;
   - the final returned state/content is visible after resolution;
   - the target component was not incorrectly unmounted;
   - global loading did not replace a local interaction surface.
   For startup or splash gates, also add a regression where the readiness
   future never completes. The app must leave the splash/loading route through a
   bounded timeout or an explicit fallback instead of waiting forever.
3. Trace the layers in order:
   - Event: click, hover, keyboard, wheel, or submit handler fires exactly once.
   - State: selectedId, detailId, expandedId, edit state, pending state, and result state are written where expected.
   - Data: API/database/provider/store refreshes do not overwrite the target state.
   - Lifecycle: route changes, keys, conditional rendering, AnimatedSwitcher-like components, and loading branches do not unmount the owner of interaction state.
   - Render: UI actually binds to the correct state after the previous layers are proven.
4. Fix the root cause, not the symptom. Move durable interaction state to a stable parent/controller/store when a child can be replaced by loading, routing, or conditional rendering. Use local loading for detail open, local refresh, save title/color/sort, and similar narrow operations. Reserve global loading for initial load or broad data-source switches.
5. Check the trigger boundary. If the user expects generation for the current entity, trigger from stable entity selection/page context, not only from narrow record-kind flags such as "external candidate". Manual buttons should remain as retry controls, not the only path to generation.
6. If the operation affects the currently viewed entity, surface status and returned content on every stable context where the user may remain while waiting, including the active tab, default overview, and relevant side panel. Do not leave the only evidence in an off-screen tab, transient child panel, hidden side panel, or default page the user is not currently viewing.
7. For aggregate responses, distinguish "request finished" from "required sub-result returned". If a key source, model, provider, or structured field is missing from the returned payload, show an explicit missing/failed diagnostic on the same stable contexts; do not let a broad "ready" status imply the missing sub-result succeeded.
8. For AI/model synthesis that supplements several factual modules, centralize extraction from the real response in a stable parent and render module-specific supplement panels. Each panel must label loading, failure, missing sub-result, or completion; completed AI content must be marked as AI-generated and must not be merged into authoritative facts unless the normal source-gating path approves it.
9. For slow search/detail generation, never leave the previous selected entity visible while the new query is pending. After a short threshold, render a query-scoped pending placeholder in the stable parent, label it as generating, and suppress duplicate detail verification for that placeholder. When the aggregate search resolves, replace the placeholder with the real returned candidate or an explicit empty/error state.
10. For launch Aha screens, onboarding tours, permission primers, marketing modals, or other delayed overlays, gate later overlays on the dismissal/completion state of the current primary surface. A timer-driven tour must not appear on top of an undismissed launch panel, auth gate, consent gate, or blocking first-run task. Add a delayed regression that waits longer than the overlay timer while the primary surface remains open.
11. For mobile floating action clusters, measure the actual bounding rectangles of every simultaneously visible trigger. Assert all triggers are inside the viewport and pairwise non-overlapping. Treat the cluster as one layout system rather than moving one button at a time. When an opened sheet/panel should cover those triggers, assert the panel is in the viewport and has an overlay layer above persistent top/bottom controls.
12. For mobile overlays containing text inputs, check whether opening the overlay auto-focuses an input. On Android and other touch-first contexts, auto-focus can cause the first hardware/back gesture to clear input focus or keyboard state instead of closing the overlay. Prefer no mobile auto-focus unless text entry is the sole immediate task, and add a regression that the expected back/overlay history path closes on the first action.
13. For external OAuth/device-code flows, separate "browser-side approval" from "app-side token/profile completion." The app must keep the device code and waiting state visible while polling, and transient DNS/connection/timeouts from token or profile endpoints should update a retrying status rather than switch to terminal failure. Add a regression where the first token poll or profile request fails with a network error and the next retry succeeds; assert no error UI appears and the signed-in state eventually renders.
14. For auth-bound forms with quick-fill presets, templates, or shortcuts, assert that applying the preset does not clear authenticated identity, creator, token, tenant, workspace, or attribution fields. Re-read the stable auth/session store at the submit boundary as a fallback, because the visible form field may have been cleared by a preset, locale switch, or overlay remount.
15. If one part of an authenticated flow uses native/mobile-safe retry semantics, adjacent authenticated actions such as submit, publish, save, or create-record should use the same retry class for DNS, connection, timeout, HTTP 0, and 5xx/429 states. Add a regression where the first submit/publish request fails transiently and the next retry succeeds.
16. Verify with the slow regression plus relevant static checks, build, and browser checks that switch every affected tab/module.
17. For file-backed or local-database UI state, inspect write ordering as well as
    restore ordering. Two unawaited saves can race even when each save is
    individually correct: an older snapshot may finish last and overwrite a
    newer terminal/error/result state. Serialize complete snapshot writes (or
    use an atomic transaction), establish restored terminal guards before
    publishing restored content, and gate entitlement/lifecycle auto-retries
    until hydration completes. Run the restart regression repeatedly and add a
    200-500 ms delayed hydration case where entitlement becomes active before
    the persisted state arrives.

## Common Mistakes

- Adjusting z-index, hit area, opacity, or animation before proving the render layer is wrong.
- Testing only with synchronous fake APIs.
- Replacing the whole app or main panel with global loading during a local save/detail/refresh.
- Treating a terminal phase such as `complete`, `finished`, `submitted`, or `done` as the active in-progress step. For step timelines, model terminal phases explicitly: previous and terminal rows should render completed indicators, while spinners belong only to non-terminal active phases. Add a small regression test for phase semantics so `complete` cannot keep returning `isActive`.
- Storing returned data only inside a transient component that can unmount.
- Fixing only the default overview while the user is waiting inside another tab, drawer, or detail workspace.
- Gating auto-generation on source/candidate type when the user's mental model is "this selected entity is being generated now".
- Treating an aggregate response as successful when a required nested source or model result is absent.
- Showing AI/model synthesis in only one or two modules while sibling modules remain blank, or merging AI text into factual sections without a visible AI-generated label.
- Letting a slow new search keep rendering the old selected entity, which makes users think nothing happened. The pending UI must be keyed by the current query, not by the previous selected ID.
- Letting a delayed onboarding or feature tour mount while a first-run Aha panel, auth gate, or consent gate is still open. The user experiences this as an unresponsive or trapped first screen even when all click handlers technically work.
- Treating mobile FABs, filter buttons, upload buttons, and graph buttons as independent absolute elements. If they are visible at the same time, they are a single bottom action cluster and need explicit no-overlap tests.
- Treating a mobile top/bottom sheet as safe because both offsets use `env(safe-area-inset-*)`. If the sheet content has intrinsic minimum height, it can still overflow the viewport. Measure the rendered bounding rect and constrain the sheet with explicit `height`/`max-height` based on `100dvh` minus safe-area insets and margins, with internal scrolling.
- Auto-focusing an input inside a mobile overlay by default. This can make Android hardware back appear broken because the first back action is consumed by keyboard/focus handling.
- Treating test and real-browser divergence as a visual bug before checking async lifecycle.
- Treating a disabled submit button after login/auth as an auth-state failure before checking local form validation. First inspect the visible counters, validation thresholds, and disabled predicate. If a button is disabled because content is below a threshold, show the exact unmet requirement near the input and add a regression for the user-entered text, not just a prefilled long template.
- Treating a transient network/DNS failure during OAuth Device Flow polling as "login failed" after the user has already approved the login in the external browser. Until the OAuth server returns a terminal error such as cancellation, expiration, access denial, or a non-retryable HTTP response, keep the flow in a visible retrying/waiting state.
- Showing an OAuth Device Flow code without copying or copy-state feedback. On mobile, the user may switch to an external browser immediately; write the code to the native clipboard when available, render a visible copied/failed status beside the code, and keep a manual copy button as fallback. Regression tests should assert both the clipboard payload and the visible status.
- Letting a quick preset, template, animal/persona mode, or demo shortcut clear a signed-in creator/author field. The user perceives this as auth or upload failure because the submit button/state changes after using the shortcut, even though the actual root cause is local form state mutation.
- Hardening OAuth polling with mobile network retries but leaving the post-login submit/publish request on a raw one-shot fetch path. Real-device DNS and captive-network failures can then move from "login failed" to "upload failed" without a consistent recovery path.
- Waiting forever on a global startup readiness future, service container,
  server discovery, notification/Firebase initialization, or other background
  bootstrap step. Splash and full-screen launch loading should have a bounded
  wait, a logged fallback, and a test that proves an uncompleted future cannot
  strand the user on the launch screen.
- Updating only a distant side panel after a card/button click while the clicked card has no selected state, expansion, or inline confirmation. If the user clicks `查看线索` or `查看证据` inside a card, the card itself should show immediate feedback or inline detail when the side panel may be off-screen.
- Assuming `save(state)` calls finish in invocation order. Async filesystem
  writes that delete/recreate a directory or rewrite one metadata file must be
  serialized; otherwise a stale pre-error snapshot can overwrite the newer
  terminal state and trigger an incorrect retry after restart.

## Completion Standard

The original symptom is reproduced, the slow async regression fails before the fix and passes after it, the status/content is visible where the user expects it, and no visual-only tweak is used without evidence.
