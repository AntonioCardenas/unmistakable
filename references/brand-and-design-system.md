# Brand Extraction, Design Systems, and A4 Brand Books

Evidence-first workflow for capturing product context (`PRODUCT.md`), documenting or extracting a brand's visual system (`DESIGN.md` + `design/tokens.css`), and producing two shareable, zero-build HTML/PDF artifacts: a scrollable `design/design-system.html` reference and a print-exact single-page `design/brand-book-a4.pdf`.

## Contents
- Core evidence rules
- Extraction workflow from URL, screenshot, or codebase
- PRODUCT.md and DESIGN.md schemas
- Output 1: design/tokens.css and tokens.json
- Output 2: design/design-system.html
- Output 3: design/brand-book-a4.html and PDF rendering
- Wordmark lockup patterns

## Core evidence rules

1. **Extract before asking.** Inspect the provided URL, screenshot, Figma export, SVG asset, or existing repository first; ask the user only for genuine gaps that cannot be observed.
2. **Zero invented brand details.** Colors, typefaces, product names, taglines, principles, and metrics come strictly from the reference or user confirmation. When a brand publishes no written design principles or sub-brand family, omit that section from `design-system.html` and `brand-book-a4.html` rather than filling it with invented slogans.
3. **Preserve exact logos.** Copy the brand's inline `<svg>` mark verbatim when present in the source. If the reference only has a raster logo (`png`/`webp`), reference that exact image file or ask the user for the vector SVG - NEVER redraw or approximate a brand mark from scratch.
4. **Match the brand's own language.** If the source brand is soft, rounded, and sunlit, keep its radii and light surfaces. If it is dense, monochrome, and sharp, preserve `0px-2px` corners. The HTML templates supply layout bones only.

## Extraction workflow from URL, screenshot, or codebase

1. **Gather source material:**
   - **Existing codebase (`document` / `system .`):** Read global stylesheets (`styles.css`, `globals.css`, `tailwind.config.*`, `@theme`), `<head>` font links (`next/font`, `@font-face`, Google Fonts), public SVG marks, and 2-3 representative screens.
   - **Live URL (`system <url>`):** Fetch HTML and linked stylesheets; extract `:root` custom properties, computed hex/OKLCH values, `<link rel="stylesheet">` font families, `<title>` / meta description tagline, and inline `<svg>` wordmark.
   - **Screenshot or Brand Brief (`system <image>`):** Inspect canvas background, surface elevation, primary/secondary/tertiary accents, serif/sans/mono proportions, corner radii, and border treatment.
2. **Confirm extraction concisely:** List extracted colors, fonts, surface polarity (light/dark/dual), tagline, and missing items in 5-8 lines. Proceed immediately once confirmed (or right away when the source is complete).
3. **Write synchronized artifacts:**
   - `PRODUCT.md` (when missing and product context is known)
   - `DESIGN.md` (human + agent source of truth)
   - `design/tokens.css` (framework-agnostic `:root` variables)
   - `design/design-system.html` (adapted from `assets/design-system-template.html`)
   - `design/brand-book-a4.html` -> `design/brand-book-a4.pdf` (adapted from `assets/brand-book-a4-template.html` and rendered via `scripts/render_brand_book.py`)

## PRODUCT.md and DESIGN.md schemas

Use these structures as sensible defaults; omit sections lacking source evidence.

### `PRODUCT.md` (durable product truth)

```markdown
# Product Context

## Identity & Audience
- **Name:** <Product or Brand Name>
- **Tagline:** <Exact 1-line value proposition>
- **Primary Audience:** <Who uses this, in what physical/work context>

## Surface Modes
- **Marketing (`/`):** Persuade
- **Workspace (`/app/*`):** Operate
- **Documentation (`/docs/*`):** Read

## Stack & Constraints
- **Framework & Styling:** <e.g., Next.js App Router + CSS Modules / Astro + Tailwind v4 / Angular Signals>
- **Target Viewports & Locales:** Desktop (`1440px`), Tablet (`768px`), Mobile (`390px`); LTR/RTL requirements
- **Non-Negotiables:** <Accessibility level, performance budgets, legal/compliance notes>
```

### `DESIGN.md` (durable visual authority)

```markdown
# Design System: <Brand Name>

## Visual Thesis & Anti-References
- **Physical Scene:** <1 sentence grounding light/dark polarity and material character>
- **Color Strategy:** <Restrained | Committed | Color-Blocked>
- **Anti-References:** <Explicit patterns to refuse for this brand>

## Color Tokens
| Token | Value | Role & Contrast Note |
|---|---|---|
| `--color-bg` | `<hex/oklch>` | Primary page canvas |
| `--color-surface` | `<hex/oklch>` | Elevated container or panel |
| `--color-text` | `<hex/oklch>` | Primary copy (`>= 7:1` on `--color-bg`) |
| `--color-text-muted` | `<hex/oklch>` | Secondary metadata (`>= 4.5:1` on `--color-bg`) |
| `--color-border` | `<hex/oklch>` | `1px` structural hairline |
| `--color-primary` | `<hex/oklch>` | Primary action & focus ring |
| `--color-secondary` | `<hex/oklch>` | Supporting semantic accent |

## Typography (Max 2 Families, 3 Body Steps)
- **Display Family:** `<Family Name>`, weights `<weights>`, tracking `-0.03em`
- **Body Family:** `<Family Name>`, weights `<weights>`, `font-variant-numeric: tabular-nums`
- **Scale:** Display `clamp(...)` · Step 1 (`--text-heading`) · Step 2 (`--text-body: 1rem`) · Step 3 (`--text-sm: 0.875rem`)

## Spatial & Control Language
- **Spacing Unit:** `4px` (`0.25rem`) base; section separation `clamp(3.5rem, 7vw, 6rem)`
- **Radii & Depth:** `--radius-sm: <val>`, `--radius-md: <val>`, `1px` solid borders
- **Motion:** `160ms cubic-bezier(0.22, 1, 0.36, 1)` on `transform` and `opacity`; reduced-motion safe
```

## Output 1: design/tokens.css and tokens.json

Write `design/tokens.css` with `:root` custom properties matching `DESIGN.md` so any framework can `@import` it immediately. When a cross-platform pipeline (Style Dictionary, Figma Tokens, iOS/Android) is present, also emit W3C Design Tokens Community Group format in `design/tokens.json` (`{"color": {"primary": {"$value": "#...", "$type": "color"}}}`).

## Output 2: design/design-system.html

Start from `assets/design-system-template.html` and replace every `{{TOKEN}}` placeholder. Keep the file 100% self-contained (font `<link>`, inline `<style>`, inline `<svg>`, zero build step). Include sections in this order, dropping any section without verified source data:

1. **Masthead:** Brand lockup, tagline, version, and source attribution.
2. **Color Hierarchy & Extended Palette:** Primary, secondary, tertiary, and canvas/surface swatches with hex/OKLCH codes and WCAG contrast notes.
3. **Typography & 3-Size Body Ladder:** Live specimens for `--text-display`, `--text-heading`, `--text-body` (`tabular-nums`), and `--text-sm`.
4. **Principles:** Documented brand rules (omit if undocumented).
5. **Core Controls & States:** Primary button (`>= 44px` height), segmented mode control (`aria-pressed`), and `16px` input with themed `:focus-visible` and `::selection`.
6. **Icons & Wordmark Lockups:** Brand SVG icon style and applicable wordmark treatments.

## Output 3: design/brand-book-a4.html and PDF rendering

Start from `assets/brand-book-a4-template.html` (`210mm x 297mm`, `@page { size: A4 portrait; margin: 0; }`, `print-color-adjust: exact`). Keep copy concise so the entire sheet fits onto **exactly 1 A4 portrait page** without vertical overflow.

Run the cross-platform renderer script to produce `design/brand-book-a4.pdf`:

```bash
python3 scripts/render_brand_book.py design/brand-book-a4.html design/brand-book-a4.pdf
```

`scripts/render_brand_book.py` locates headless Google Chrome, Chromium, Brave, or Microsoft Edge across macOS, Linux, and Windows, prints `design/brand-book-a4.pdf` with `--no-pdf-header-footer`, and verifies that the generated PDF is non-empty and fits a single page (`Exit 0`). If the script reports page count `> 1`, tighten `.page` vertical gaps or drop an optional row in `design/brand-book-a4.html` and re-run.

## Wordmark lockup patterns

Include only lockup treatments that fit the brand's actual name structure:
- **Mark + wordmark:** Exact brand SVG beside the wordmark in matching optical weight and tracking.
- **Split-weight lockup (`PART1PART2`):** Heavy primary stem paired with lighter descriptor stem for multi-word or group names (skip for short single-word brands).
- **Accent lockup:** Primary brand color applied to one semantic half of a studio or product-family name.
