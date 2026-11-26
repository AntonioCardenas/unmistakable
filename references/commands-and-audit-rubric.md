# Commands Playbook, Audit Rubric, and 57-Rule Anti-Slop Catalog

Execution guide for all 20 `/unmistakable` commands, the 24-point Technical Audit Health Score (`0-4` across 6 dimensions), and the 57 deterministic rules enforced by `scripts/detect_slop.py`.

## Contents
- Command execution playbooks
- Technical audit rubric (24-point health score)
- Critique rubric (UX and visual direction review)
- Foundations roadmap (18 ship-readiness gates)
- Deterministic 57-rule catalog (UNM-01 to UNM-57)

## Command execution playbooks

### System & Setup
- **`init`:** Inspect `package.json`, framework config, routes, and stylesheets. Ask at most 2-3 questions for missing product context (audience, primary job, non-negotiables) and write `PRODUCT.md`.
- **`system [ref]`:** Extract colors, fonts, SVG logo, tagline, and principles from the provided URL, screenshot, or codebase (`references/brand-and-design-system.md`). Confirm gaps, write `DESIGN.md`, `design/tokens.css`, `design/design-system.html`, and `design/brand-book-a4.html`, then run `python3 scripts/render_brand_book.py design/brand-book-a4.html design/brand-book-a4.pdf`.
- **`document`:** Reverse-engineer an existing project's shipped design language into `DESIGN.md` and `design/tokens.css` without changing visual behavior.
- **`extract [target]`:** Replace repeated hex literals, magic pixel spacing, and duplicated inline styles in `[target]` with semantic CSS custom properties from `DESIGN.md` / `design/tokens.css`.

### Build & Steer
- **`shape [feature]`:** Plan UX flow, Visitor Mode, state matrix, and the 6-block Direction Contract before writing code; stop for user confirmation on ambiguous product calls.
- **`build [target]`:** Execute Workflow A in `SKILL.md` end-to-end: Direction Contract, semantic landmarks, 3-tier tokens, 2-family / 3-size typography, all 5 interactive states, SEO/GEO markup, and clean `scripts/detect_slop.py` verification.
- **`typeset [target]`:** Collapse drifted font sizes into at most 3 body steps, cap families at 2 (`tabular-nums` for numbers), enforce `45ch-68ch` prose measure, apply `text-wrap: balance` / `pretty`, and set `>= 16px` on form inputs.
- **`layout [target]`:** Diagnose reading order with the squint test; replace nested card cages with proximity spacing and `1px` dividers, enforce `min-width: 0` on flex/grid children, and vary section composition below the fold.
- **`colorize [target]`:** Introduce intentional color hierarchy from `DESIGN.md` (`Restrained`, `Committed`, or `Color-Blocked`), tint secondary neutrals from the canvas hue, and fix every `< 4.5:1` contrast pair.
- **`graphics [target]`:** Make every micrographic speak one language (`references/micrographics.md`). Inventory each graphic on the target: icons, markers, dividers, callouts, status glyphs, small data graphics, spot art, social card, favicon. Write or confirm the Graphic Language block in `DESIGN.md` (derived from OWN-WORLD when missing). Consolidate to one icon family (`UNM-56`, gate `icon-system`), one stroke and three sizes (`UNM-54`), and `currentColor` (`UNM-55`); replace emoji (`UNM-32`) and stock illustrations (`UNM-57`) with inventory motifs; delete decoration the inventory cannot name. Finish with the belongs test on both viewports.
- **`animate [target]`:** Add one orchestrated entrance or spatial transition plus crisp `140ms-240ms` `cubic-bezier(0.22, 1, 0.36, 1)` control feedback on explicit properties (`transform`, `opacity`, `clip-path`), guarded by `@media (prefers-reduced-motion: reduce)`.
- **`bolder [target]`:** Amplify timid, generic layouts: commit to monumental hero typography, edge-to-edge imagery or live interactive stages, stronger scale contrast, and decisive surface fields while preserving product copy truth.
- **`quieter [target]`:** Calm visually noisy screens: remove competing accent colors, decorative glows, redundant borders, and gratuitous motion so primary content and controls breathe.
- **`distill [target]`:** Strip non-essential sections, duplicate CTAs, pre-heading eyebrows, decorative badges, and filler prose until every remaining element earns its pixels.
- **`deslop [target]`:** Remove the tells in `references/anti-patterns.md`. Score the 60-second slop review and run `python3 scripts/detect_slop.py <target> --json`, then fix at the token and component layer in this order: (1) light and depth: gradients, glows, glass, heavy shadows, and blobs become solid surface tokens, `1px` borders, and one `--shadow-overlay` for floating layers; (2) a stock purple accent becomes an accent derived from `DESIGN.md` (propose two options when no brand exists); (3) layout tells such as the `50/50` hero and icon-card grids; (4) copy: filler phrases rewritten, invented numbers, ratings, and logos deleted, never replaced with new inventions; (5) idle motion; (6) radius, spacing, and `z-index` drift. Re-run until `UNM-01` to `UNM-12` and `UNM-41` to `UNM-50` are clean or waived with a reason, and report the tell count before and after.

### Evaluate, Harden & Ship
- **`audit [target]`:** Run `python3 scripts/detect_slop.py <target> --json`, inspect source and rendered states, and output the 24-point Audit Health Score report below without modifying files.
- **`critique [target]`:** Evaluate visual authority, mode alignment, focal hierarchy, copy clarity, and anti-slop originality; deliver the top 3 highest-leverage design changes before minor polish notes.
- **`harden [target]`:** Apply `references/production-hardening.md`: long-text truncation/wrapping, RTL logical properties, Arabic ZWNJ and `Intl` formatting, network/API error recovery, concurrency locks, and pointer-gesture cancellation.
- **`optimize [target]`:** Fix Core Web Vitals (`LCP < 2.5s`, `INP < 200ms`, `CLS < 0.1`), eager hero `fetchpriority="high"`, image `width`/`height`/`aspect-ratio`, font `size-adjust`, and below-fold `content-visibility: auto`.
- **`seo [target]`:** Apply `references/seo-and-geo-patterns.md`: single `<h1>`, semantic landmarks, canonical + OpenGraph `1200x630`, validated Schema.org JSON-LD, answer-first lead blocks, semantic `<table>`/`<dl>`, and `llms.txt`.
- **`foundations [id]`:** Run `python3 scripts/check_foundations.py <project-root>` to display the 16-item ship roadmap, or pass `<id>` to fix one specific item and re-verify.
- **`polish [target]`:** Final pre-ship pass: clear `scripts/detect_slop.py` findings, theme browser surfaces (`::selection`, `:focus-visible`, `caret-color`, `scrollbar-color`), verify `1440x900` and `390x844` renders, and confirm `0` P0/P1 defects.

## Technical audit rubric (24-point health score)

During `/unmistakable audit`, score each dimension `0-4` (`0 = Critical`, `1 = Major gaps`, `2 = Partial`, `3 = Good`, `4 = Production-grade`) and tag every concrete finding `P0` (blocking), `P1` (major / WCAG AA or CWV failure), `P2` (minor), or `P3` (polish):

| # | Dimension | Score (0-4) | Key Evidence Checked |
|---|---|---|---|
| 1 | **Accessibility (WCAG 2.2 AA)** | `? / 4` | Contrast `>= 4.5:1`, native `<button>`/`<a>`, labels, `:focus-visible`, `>= 24px` (`44px` primary) touch targets, `prefers-reduced-motion` |
| 2 | **Performance & Core Web Vitals** | `? / 4` | Eager LCP media (`fetchpriority="high"`), explicit media dimensions (`CLS`), explicit transition properties, no layout thrash (`INP`) |
| 3 | **Theming, Tokens & Graphic Coherence** | `? / 4` | Semantic CSS variables (`--color-*`), zero scattered hex drift, coherent light/dark polarity, themed browser surfaces, one icon family with token strokes and `currentColor`, every micrographic named in `DESIGN.md` |
| 4 | **Responsive, Overflow & i18n/RTL** | `? / 4` | `min-width: 0`, `>= 16px` mobile inputs, `200%` text zoom, logical CSS (`inline`/`block`), `Intl` formatting, pointer-cancel safety |
| 5 | **Technical SEO & AI GEO** | `? / 4` | Landmarks (`<main>`), single `<h1>`, title/description/canonical, `1200x630` OG card, Schema.org JSON-LD, answer-first prose, `llms.txt` |
| 6 | **Implementation Integrity (Anti-Slop)** | `? / 4` | Mode-matched first viewport, 2-family / 3-size body scale, flat depth model (no gradients, glows, glass, heavy shadows, stock purple), zero eyebrows/nested cards/filler copy/invented proof, slop tell count `<= 1` |
| **Total** | **Audit Health Score** | **`?? / 24`** | **`21-24` Unmistakable · `16-20` Solid · `11-15` Drifted · `0-10` Slop/Fragile** |

Always lead the report with the **Implementation Integrity Verdict** (`Pass` / `Fail`), followed by the score table, `P0 -> P3` findings (`file:line`, user impact, concrete fix, and recommended `/unmistakable <command>`), and positive strengths worth preserving.

## Critique rubric (UX and visual direction review)

Run `/unmistakable critique` independent of mechanical linter noise first, answering five design-director tests with specific visual or DOM evidence:
1. **The Memory Test:** If a visitor closes the tab after 5 seconds on the first viewport, what single image, tool, or typographic statement do they remember?
2. **The Competitor Swap Test:** If you swapped the brand name with a rival in the same category, would the palette, copy specifics, and layout still fit? If yes, the direction is generic.
3. **The Squint Test:** With the screen blurred, do the primary focal point, primary action, and section cadence separate cleanly?
4. **Surface Mode Honesty:** Did an `Operate` or `Read` screen accidentally get buried under a marketing hero, or did a `Persuade` page collapse into a `50/50` template and 3-column icon cards?
5. **State Completeness:** What happens on empty data, 120-character strings, slow networks, and `390px` mobile screens?
6. **The Belongs Test:** Can every graphic on screen be named from the `DESIGN.md` motif inventory, drawn with its stroke and color tokens? Each unnamed mark is a coherence finding.
7. **The Tell Count:** Score the 60-second slop review from `references/anti-patterns.md`. `2+` tells on the first viewport means the direction reads as default output regardless of polish.

## Foundations roadmap (18 ship-readiness gates)

`python3 scripts/check_foundations.py <project-root>` checks 18 production gates offline (`checked`, `failing`, or `not_applicable`):
1. `secrets-out-of-repo` - No private keys or live secret values tracked in repo files (never echo a detected secret value).
2. `design-tokens` - Semantic CSS custom properties (`--color-*` or `@theme`) defined and consumed via `var()`.
3. `no-ai-slop-patterns` - Zero `P0`/`P1` anti-slop or accessibility errors from `scripts/detect_slop.py`.
4. `reduced-motion-guard` - Animations/transitions paired with `@media (prefers-reduced-motion: reduce)`.
5. `semantic-landmarks` - `<main>`, `<header>`/`<nav>`, and sequential `<h1>` structure present on web entry templates.
6. `not-found-route` - Custom 404 route (`not-found.tsx`, `404.astro`, `+error.svelte`, `error.vue`, `404.html`, or wildcard route).
7. `app-icons` - Favicon / app icon assets (`favicon.svg`, `favicon.ico`, `apple-touch-icon.png`, or manifest icons) present.
8. `social-previews` - `og:image` and `twitter:image` (or framework `openGraph.images` / `opengraph-image.*`) configured.
9. `canonical-and-meta` - `<title>`, meta description, and canonical URL configured in app shell or route metadata.
10. `structured-data-jsonld` - Valid `application/ld+json` Schema.org metadata present on public web surfaces.
11. `robots-and-sitemap` - `robots.txt` and `sitemap.xml` (or framework route generators `robots.ts` / `sitemap.ts`) present.
12. `llms-geo-index` - `llms.txt` present at root or `public/llms.txt` for AI Answer Engine discovery.
13. `legal-routes` - Privacy and terms routes or links when user data/auth is present.
14. `readme-commands` - `README.md` documents runnable install/build/test commands matching `package.json` or repo scripts.
15. `ci-verification` - `.github/workflows/*.yml` (or CI config) executes tests or static checks on push/PR.
16. `no-giant-files` - Hand-authored UI source files stay under `1,000` lines for maintainable modularity.
17. `ai-search-crawlers` - A static robots.txt does not fully block search or AI answer agents (`Googlebot`, `Bingbot`, `OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`); training-only crawlers may be blocked.
18. `icon-system` - Exactly one icon family across source imports and `package.json` (outline and solid variants of one family count once; `react-icons` sub-packages count separately).

## Deterministic 57-rule catalog (UNM-01 to UNM-57)

`scripts/detect_slop.py` enforces 57 rules across markup, stylesheets, inline styles, JSX style objects, and Tailwind utilities. Gate CI on a severity with `--fail-on P1`. Suppress a verified intentional exception on one line or file with `<!-- unmistakable-disable UNM-XX: reason -->` or `/* unmistakable-disable UNM-XX: reason */`.

| ID | Sev | Scope | Rule Summary |
|---|---|---|---|
| `UNM-01` | P1 | Slop | Pre-heading `.eyebrow` / `.kicker` micro-label element perched above `<h1>`-`<h3>` |
| `UNM-02` | P2 | Slop | Decorative `01 / 02 / 03` or bracketed `[01]` prefix inside headings |
| `UNM-03` | P2 | Slop | Gradient text (`background-clip: text` + transparent fill) used as display decoration |
| `UNM-04` | P1 | Slop | Nested bordered card inside another card container |
| `UNM-05` | P2 | Slop | One-sided thick accent border (`border-left: 3px/4px solid`) on a rounded box |
| `UNM-06` | P2 | Slop | Zero-offset neon glow halo (`box-shadow: 0 0 20px <color>`) used as generic chrome |
| `UNM-07` | P2 | Slop | Purple-to-blue/cyan/pink AI cliche gradient (CSS colors in any format, or Tailwind `from-`/`to-` stops) |
| `UNM-08` | P2 | Slop | Fake telemetry badge (`LIVE` pulsing dot or `SCROLL DOWN` cue) |
| `UNM-09` | P2 | Copy | Generic AI marketing filler (*seamless*, *elevate*, *reimagined*, *unleash*, *supercharge*, *cutting-edge*, *effortless*, *world-class*) |
| `UNM-10` | P2 | Copy | Headline split mid-thought with `<br><em>` italic cliché |
| `UNM-11` | P3 | Copy | Em-dash (`U+2014`) in generated UI markup copy |
| `UNM-12` | P2 | Copy | Placeholder `lorem ipsum` or dummy `example@example.com` shipped in UI |
| `UNM-13` | P2 | Type | More than `2` distinct font families declared in a single stylesheet |
| `UNM-14` | P2 | Type | More than `5` distinct font-size declarations in component styles (violates 3-size body discipline) |
| `UNM-15` | P1 | Type | Micro-text `< 12px` (`< 0.75rem`) harming legibility |
| `UNM-16` | P1 | Forms | `<input>` / `<select>` / `<textarea>` font-size `< 16px` triggering iOS Safari forced zoom |
| `UNM-17` | P2 | Type | Tracked-out `text-transform: uppercase` combined with micro font-size |
| `UNM-18` | P1 | Perf | `transition: all` or `transition-all` animating layout properties |
| `UNM-19` | P2 | Motion | `ease-in` timing function on UI transition (feels sluggish on interaction start) |
| `UNM-20` | P1 | A11y | CSS `@keyframes` or transition stylesheet lacking `@media (prefers-reduced-motion: reduce)` |
| `UNM-21` | P2 | Perf | Broad `will-change` overused across multiple properties or universal selectors |
| `UNM-22` | P0 | A11y | Click handler (`onClick`, `@click`, `(click)`) on non-interactive `<div>` or `<span>` without role/tabIndex |
| `UNM-23` | P0 | A11y | `<img>` element missing `alt` attribute |
| `UNM-24` | P1 | CWV | `<img>` element missing explicit `width` and `height` (or CSS `aspect-ratio`), risking CLS |
| `UNM-25` | P1 | CWV | Above-the-fold hero image marked `loading="lazy"` (degrades LCP) |
| `UNM-26` | P0 | A11y | `outline: none` or `outline: 0` without a replacement `:focus-visible` indicator |
| `UNM-27` | P1 | A11y | Skipped heading hierarchy (`<h1>` jumping directly to `<h3>` or `<h4>`) |
| `UNM-28` | P1 | A11y | `<button>` with icon/SVG only and no accessible text or `aria-label` |
| `UNM-29` | P1 | A11y | Form `<input>` lacking associated `<label>`, `aria-label`, or `aria-labelledby` |
| `UNM-30` | P2 | Tokens | Scattered hardcoded hex color literals (`> 6` outside `:root` / `@theme` token blocks) |
| `UNM-31` | P2 | RTL | Physical `margin-left`/`right` or `padding-left`/`right` on `dir="rtl"` surface |
| `UNM-32` | P2 | Icons | Raw emoji used as icons in buttons, links, nav, headings, list items, labels, or table headers |
| `UNM-33` | P1 | SEO | Full HTML document missing `<html lang="...">` attribute |
| `UNM-34` | P1 | SEO | Full HTML document missing `<main>` landmark |
| `UNM-35` | P1 | SEO | Zero or multiple `<h1>` elements in a single page template |
| `UNM-36` | P1 | SEO | Full HTML `<head>` missing `<title>` or `<meta name="description">` |
| `UNM-37` | P2 | SEO | Full HTML `<head>` missing `<link rel="canonical">` |
| `UNM-38` | P2 | SEO | Full HTML `<head>` missing `og:image` OpenGraph social card |
| `UNM-39` | P2 | GEO | Public HTML document missing `<script type="application/ld+json">` structured data |
| `UNM-40` | P1 | SEO | Vague non-descriptive anchor text (`"click here"`, `"read more"`, `"learn more"` alone) or `<a>` without `href` |
| `UNM-41` | P2 | Slop | Decorative multi-color gradient on a background, button, border, or icon tile (neutral scrims and `mask-image` exempt) |
| `UNM-42` | P2 | Slop | Stock AI purple accent (Tailwind `indigo`/`violet`/`purple` 400-700 hex, rgb, OKLCH, or utility classes), once per file |
| `UNM-43` | P2 | Slop | Colored (chromatic) `box-shadow`, `drop-shadow`, or `text-shadow` glow, including `shadow-<color>-500/50` |
| `UNM-44` | P2 | Slop | Heavy or stacked shadow: blur `>= 48px`, spread `>= 16px`, `3+` blurred layers, or `shadow-2xl` |
| `UNM-45` | P2 | Slop | Glassmorphism: `backdrop-filter: blur()` or `backdrop-blur-*` outside modal scrims and `fixed inset-0` overlays |
| `UNM-46` | P2 | Slop | Blurred decorative orb: `filter: blur(>= 40px)` or `blur-2xl` / `blur-3xl` |
| `UNM-47` | P2 | Motion | Idle infinite animation not tied to loading (`float`, `glow`, `bounce`, `marquee`, gradient shift) |
| `UNM-48` | P3 | Sloppy | More than 3 distinct `border-radius` literals or `rounded-*` steps in one file |
| `UNM-49` | P3 | Sloppy | Off-grid spacing (`3+` odd px values or arbitrary `p-[13px]`) or `z-index >= 999` |
| `UNM-50` | P2 | Copy | Unverified social proof ("Trusted by 10,000+", "Join 50k+", "10K+ happy customers", star strings) |
| `UNM-51` | P1 | GEO | `application/ld+json` block that is invalid JSON or lacks `@context` |
| `UNM-52` | P2 | SEO | Relative or `http://` canonical, `og:url`, `og:image`, or `twitter:image` |
| `UNM-53` | P2 | SEO | Dead placeholder link (`href="#"` or `href="javascript:..."`) |
| `UNM-54` | P2 | Icons | Icon drift: more than 2 stroke weights or more than 3 sizes across inline SVG icons and icon components in one file |
| `UNM-55` | P2 | Icons | Hardcoded hex/rgb/hsl `fill`, `stroke`, or `color` inside an icon SVG or icon component (logos and flags exempt) |
| `UNM-56` | P2 | Icons | Imports from more than one icon family in one file (`react-icons` sub-packages count separately) |
| `UNM-57` | P2 | Slop | Stock illustration pack reference (unDraw, Storyset, Humaaans, DrawKit, Open Peeps, ManyPixels, Blush) |
