---
name: frontend-layering-specificity-debug
description: Diagnose and fix frontend controls whose typography or dimensions ignore component CSS, and React Three Fiber/Drei projected HTML labels that paint above opaque drawers, dialogs, or navigation. Use for inconsistent button sizes, element-type-dependent styling, unexpected wrapping, z-index escalation failures, or WebGL labels leaking through DOM overlays.
---

# Frontend Layering And Specificity Debug

## Diagnose Before Styling

1. Reproduce at the reported viewport and interaction state.
2. Record bounding boxes plus computed `font-size`, `line-height`, `width`, `height`, and `z-index`.
3. Compare equivalent element types. A `<button>` and an `<a>` that share a component class but render differently usually indicate a selector or user-agent boundary.
4. Enumerate matched CSS rules instead of inferring from source order alone.
5. Use `document.elementFromPoint()` at the overlap to identify the element that actually paints or receives input.

## Fix Typography Specificity

- Treat shorthand declarations such as `font: inherit` as resetting `font-size`, `font-weight`, and `line-height` together.
- Check specificity as well as order. `.app button` overrides `.button` even when `.button` appears later.
- In scoped resets, prefer `font-family: inherit` and explicit inherited properties. Keep component-level `font-size` and `line-height` authoritative.
- Add `white-space: nowrap` only to stable command controls; use responsive label collapse when the toolbar cannot fit.
- Verify computed styles on real `<button>`, `<a>`, `<input>`, and `<select>` elements after the fix.

## Fix Projected 3D Labels

- Remember that Drei `<Html>` is projected DOM, not canvas pixels. Its default `zIndexRange` is extremely high and can paint over an otherwise opaque drawer.
- Assign a bounded range such as `zIndexRange={[8, 1]}` for scene labels, then keep application chrome above it.
- Do not keep increasing drawer z-index without identifying the projected label range and stacking context.
- Reserve real canvas width for persistent desktop drawers when labels or selected nodes would otherwise sit underneath them.
- Use semantic zoom: show detailed labels only for hover, selection, a focused domain, or an actual non-empty search match.

## Regression Checks

Run desktop, compressed desktop, and mobile checks:

```js
const style = getComputedStyle(control)
expect(style.fontSize).toBe('13px')
expect(document.body.scrollWidth).toBe(document.documentElement.clientWidth)
```

For an open overlay, compare the projected label and drawer layers and probe overlap points:

```js
const top = document.elementFromPoint(x, y)
expect(drawer.contains(top)).toBe(true)
```

Also verify:

- short mobile sheets size to content;
- long content reaches a bounded height and scrolls internally;
- adjacent 3D nodes remain independently clickable;
- an empty search does not highlight every node;
- screenshots show no labels painted through drawers.

## Completion Standard

Complete only when the original viewport reproduces cleanly, computed styles prove the intended rule wins, projected labels stay below DOM overlays, responsive overflow is zero, and a regression check covers the root cause.
