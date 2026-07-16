---
name: cloudflare-pages-stale-assets
description: Diagnose and fix Cloudflare Pages deployments where the live site still shows old CSS, JavaScript, native controls, untranslated text, or stale UI after a successful deploy. Use for static websites on Cloudflare Pages, custom domains, pages.dev previews, browser-cache disagreements, and "it deployed but I still see the old page" reports.
---

# Cloudflare Pages Stale Assets

Use this before changing UI code again. First prove whether the failure is deployment, domain routing, edge/browser cache, or runtime JavaScript.

## Workflow

1. Confirm the repo state:
   - Read project agent rules first.
   - Check the current branch, latest commit, and dirty files.
   - Identify the exact generated/static output directory used by Pages.
2. Compare every live hostname:
   - Fetch `https://<pages-project>.pages.dev/`, the apex custom domain, and `www`.
   - Add a cache-busting query to HTML, CSS, and JS URLs, for example `?codex_check=<timestamp>`.
   - Record status, redirect target, `ETag`, `CF-Cache-Status`, `Age`, and whether the expected new code appears.
3. Distinguish failure layers:
   - Deployment: latest commit is not in the live HTML.
   - Domain routing: `pages.dev` is current but custom domain is stale or SSL/route-broken.
   - Asset cache: HTML is current but references unversioned old CSS/JS.
   - Browser cache: network fetch is current but the user's browser still displays old assets.
   - Runtime: assets are current but console errors prevent enhancement.
4. Fix at the owning layer:
   - If production branch is wrong, fix Pages branch control or redeploy the intended branch.
   - If custom domain differs, fix Pages custom domain binding and DNS before editing UI.
   - If stale CSS/JS is plausible, version static asset URLs in every HTML page, such as `style.css?v=<release-id>` and `language.js?v=<release-id>`.
   - If runtime fails, inspect console errors and fix the actual JavaScript exception.
5. Verify after deploy:
   - Fetch live HTML and confirm it references versioned assets.
   - Fetch versioned CSS/JS and confirm they contain the expected selectors/functions.
   - Use a real browser when possible to confirm DOM enhancement, not only source text.
   - Tell the user whether they need a hard refresh; after versioned assets they usually should not.

## Completion Standard

The latest live HTML is proven to reference the intended assets, all affected hostnames are checked or explicitly reported as unreachable, runtime errors are ruled out or fixed, and the final commit includes only task-scoped files.
