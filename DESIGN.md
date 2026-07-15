---
version: "alpha"
name: Noosphere Living Skill Tree
description: A restrained, full-bleed knowledge interface where verified Agent Skills grow through visible evidence and outcomes.
colors:
  primary: "#F4F6F8"
  on-primary: "#090B0D"
  background: "#090B0D"
  surface: "#101418"
  surface-raised: "#171C21"
  border: "#2A3036"
  text: "#F4F6F8"
  text-muted: "#9AA3AC"
  text-faint: "#7C858E"
  branch: "#D9D1C2"
  seed: "#F0C75E"
  reproduced: "#35D07F"
  proven: "#33D6C4"
  established: "#5FA8FF"
  update: "#E65AB0"
  warning: "#F26B5E"
  violet: "#8D7CFF"
  orange: "#F28B4B"
typography:
  display:
    fontFamily: Inter
    fontSize: 3rem
    fontWeight: 600
    lineHeight: 1.04
    letterSpacing: 0
  h1:
    fontFamily: Inter
    fontSize: 2rem
    fontWeight: 600
    lineHeight: 1.12
    letterSpacing: 0
  h2:
    fontFamily: Inter
    fontSize: 1.25rem
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: 0
  body:
    fontFamily: Inter
    fontSize: 0.9375rem
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: 0
  label:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: 0
  mono:
    fontFamily: ui-monospace
    fontSize: 0.8125rem
    fontWeight: 500
    lineHeight: 1.45
    letterSpacing: 0
rounded:
  xs: 2px
  sm: 4px
  md: 8px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 10px
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: 10px
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: 24px
  panel-raised:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: 16px
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    height: 44px
  divider:
    backgroundColor: "{colors.border}"
    height: 1px
  metadata:
    backgroundColor: "{colors.background}"
    textColor: "{colors.text-muted}"
    typography: "{typography.label}"
  metadata-faint:
    backgroundColor: "{colors.background}"
    textColor: "{colors.text-faint}"
    typography: "{typography.label}"
  branch:
    backgroundColor: "{colors.branch}"
    textColor: "{colors.on-primary}"
  state-seed:
    backgroundColor: "{colors.seed}"
    textColor: "{colors.on-primary}"
  state-reproduced:
    backgroundColor: "{colors.reproduced}"
    textColor: "{colors.on-primary}"
  state-proven:
    backgroundColor: "{colors.proven}"
    textColor: "{colors.on-primary}"
  state-established:
    backgroundColor: "{colors.established}"
    textColor: "{colors.on-primary}"
  state-update:
    backgroundColor: "{colors.update}"
    textColor: "{colors.on-primary}"
  state-warning:
    backgroundColor: "{colors.warning}"
    textColor: "{colors.on-primary}"
  domain-violet:
    backgroundColor: "{colors.violet}"
    textColor: "{colors.on-primary}"
  domain-orange:
    backgroundColor: "{colors.orange}"
    textColor: "{colors.on-primary}"
---

## Overview

Noosphere Skills is a quiet operational interface wrapped around a living, cinematic knowledge tree. The tree is not decoration: every branch, bud, leaf, version segment, and light pulse communicates real lifecycle state. The first screen must be immediately useful to developers while still producing a singular visual identity.

Noosphere Universe keeps the existing colorful 3D consciousness experience as a separate opt-in surface. Skills is the default product surface and should feel more mature, precise, and evidence-driven.

## Colors

The foundation is neutral black rather than blue-black. Ivory structure and high-contrast text provide permanence; spectrum colors encode distinct domains and lifecycle states. Never wash the whole scene in one hue.

- Use `{colors.branch}` for the trunk and stable branch structure.
- Use lifecycle colors consistently: Seed, Reproduced, Proven, Established, Update, and Warning.
- Domain colors may use proven, seed, established, violet, update, orange, reproduced, and warning as a balanced spectrum.
- Bloom is reserved for active propagation, selection, and a newly verified outcome. Static nodes remain legible without glow.
- Never rely on color alone. Pair every state with shape, stroke, and textual status.

## Typography

Inter remains the product typeface to preserve existing assets and loading behavior. Text is compact and operational. Hero-scale typography is limited to the product name and the current focused domain; drawers, lists, and controls use body and label scales.

All letter spacing is zero. Code, versions, digests, and commands use the mono token.

## Layout

The tree occupies the full available canvas. Navigation and controls sit on stable edge rails, not floating decorative cards. Desktop uses a compact top bar, a left domain rail, and one right detail drawer. Mobile uses a compact header and bottom sheets while preserving an unobstructed tree overview.

The interface has two equal product modes:

- Tree: spatial overview, growth, relationships, and lifecycle.
- Directory: scanning, filtering, comparison, and repeated developer work.

Semantic zoom controls information density:

1. Overview shows the root and domain branches.
2. Domain focus shows Skill nodes and compact labels.
3. Skill focus shows immutable versions, evidence, and selective cross-domain links.

## Elevation & Depth

Depth comes from occlusion, line weight, focus blur, and restrained emissive edges. UI surfaces use one border and one shadow layer. Do not nest cards or stack multiple translucent glass panels.

## Shapes

The tree combines botanical growth, neural dendrites, and engineered topology. It must not resemble a literal fantasy tree.

- Domain junction: faceted branch joint.
- Seed: hollow diamond bud.
- Reproduced: open leaf pair.
- Proven: filled hexagonal node.
- Established: ringed hexagonal node.
- Update candidate: offset pulse marker at a branch tip.
- Version: a visible segment along the same branch, never an overwritten node.
- Withdrawn: retained dark branch scar with an audit affordance.

Rounded rectangles are limited to fields, segmented controls, drawers, and repeated directory rows. Icons use Lucide where available.

## Components

The global search is the first value action. It accepts an error, symptom, or task and highlights the most relevant real Skills or verified Seeds. Search results must never imply publication when the registry is empty.

Selecting a domain focuses the camera and opens a conventional list for that domain. Selecting a Skill opens a single detail drawer with version, source, verification state, digest, outcomes, install command, and update actions.

Create Skill is contextual: select a domain first, then open the structured creation drawer. Propose Domain is a secondary command and creates a review request rather than immediately mutating the public taxonomy.

Noosphere Universe is available through a persistent but secondary navigation item. Switching surfaces must preserve the full existing Universe implementation.

## Do's and Don'ts

- Do make the first useful result reachable in under one minute.
- Do show real registry, static Skill, and Founding Seed data with explicit source labels.
- Do keep branch positions deterministic so returning users build spatial memory.
- Do provide Tree and Directory parity for every domain and Skill.
- Do provide keyboard navigation, visible focus, reduced motion, and non-color status cues.
- Don't fabricate Skill counts, outcomes, validators, or version history.
- Don't turn every Skill into a new top-level domain.
- Don't render all cross-domain links at once.
- Don't use full-scene bloom, decorative gradient orbs, or purple-dominated glassmorphism.
- Don't delete or rewrite the existing Noosphere Universe functionality.
