# Founding Debug Memories

Last updated: 2026-07-09

Canonical launch thread: https://github.com/JinNing6/Noosphere/issues/25

## Why This Exists

Noosphere should not launch as a generic social feed. The first public proof is narrower:

```text
Stop solving the same bug twice.
```

This document turns real Noosphere engineering failures into reusable debug memories. The strongest memories can become `skill-candidate` issues and, later, callable agent skills.

Every founding memory below follows the same proof shape:

- Symptom: what failed.
- Wrong fix: what looked plausible but did not address the real cause.
- Root cause: why it failed.
- Correct fix: what changed.
- Verification: how the fix was checked.
- Skill candidate: what future agents should learn.

## Proof Story 1: Android WebView / R3F Node Picking

### Symptom

On Android, visible glowing globe nodes could be tapped without opening the detail panel. Some taps selected the wrong node or no node at all.

### Wrong Fix To Avoid

Do not only increase visual glow, z-index, or canvas size. The user was tapping the perceived glow footprint, while the actual raycast target remained a compact mesh.

### Root Cause

The mobile touch target used a compact visual `InstancedMesh` sphere while Bloom/emissive glow made the perceived node footprint much larger. A later real Android WebView test also showed two extra causes:

- Hidden splash/log display layers could remain hit-testable during transition.
- Competing R3F particle layers were sorted by world depth rather than touch-center precision.

### Correct Fix

`GPUParticleLayer` keeps the compact visual particle scale but adds a synchronized invisible low-poly hit layer with larger touch targets. It handles selection on `onPointerDown`, preserves `event.instanceId`, and uses a perceptual screen-picking score so the visible node closest to the touch wins across particle layers. `SplashScreen` and its wrapper were made non-interactive display layers.

### Verification

Verified with:

- `reports/mobile-floating-panel-regression.cjs`
- `reports/android-app-node-pick-regression.cjs`
- Pixel 5 canvas coordinate probing
- Android ADB physical taps on projected dynamic-light-node coordinates
- Debug checks that `window.__NOOSPHERE_LAST_PARTICLE_PICK__.instanceId` matched the tapped dynamic node
- `.detail-panel-shell` opening after the tap
- Android release rebuild `versionCode 14` / `versionName "1.0.13"`

### Skill Candidate

Trigger this skill when a mobile WebView / R3F canvas has a visible target that does not respond accurately to touch.

The skill should check:

- Visual footprint versus raycast footprint.
- Invisible overlays that still receive pointer events.
- Whether `instanceId` survives custom raycast layers.
- Whether depth sorting conflicts with what users perceive as the nearest target.
- Real Android WebView taps, not only desktop browser clicks.

## Proof Story 2: GitHub Device Flow Mobile Login

### Symptom

In early mobile builds, tapping GitHub sign-in opened the GitHub verification page too quickly for users to retain the device code. Later, even after successful browser-side approval, the app could show a failure such as:

```text
Unable to resolve host "github.com": No address associated with hostname
```

The GitHub mark was also too weak visually in the sign-in control.

### Wrong Fix To Avoid

Do not treat every token polling/profile fetch error as a terminal OAuth failure. Mobile network and DNS failures during Device Flow are often transient, especially after the user leaves and returns from an external browser.

### Root Cause

The interaction mixed three concerns too tightly:

- Showing the `user_code`.
- Opening the verification browser.
- Polling token/profile endpoints.

The browser handoff happened before users could comfortably copy or remember the code, and retryable network failures were surfaced as final login failures.

### Correct Fix

The app now shows the `user_code` persistently first and opens GitHub only when the user taps the explicit browser action. Native Android opens GitHub through `@capacitor/app-launcher` and the system/default browser path, with Capacitor Browser only as fallback. `@capacitor/clipboard` copies the code automatically, displays copied/failed status, and keeps a manual copy button. Device Flow token polling and GitHub profile fetch treat DNS, connection, and timeout errors as retryable waiting states instead of terminal failures.

### Verification

Verified with:

- `reports/github-device-flow-regression.cjs`
- A mocked slow GitHub device-code request
- Assertion that no automatic GitHub open occurs
- Manual open target `https://github.com/login/device`
- Transient network failures on `https://github.com/login/oauth/access_token`
- Transient network failures on `https://api.github.com/user`
- Assertion that no `.github-auth-error` appears for retryable failures
- Successful session completion as `octocat` after retry
- Android release rebuilds through `versionCode 6` / `versionName "1.0.5"`

### Skill Candidate

Trigger this skill when a no-backend OAuth Device Flow login works in ideal browser tests but fails on mobile devices.

The skill should check:

- Whether the device code is visible before browser handoff.
- Whether the code is copied to clipboard with a fallback copy action.
- Whether external browser launch uses the native default browser path.
- Whether polling respects OAuth terminal errors versus retryable network failures.
- Whether the waiting UI preserves state while the user leaves and returns.

## Proof Story 3: Mobile Async UI Overlay Lifecycle

### Symptom

Mobile panels could be clipped or covered by fixed controls. The consciousness upload button was covered by `SAFE` and contribution buttons. Android back could first clear input focus instead of closing the overlay. Some sheets needed swipe-back and hardware-back behavior without tearing down the main UI.

### Wrong Fix To Avoid

Do not keep adjusting z-index alone. If fixed controls, keyboard focus, safe-area height, and route/back lifecycle are not modeled together, each panel fix can break another panel.

### Root Cause

Panel state, viewport constraints, fixed bottom controls, keyboard focus, and Android back behavior were distributed across UI elements. That made local fixes fragile on real mobile viewports.

### Correct Fix

The contribution heat network and safety filter panels were changed from desktop absolute positioning to viewport-constrained mobile sheets. The detail panel became a mobile full-screen overlay. Reusable hooks `useSwipeBack`, `useOverlayHistory`, and `useAndroidBackButtonBridge` coordinate overlay state. The upload trigger became a 56px circular FAB in the same bottom cluster, and the expanded uploader became a high-level mobile overlay. Mobile touch devices no longer autofocus the thought textarea when opening the uploader.

### Verification

Verified with:

- `reports/mobile-floating-panel-regression.cjs`
- Playwright Pixel 5 viewport checks
- Targeted ESLint for touched files
- `cmd /c npm run build:android`
- `cmd /c npm run sync:android`
- Android `bundleRelease`
- Android `assembleDebug`
- Emulator checks that the contribution panel opens fully in-screen
- `KEYCODE_BACK` and edge back swipe closing the open overlay
- Screenshots under `reports/android-capacitor-*`, `reports/android-uploader-fixed.png`, and `reports/android-uploader-back-fixed.png`

### Skill Candidate

Trigger this skill when mobile WebView overlays are clipped, covered by fixed controls, or inconsistent with Android back and swipe-back.

The skill should check:

- Safe-area and `100dvh` constraints.
- Whether the overlay is mounted at a stable high-level UI layer.
- Whether keyboard autofocus steals the first Android back event.
- Whether fixed bottom controls overlap panel actions.
- Whether hardware back and edge swipe close overlay state before exiting the app.

## Seven Additional Founding Memory Candidates

These candidates should be converted into public memories or skill candidates after the first three proof stories are published.

| Candidate | Reusable Lesson | Evidence Source |
|---|---|---|
| Mobile HUD / FAB overlap | Treat stats HUD, zoom rail, and bottom action cluster as collision domains, not isolated components. | `reports/mobile-floating-panel-regression.cjs` and Android rebuild `1.0.10` |
| Mobile globe zoom and overview | Give dense 3D graphs explicit overview, zoom-in, and zoom-out controls; do not rely on pinch gestures alone. | `reports/android-globe-zoom-main-complete2.png`, `reports/android-globe-zoom-out.png` |
| R3F lint and animation mutation | Use declarative JSX materials plus refs for animation-frame mutation to satisfy React immutability rules. | Full frontend ESLint cleanup on 2026-07-01 |
| Play Console package mismatch | The Play Console package name is immutable for the app entry; local Android `applicationId` must match before AAB upload. | `com.noosphere.app` package correction and release manifest inspection |
| UGC safety controls | Public user-generated memory needs native report, hide, and block controls even when GitHub is the backend. | Play content-rating and Data Safety updates on 2026-06-30 |
| Local notifications without backend | No-backend Android notification can start as local polling of GitHub Issues/Comments, not remote FCM. | `@capacitor/local-notifications@8.2.0` implementation and regression |
| MCP notification daemon state | Daemons should share active runtime state rather than reading split stale module globals. | `sdk/tests/test_notifications_daemon.py` and `161 passed` SDK tests |

## Public CTA

Upload one bug you never want another agent to solve again:

```text
https://github.com/JinNing6/Noosphere/issues/25
```

The first goal is not broad traffic. The first goal is one public proof that a Noosphere memory saves a future agent from rediscovering a solved failure.
