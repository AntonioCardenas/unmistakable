---
name: unmistakable
description: "Designs, builds, audits, and hardens production web interfaces without generic AI slop: no purple gradients, neon glows, glassmorphism, heavy shadows, eyebrow pills, 50/50 heroes, mixed icon sets, stock illustrations, or invented social proof. Keeps icons and micrographics in one graphic language with the design system. Also extracts living design systems and 1-page A4 brand books, and ships technical SEO plus GEO (AI answer-engine visibility). Use when building or redesigning websites, landing pages, dashboards, components, or design systems in React, Next.js, Vue, Nuxt, Svelte, Astro, Angular, Tailwind, or plain HTML/CSS; when a UI looks generic, templated, or AI-generated; or when asked to audit UI quality, extract brand tokens, fix accessibility or Core Web Vitals, or improve search and AI citation visibility (JSON-LD, robots.txt for AI crawlers, llms.txt)."
license: MIT
compatibility: "Framework-agnostic (React, Next.js, Vue, Nuxt, SvelteKit, Astro, Angular, Solid, Web Components, Tailwind CSS, vanilla HTML/CSS). Bundled scripts use Python 3.8+ standard library only."
metadata:
  author: Antonio Cardenas
  version: "1.2.0"
  repository: "https://github.com/AntonioCardenas/unmistakable"
---

# Unmistakable

Unmistakable turns generic AI-generated interfaces into committed, production-ready frontend engineering with verifiable brand systems, resilient states, and search-ready semantic markup. Treat this file as the router: lock the surface mode and standing rules first, then open only the reference file or script required for the active job.

## Standing Rules

1. **Honor the brief or derive from real materials.** Follow explicit brand tokens, palettes, eras, and typefaces in `DESIGN.md` or the user's brief. When the aesthetic is open, derive color, contrast, and rhythm from the subject's physical scene and domain materials. Three priors are spent: warm beige/terracotta with display serifs, dark slate with neon glow, and the Tailwind `indigo`/`violet` accent.
2. **Match the opening viewport to the visitor mode.** Choose the mode per route, not per company:
   - **Persuade** (landing pages, launches, pricing, storefronts): commit to a bold, full-viewport opening (`y = 0` behind a single-line header), `<= 25` words of supporting copy, and one primary action. Skip the `50/50` split hero and bottom stat strip.
   - **Operate** (dashboards, admin, editors, consoles, settings, utility tools): skip marketing hero banners completely; open directly into live workspace controls, data density, and keyboard-ready affordances.
   - **Read** (docs, blogs, changelogs, news, guides, CVs): open directly into the masthead, typographic sheet, or story grid with a `45ch-68ch` measure.
   - **Experience** (portfolios, showcases, interactive stories): let the canvas, imagery, or interactive work occupy the first viewport while UI chrome recedes.
3. **Keep light and depth flat and honest.** Default to solid surfaces: no decorative gradients, no gradient text, no colored or zero-offset glow shadows, no glassmorphism, no blurred orbs, and no idle animation loops. Depth comes from `1px` borders and surface tint steps; one neutral `--shadow-overlay` token is reserved for layers that genuinely float (menus, popovers, dialogs, toasts). Resting cards get no shadow. Exceptions exist only when `DESIGN.md` or the brief pins them, recorded as a waiver with a reason.
4. **Speak one graphic language.** Micrographics (icons, markers, dividers, callouts, status glyphs, small data graphics, spot illustrations, social cards, favicons) come from the motif inventory in `DESIGN.md` and are drawn with its tokens: one icon family, one stroke weight per size, at most `3` icon sizes, `currentColor` instead of literal colors, and motifs derived from the OWN-WORLD. Anything `DESIGN.md` cannot name does not ship: no emoji icons, sparkles, stock illustration packs, second icon libraries, or generated art in a different style. See [references/micrographics.md](references/micrographics.md).
5. **Hold strict typographic and structural discipline.** Use at most `2` font families (`font-variant-numeric: tabular-nums` on the body font instead of a decorative 3rd monospace font unless building a code or terminal tool) and at most `3` body font-size steps below the hero (`4` only for dense data tables). Start sections directly with `<h1>` or `<h2>`: no pre-heading eyebrow labels, no non-interactive category chips, no `01 / 02` decorative numbering, no button walls, no cards nested inside cards, and at most `3` radius steps.
6. **Never invent facts.** Source colors, fonts, taglines, principles, and exact SVG logos from the user's URL, screenshot, or codebase. Never fabricate metrics, ratings, testimonials, customer counts, or logos ("Trusted by 10,000+"); when proof is missing, leave the slot out and say so. Ask only for genuine gaps and omit unsourced sections.
7. **Keep development contracts out of shipped code.** Record surface strategy in `PRODUCT.md` or `DESIGN.md`, NEVER inside HTML comments, hidden DOM nodes, `data-*` attributes, serialized component props, or JSON-LD payloads.
8. **Verify mechanically and visually.** Run `scripts/detect_slop.py` and `scripts/check_foundations.py` on modified targets, score the 60-second slop review in [references/anti-patterns.md](references/anti-patterns.md), and inspect rendered desktop (`1440x900` opening + scrolled sections) and mobile (`390x844`) viewports when a browser tool is available.

## Command Router

Invoke as `/unmistakable <command> [target]` (or `$unmistakable` in Codex). With no command, infer the narrowest matching workflow below or present the four groups as a compact menu.

| Group | Command | Job | Reference / Script to Open |
|---|---|---|---|
| **System & Setup** | `init` | Capture product audience, surface modes, and stack in `PRODUCT.md` | [references/brand-and-design-system.md](references/brand-and-design-system.md) |
| **System & Setup** | `system [ref]` | Extract brand from URL/screenshot/code into `DESIGN.md`, `design/tokens.css`, `design/design-system.html`, and `design/brand-book-a4.pdf` | [references/brand-and-design-system.md](references/brand-and-design-system.md) + `scripts/render_brand_book.py` |
| **System & Setup** | `document` | Reverse-engineer an existing codebase's visual system into `DESIGN.md` and `design/tokens.css` | [references/brand-and-design-system.md](references/brand-and-design-system.md) |
| **System & Setup** | `extract [target]` | Consolidate repeated inline styles or utility classes into semantic design tokens | [references/agnostic-design-patterns.md](references/agnostic-design-patterns.md) |
| **Build & Steer** | `shape [feature]` | Write the 6-block Direction Contract and UX topology before writing UI code | [references/agnostic-design-patterns.md](references/agnostic-design-patterns.md) |
| **Build & Steer** | `build [target]` | Build a new page, workspace, or component end-to-end with anti-slop, a11y, and SEO/GEO gates | [references/agnostic-design-patterns.md](references/agnostic-design-patterns.md) + [references/anti-patterns.md](references/anti-patterns.md) |
| **Build & Steer** | `deslop [target]` | Strip AI tells: gradients, glows, glass, heavy shadows, stock purple, eyebrow pills, filler copy, invented proof, idle motion, radius and spacing drift | [references/anti-patterns.md](references/anti-patterns.md) + `scripts/detect_slop.py` |
| **Build & Steer** | `graphics [target]` | Unify micrographics: one icon family, token strokes and sizes, `currentColor`, motifs from the `DESIGN.md` inventory; remove anything it cannot name | [references/micrographics.md](references/micrographics.md) + `scripts/detect_slop.py` |
| **Build & Steer** | `typeset` / `layout` / `colorize` / `animate` | Targeted pass on 3-size type math, spatial proximity rhythm, token contrast, or `140ms-240ms` motion | [references/agnostic-design-patterns.md](references/agnostic-design-patterns.md) |
| **Build & Steer** | `bolder` / `quieter` / `distill` | Scale visual conviction up, calm visual noise down, or strip filler chrome to its essence | [references/commands-and-audit-rubric.md](references/commands-and-audit-rubric.md) |
| **Evaluate** | `audit [target]` | Run `scripts/detect_slop.py` and score 6 technical dimensions (`0-24`) ranked `P0-P3` without editing | [references/commands-and-audit-rubric.md](references/commands-and-audit-rubric.md) + `scripts/detect_slop.py` |
| **Evaluate** | `critique [target]` | Design-director UX review: memory, competitor swap, squint, mode fit, state completeness, and tell count, then top 3 high-leverage fixes | [references/commands-and-audit-rubric.md](references/commands-and-audit-rubric.md) + [references/anti-patterns.md](references/anti-patterns.md) |
| **Harden & Ship** | `harden [target]` | Harden overflow, `16px` mobile inputs, RTL/i18n, Arabic ZWNJ/`Intl`, error recovery, and interrupted gestures | [references/production-hardening.md](references/production-hardening.md) |
| **Harden & Ship** | `optimize [target]` | Fix Core Web Vitals (`LCP < 2.5s`, `INP < 200ms`, `CLS < 0.1`), font loading, and DOM containment | [references/production-hardening.md](references/production-hardening.md) |
| **Harden & Ship** | `seo [target]` | Implement landmarks, the head contract, validated Schema.org JSON-LD, answer-first GEO passages, AI crawler access, `sitemap.xml`, and `llms.txt` | [references/seo-and-geo-patterns.md](references/seo-and-geo-patterns.md) |
| **Harden & Ship** | `foundations` | Run `scripts/check_foundations.py` across 18 ship-readiness gates and fix one item at a time | [references/commands-and-audit-rubric.md](references/commands-and-audit-rubric.md) + `scripts/check_foundations.py` |
| **Harden & Ship** | `polish [target]` | Final ship pass: clear detector findings, theme browser surfaces, verify viewports, and confirm `0` P0/P1 issues and a tell count `<= 1` | [references/commands-and-audit-rubric.md](references/commands-and-audit-rubric.md) + [references/anti-patterns.md](references/anti-patterns.md) |

## Primary Workflows

### Workflow A: New Surface or Redesign (`build`)

Copy this checklist into your working plan and tick items as they pass:

```text
Unmistakable build progress:
- [ ] Step 1: Context & Mode locked (PRODUCT.md / DESIGN.md checked; Visitor Mode named)
- [ ] Step 2: Direction Contract recorded (THESIS, OWN-WORLD + motif inventory, FIRST VIEWPORT, STATES, SEO/GEO, FINISH)
- [ ] Step 3: Semantic & Token Architecture built (:root / @theme tokens, flat depth model, one graphic language, 3-size body scale, landmarks)
- [ ] Step 4: States, Hardening & SEO/GEO applied (loading/empty/error/focus, JSON-LD, zero-CLS media)
- [ ] Step 5: Mechanical & Visual Verification clean (detectors + slop tell count <= 1). If any check fails, return to Step 3.
```

- **Step 1 (Context):** Inspect existing framework conventions, CSS architecture, `PRODUCT.md`, and `DESIGN.md`. Preserve an established brand unless asked to redesign. Done when the Visitor Mode (`Persuade`, `Operate`, `Read`, `Experience`) and stack are stated in one line.
- **Step 2 (Direction Contract):** Read [references/agnostic-design-patterns.md](references/agnostic-design-patterns.md). Write a compact 6-block contract in `DESIGN.md` or a local surface brief (`THESIS`, `OWN-WORLD`, `FIRST VIEWPORT`, `STATES & A11Y`, `SEO & GEO`, `FINISH`). Done when someone could recognize the visual world with all copy removed.
- **Step 3 (Build):** Implement semantic HTML5 landmarks, framework-agnostic CSS custom properties, the flat depth model, micrographics from the `DESIGN.md` Graphic Language block ([references/micrographics.md](references/micrographics.md)), 2-family / 3-size typography, themed browser surfaces (`::selection`, `:focus-visible`, `caret-color`, `scrollbar-color`), and purposeful motion (`prefers-reduced-motion` guarded). Skim [references/anti-patterns.md](references/anti-patterns.md) before styling. Done when the surface renders real domain content with zero placeholder copy, invented proof, or banned chrome.
- **Step 4 (Harden & SEO/GEO):** Apply [references/production-hardening.md](references/production-hardening.md) (`min-width: 0` in flex/grid, logical spacing, `>= 44x44px` primary touch targets, interactive states) and, for public web routes, [references/seo-and-geo-patterns.md](references/seo-and-geo-patterns.md) (`<title>`, meta description, absolute canonical, OpenGraph, valid `application/ld+json`, answer-first headings). Done when all states and metadata are wired.
- **Step 5 (Verify):** Run `python3 scripts/detect_slop.py <target>` and `python3 scripts/check_foundations.py <project-root>`, then score the 60-second slop review. When a browser tool is available, inspect `1440x900` and `390x844` renders for contrast, overflow, and hierarchy. If any check fails, return to Step 3, fix findings in a single batch, and re-run until clean.

### Workflow B: Brand Extraction & Living Design System (`system`)

Copy this checklist when generating a design system and brand book:

```text
Design system progress:
- [ ] Step 1: Source extracted (hex colors, fonts, SVG logo, icon family and stroke, motifs, tagline, principles, surface polarity)
- [ ] Step 2: Gaps confirmed with user (zero invented brand claims or redrawn logos)
- [ ] Step 3: DESIGN.md, design/tokens.css, design/design-system.html, and design/brand-book-a4.html written
- [ ] Step 4: A4 PDF rendered via scripts/render_brand_book.py and verified. If layout overflows 1 page, return to Step 3.
```

Read [references/brand-and-design-system.md](references/brand-and-design-system.md) and adapt [assets/design-system-template.html](assets/design-system-template.html) and [assets/brand-book-a4-template.html](assets/brand-book-a4-template.html) to the extracted brand tokens, then run `python3 scripts/render_brand_book.py design/brand-book-a4.html design/brand-book-a4.pdf`.

### Workflow C: Audit, De-slop, Harden & Ship (`audit` -> `deslop` -> `harden` -> `seo` -> `polish`)

1. Run `python3 scripts/detect_slop.py <target> --json` and `python3 scripts/check_foundations.py <project-root> --json` (do not read the script source unless extending rules; running outputs compact JSON).
2. Score all 6 dimensions in [references/commands-and-audit-rubric.md](references/commands-and-audit-rubric.md) (`Accessibility`, `Performance & CWV`, `Theming & Tokens`, `Responsive & RTL`, `SEO & GEO Readiness`, `Implementation Integrity` for a `0-24` total), add the slop tell count from [references/anti-patterns.md](references/anti-patterns.md), and report `P0-P3` findings without editing during `audit`.
3. When asked to fix or run `deslop` / `polish`, resolve `P0` and `P1` issues and slop tells at the token and component layer, re-run `scripts/detect_slop.py`, and stop only when zero `P0`/`P1` findings remain and every remaining slop rule is fixed or waived with a reason.

## Bundled References and Scripts

- [references/agnostic-design-patterns.md](references/agnostic-design-patterns.md) - Visitor modes, opening-viewport choreography, 3-tier token architecture across frameworks, 2-family / 3-size typography, optical alignment, motion, and the craft floor.
- [references/anti-patterns.md](references/anti-patterns.md) - The AI-slop catalog: light and depth (gradients, glows, glass, shadows, stock purple), layout, typography, components, copy and invented proof, motion, sloppy craft, the 60-second slop review, and legitimate waivers.
- [references/micrographics.md](references/micrographics.md) - One graphic language: the Graphic Language block for `DESIGN.md`, motifs derived from the OWN-WORLD, icon system rules, micrographic tokens, data glyphs, spot art, generated-imagery prompt bases, and the belongs test.
- [references/brand-and-design-system.md](references/brand-and-design-system.md) - Evidence-first brand extraction, `PRODUCT.md` and `DESIGN.md` schemas, `design/tokens.css`, scrollable `design-system.html`, and 1-page `brand-book-a4.pdf` workflow.
- [references/production-hardening.md](references/production-hardening.md) - Overflow, i18n/RTL, Arabic ZWNJ and `Intl` formatting, network/API error recovery, pointer-gesture cancellation, WCAG 2.2 AA, and Core Web Vitals (`LCP`, `INP`, `CLS`).
- [references/seo-and-geo-patterns.md](references/seo-and-geo-patterns.md) - Landmarks, the head contract, Schema.org JSON-LD, passage-level GEO writing, entity signals, the AI crawler access matrix, `llms.txt` (and its limits), and measuring AI visibility.
- [references/commands-and-audit-rubric.md](references/commands-and-audit-rubric.md) - Execution playbooks for all 20 sub-commands, the 24-point Audit Health Score rubric, and the 57-rule deterministic catalog (`UNM-01` to `UNM-57`).
- [assets/design-system-template.html](assets/design-system-template.html) - Self-contained HTML/CSS living design system skeleton with `{{TOKEN}}` placeholders.
- [assets/brand-book-a4-template.html](assets/brand-book-a4-template.html) - Print-calibrated `210mm x 297mm` single-page A4 brand book skeleton.
- `scripts/detect_slop.py` - Run `python3 scripts/detect_slop.py <path> [--json] [--sarif] [--fail-on P1] [--list-rules]` to detect anti-slop, micrographic drift, sloppy-UI, a11y, motion, and SEO/GEO issues across CSS, markup, inline styles, icon imports, and Tailwind classes (`Exit 0` clean, `Exit 2` findings at or above `--fail-on`, `Exit 1` scan error).
- `scripts/check_foundations.py` - Run `python3 scripts/check_foundations.py <project-root> [--json]` to verify 18 production and SEO/GEO ship-readiness foundations, including AI crawler access and a single icon family.
- `scripts/render_brand_book.py` - Run `python3 scripts/render_brand_book.py <input.html> <output.pdf>` to render a print-exact A4 PDF via headless Chrome, Chromium, or Edge.
- [README.es.md](README.es.md) - Spanish overview and command reference when collaborating in Spanish.
