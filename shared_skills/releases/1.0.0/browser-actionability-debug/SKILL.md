---
name: browser-actionability-debug
description: Diagnose browser UI tests or real browser checks where an element appears visible but cannot be clicked, copied, hovered, or focused. Use for Playwright/Chrome/browser automation failures involving overlays, splash screens, opacity transitions, pointer-events, elementFromPoint mismatches, clipboard assertions, or differences between "visible" and actually actionable UI.
---

# Browser Actionability Debug

## Workflow

1. Reproduce the failure with a real browser action, not only DOM existence.
   - Prefer normal `locator.click()` first so the browser reports what intercepts the pointer.
   - Read the full call log. If it names an intercepting element, treat that as evidence.

2. Separate visibility from actionability.
   - `visible` can still be blocked by an overlay, `opacity: 0`, parent `pointer-events: none`, a splash screen, or an element with higher stacking order.
   - Inspect `elementFromPoint()` at the target center and compare it to the intended button/input.
   - Capture computed `opacity`, `visibility`, `display`, `pointerEvents`, and bounding boxes for the target and its stable ancestors.

3. Check lifecycle gates before changing CSS.
   - If a splash/loading/transition component exists, wait for the lifecycle signal that makes the app interactive, such as overlay detached or app shell `pointer-events: auto`.
   - Do not fix a test by using `force: true` unless the user specifically needs to bypass hit testing. It can hide real UX bugs.

4. Fix at the correct layer.
   - If the overlay should still be active, update the test to wait for the overlay to detach.
   - If a decorative canvas or visual layer should never capture input, set `pointer-events: none` on that visual layer.
   - If app content is intentionally disabled until boot, do not make underlying controls clickable before boot unless that is a product decision.

5. Verify clipboard behavior cross-platform.
   - On Windows, browser clipboard reads may normalize line endings to CRLF. Normalize `\r\n` to `\n` for semantic multi-line copy assertions.
   - Still assert exact command text after line-ending normalization.

## Diagnostic Snippet

Use this inside `page.evaluate()` when a click target exists but is not actionable:

```js
const target = document.querySelector('[aria-label="Copy Noosphere share post"]');
const rect = target?.getBoundingClientRect();
const top = rect
  ? document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2)
  : null;

return {
  target: target ? getComputedStyle(target).cssText : null,
  topTag: top?.tagName,
  topClass: String(top?.className || ''),
  topAria: top?.getAttribute?.('aria-label') || null,
  targetRect: rect ? {
    x: rect.x,
    y: rect.y,
    width: rect.width,
    height: rect.height,
  } : null,
};
```

## Completion Standard

- The original browser action succeeds without `force: true`.
- The target is within the tested viewport.
- `elementFromPoint()` at the target center resolves to the target or a child of it.
- Clipboard assertions normalize OS line endings but otherwise match exactly.
- Dev servers and temporary browser dependencies are stopped or removed after verification.
