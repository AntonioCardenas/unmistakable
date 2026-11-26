# Agnostic Frontend Design Patterns

Framework-agnostic architectural rules for building web interfaces that feel authored by a human design studio rather than assembled from statistical model defaults. Every pattern uses standard HTML, CSS Custom Properties, and progressive browser APIs so it maps cleanly onto React, Next.js, Vue, Nuxt, SvelteKit, Astro, Angular, Solid, Web Components, Tailwind CSS, or plain HTML.

## Contents
- Visitor modes and opening viewport fit
- The 6-block direction contract
- Color beyond beige and neon purple
- Agnostic 3-tier token architecture
- 2-family, 3-size typographic discipline and optical alignment
- Spatial choreography and layout rhythm
- Calibrated motion and custom imagery
- Craft floor

## Visitor modes and opening viewport fit

Pick the visitor mode for the specific route or screen before choosing layout:

| Mode | Typical Surfaces | Opening Viewport Rule |
|---|---|---|
| **Persuade** | Brand sites, launches, product marketing, storefronts, pricing | Commit to a bold full-viewport opening (`y = 0` behind a single-line borderless header), `<= 25` words of supporting copy, and `1` primary CTA. |
| **Operate** | Dashboards, admin consoles, SaaS workspaces, editors, settings, calculators | Skip marketing hero banners completely. Open at `y = 0` directly into live controls, workspace state, or data tables. |
| **Read** | Docs, technical guides, blogs, changelogs, news indexes, resumes | Open directly into the masthead, table of contents, or story grid with a `45ch-68ch` reading measure. |
| **Experience** | Portfolios, lookbooks, interactive installations, galleries | Let the visual artifact, canvas, or interactive stage command the first viewport while interface chrome recedes. |

### Four non-split opening directions for Persuade and Experience

Abandon the boilerplate `50/50` split hero (`left H1 + long paragraph + 2 buttons + divider + 3-4 KPI stat strip` next to a boxed right-hand mockup). Trapping `<h1>` in a half-column shrinks its authority. Adapt or combine spatial compositions such as:

1. **Centered monumental headline + wide live workbench:** Display `<h1>` spanning `70%-92%` of the viewport, `1-2` concise lines (`<= 25` words), and one primary action rising above an `80%-100%` interactive preview stage visible above the fold.
2. **Full-bleed photographic or canvas takeover:** Edge-to-edge (`width: 100%`, `min-height: 100dvh`) art-directed photography or WebGL/Canvas stage from `top: 0` behind a single-line transparent header, with typography anchored in a composed negative-space clearing.
3. **Layered foreground depth (`z-index` occlusion):** Monumental display lettering spanning edge-to-edge behind a cutout physical product or interactive sculptural object, with concise copy and primary CTA anchored along the lower horizon.
4. **Chromatic poster choreography:** Tightly stacked oversized poster type (`line-height: 0.92-1.0`) over bold color-blocked fields or asymmetric architectural grid tension.

Keep desktop navigation on one compact horizontal line, giving the brand wordmark stronger visual weight than nav links. When a header stays sticky on scroll, apply clean surface separation (`background` + `1px` border) only once scrolled so content does not collide behind nav text.

## The 6-block direction contract

Before writing UI code for a new surface or redesign, record a compact ~150-word contract in `DESIGN.md` or a local surface brief (`NEVER` inside shipped HTML comments, DOM attributes, client bundles, or JSON-LD):

- **THESIS:** The single memorable idea this surface owns and the category cliché it refuses.
- **OWN-WORLD:** Physical scene (who uses it, where, under what ambient light), material palette, control vocabulary, and the 5-9 micrographic motifs drawn from that world, recognizable even with all text blurred.
- **FIRST VIEWPORT:** Exact opening composition, scale, and primary action placement.
- **STATES & A11Y:** Loading, empty, error, hover, `:focus-visible`, and `prefers-reduced-motion` behavior.
- **SEO & GEO:** Primary entity, single `<h1>` intent, Schema.org type, and answer-first proof structure (mark `N/A - authenticated workspace` for private app screens).
- **FINISH:** Exit criteria: `0` P0/P1 findings in `scripts/detect_slop.py`, token synchronization in `DESIGN.md`, and verified desktop + mobile viewports.

## Color beyond beige and neon purple

Models left unguided converge on two overused palettes:
1. Warm cream/parchment ground + high-contrast italic serif + rust/terracotta accent (triggered whenever a prompt mentions *craft*, *editorial*, *food*, *bookish*, or *warm*).
2. Slate-black `#0f172a` ground + glowing purple-to-cyan gradients + glassmorphic borders (triggered whenever a prompt mentions *AI*, *developer*, *fintech*, or *modern*).

A third prior sits under both: the Tailwind `indigo-500`/`violet-500` accent with colored glows, glass panels, and blurred orbs. Unless the user's brand explicitly pins those colors, treat all three priors as spent. Choose a color strategy first:
- **Restrained** (best for `Operate` and `Read`): neutrals subtly tinted from the domain's hue (`chroma 0.01-0.02` in OKLCH) plus one unmistakable action accent.
- **Committed** (`Persuade` / `Experience`): one saturated brand field carries `30%-60%` of the viewport rather than tiny accent sprinkles.
- **Chromatic Color-Blocking**: deep forest, marine ink, cobalt, mineral stone, oxidized copper, international vermilion, or crisp gallery daylight derived from real domain materials.

Tint muted text from the background's hue rather than neutral mid-gray, and verify `>= 4.5:1` contrast for body/placeholder text and `>= 3:1` for large display text (`>= 24px` or `>= 18.66px` bold).

## Agnostic 3-tier token architecture

Author tokens once in standard CSS Custom Properties (`design/tokens.css` or `:root`), separating **Primitive**, **Semantic**, and **Component** roles so dark mode, brand updates, and multi-framework consumption require zero component rewrites:

```css
:root {
  /* Tier 1: Primitives (raw palette & scale) */
  --ink-950: oklch(0.16 0.015 255);
  --ink-800: oklch(0.26 0.015 255);
  --stone-100: oklch(0.96 0.008 85);
  --stone-200: oklch(0.91 0.012 85);
  --vermilion-600: oklch(0.61 0.215 34);

  /* Tier 2: Semantic roles (consumed by layouts & components) */
  --color-bg: var(--stone-100);
  --color-surface: oklch(0.985 0.004 85);
  --color-surface-raised: oklch(1 0 0);
  --color-text: var(--ink-950);
  --color-text-muted: oklch(0.42 0.015 255); /* >= 4.5:1 against --color-bg */
  --color-border: var(--stone-200);
  --color-accent: var(--vermilion-600);
  --color-accent-contrast: oklch(0.99 0.005 85);

  /* Spacing (4px base with mid-steps) & Radii */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --radius-sm: 0.375rem;
  --radius-md: 0.625rem;
  --radius-lg: 1rem;

  /* Depth: borders and surface steps first; this shadow is for floating layers only */
  --shadow-overlay: 0 1px 2px oklch(0 0 0 / 0.06), 0 8px 24px oklch(0 0 0 / 0.08);
  --z-header: 10;
  --z-overlay: 40;
  --z-toast: 50;
}

[data-theme="dark"] {
  --color-bg: oklch(0.15 0.012 255);
  --color-surface: oklch(0.20 0.014 255);
  --color-surface-raised: oklch(0.25 0.016 255);
  --color-text: oklch(0.95 0.006 85);
  --color-text-muted: oklch(0.72 0.012 255);
  --color-border: oklch(0.29 0.015 255);
}
```

### Mapping across frameworks without lock-in
- **Tailwind CSS v4:** Map semantic variables inside `@theme inline { --color-canvas: var(--color-bg); --color-ink: var(--color-text); }` so utilities (`bg-canvas`, `text-ink`) inherit theme switching automatically.
- **React / Next.js / Solid:** Import `tokens.css` once in the root layout; pass semantic tokens to CSS Modules, Tailwind, or zero-runtime style objects rather than hardcoding hex literals in JSX.
- **Vue / Nuxt / SvelteKit / Astro:** Import `tokens.css` in the app shell; scoped `<style>` blocks read `var(--color-*)` directly across component boundaries and Shadow DOM.
- **Angular:** Declare tokens on `:root` in `styles.css`; Signals-driven components toggle `document.documentElement.dataset.theme` with zero runtime style recalculation loops.

## 2-family, 3-size typographic discipline and optical alignment

1. **At most 2 font families:** Pair one expressive display face with one legible UI/body face, or commit to a single variable grotesque/serif across weights. Avoid unexamined training-data reflexes (`Inter` as display, `Space Grotesk` + `Space Mono`, `Playfair Display` + `Lora`) unless the brand pins them. Do not load a 3rd monospace font solely for prices, counters, or timestamps - apply `font-variant-numeric: tabular-nums` to your body font unless building a developer, CLI, or documentation product.
2. **At most 3 body font-size steps below the hero:**
   - `--text-heading` (section `<h2>`, e.g. `clamp(1.5rem, 2.5vw, 2.25rem)`)
   - `--text-body` (`1rem` / `16px` floor on mobile; consistent across all body `<p>` and `<ul>`/`<ol>` items - do not place an oversized `.lead` paragraph above smaller body paragraphs)
   - `--text-sm` (`0.875rem` / `14px` for secondary metadata; `0.8125rem` / `13px` absolute floor above the fold)
   - Allow a 4th compact step (`0.75rem`) only when building dense multi-column data tables or financial consoles. Hero `<h1>` and navbar brand wordmark are exempt from the 3-size body limit. Differentiate `<h3>`, buttons, and table headers through weight (`600`), family, and color rather than inventing `18px`, `20px`, and `22px` steps.
3. **Line breaks, dark-surface compensation, and optical trim:**
   - Set `text-wrap: balance` on headings (`letter-spacing: -0.02em` to `-0.04em`) and `text-wrap: pretty` on body prose (`max-width: 45ch-68ch`).
   - Use **sentence case** for navigation, buttons, form labels, and table headers.
   - On dark backgrounds, compensate light text by adding `+0.05` line-height and `+0.005em` tracking so halation does not blur letterforms.
   - For crisp optical button centering in modern browsers, apply `text-box: trim-both cap alphabetic` to an inner `<span style="display:block">` inside `inline-flex` buttons, paired with `@font-face { size-adjust: ... }` on the fallback font to eliminate font-swap layout shift.

## Spatial choreography and layout rhythm

- **Proximity before containers:** Group related items via tight spacing (`--space-2` to `--space-3`) and separate distinct groups with generous intervals (`--space-12` to `--space-16`), always leaving more space above a heading than below it (`margin-block: 2.5rem 0.75rem`). Use whitespace, `1px` hairlines, or subtle surface tint instead of wrapping every group in a bordered card.
- **Vary section pacing below the fold:** Sustain opening-screen craft all the way to the footer by alternating full-bleed stages, interactive proof instruments, asymmetric `7/5` editorial splits, and quiet reading passages rather than dropping into uniform 3-column icon-card grids.
- **Single primary action per content block:** Give marketing sections at most one primary CTA button. When users switch modes, billing intervals, sizes, or filters, use segmented controls (`role="group"` / tabs / radios / `<select>`), not walls of competing bordered buttons.

## Calibrated motion and custom imagery

- **Transitions:** Name explicit GPU-friendly properties (`transition: transform 180ms cubic-bezier(0.22, 1, 0.36, 1), opacity 180ms cubic-bezier(0.22, 1, 0.36, 1)`). Avoid `transition: all`, `ease-in` on UI entrances, idle bobbing loops, and elements initialized at `opacity: 0` without a CSS/no-JS fallback.
- **Reduced motion:** Provide an intentional `@media (prefers-reduced-motion: reduce)` path that removes spatial translation and parallax while preserving instant opacity or color state feedback.
- **Imagery:** Skip decorative stock photos inside `Operate` workspaces. When imagery earns its place, generate or source domain-specific assets saved on project-relative paths with explicit `width`, `height`, and `aspect-ratio` matching the CSS container, leaving clean negative space behind overlaid headlines so WCAG AA contrast holds without muddy full-screen black scrims. Never invent unverified external image URLs.

## Craft floor

Before calling any UI edit complete, theme what the browser leaves ugly (the banned-pattern list lives in `references/anti-patterns.md`):

- Custom `::selection` using `--color-accent` and `--color-accent-contrast`.
- `caret-color: var(--color-accent)` on text inputs and editors.
- `:focus-visible` ring (`2px solid var(--color-accent)`, `outline-offset: 2px`) on every interactive control.
- `scrollbar-color` and `color-scheme: light dark` matched to the active theme.
- `text-underline-offset: 0.2em` and `text-decoration-thickness: 1px` on inline prose links.
- One control height token shared by buttons, inputs, and selects in the same row.
- A named layering scale (`--z-header`, `--z-overlay`, `--z-toast`) instead of escalating `z-index` literals.
