# Micrographics and Graphic Coherence

Micrographics are the small marks that carry a product's identity between the big moments: icons, pictograms, status glyphs, list markers, dividers and rules, callouts and leader lines, annotations, tiny data graphics (sparklines, meters, ticks), map pins, empty-state and spot illustrations, favicons, and the art in social cards. Generated UI falls apart here first, because each mark gets pulled from a different library, prompt, or habit until the screen is a collage. The rule is simple: every graphic on screen can be named from the motif inventory in `DESIGN.md` and is drawn with the system's tokens. If it cannot be named, it does not ship.

## Contents
- The coherence rule
- Define the graphic language in DESIGN.md
- Derive motifs from the OWN-WORLD
- Icon system
- Micrographic tokens
- Small data graphics and status glyphs
- Rules, dividers, markers, and annotations
- Spot illustrations and empty states
- Generated imagery
- Social cards, favicons, and brand assets
- The belongs test
- Anti-patterns

## The coherence rule

Every graphic passes three checks before it ships:

1. **Named.** It is an entry in the `DESIGN.md` motif inventory. A new motif is added to the inventory on purpose first, never improvised in a component.
2. **Drawn with tokens.** Stroke weight, size, corner treatment, grid, and color come from tokens (`--stroke-*`, `--icon-*`, `--radius-*`, `currentColor`, `--color-*`). No literal hex values, no one-off stroke widths.
3. **Same hand.** Placed next to any other graphic on the page, it looks drawn by the same person with the same pen: same line weight, same caps and joins, same level of detail, same perspective (flat stays flat).

## Define the graphic language in DESIGN.md

Add this block to `DESIGN.md` during `system`, `document`, or the first `build`. Extract values from the existing product when they exist; derive them from the OWN-WORLD when they do not.

```markdown
## Graphic Language (Micrographics)
- **Source world:** <one line from OWN-WORLD, e.g. "machinist drawings: hairlines, dimension arrows, section hatching">
- **Construction:** `--stroke-icon` <1.5px> on a <24px> grid with 2px live-area padding; <round | square> caps; <round | miter> joins; corner radius <2px>
- **Rendering:** <outline | solid | duotone>; outline switches to solid only to mark the active item
- **Color:** icons use `currentColor`; `--color-accent` only for state or a single annotation layer
- **Icon family:** <one library and version, or "custom, drawn on the 24px grid">
- **Sizes:** `--icon-sm` <16px>, `--icon-md` <20px>, `--icon-lg` <24px>
- **Motif inventory:** <5-9 named marks, e.g. registration cross, datum rule, dimension arrow, 3-density hatch, leader line with dot>
- **Never:** <motifs from other worlds, e.g. sparkles, blobs, circuit traces, emoji, 3D clay figures>
```

## Derive motifs from the OWN-WORLD

Motifs come from the subject's physical world, the same source as the palette. Generic marks that fit any product are filler.

| World | Motifs that belong | Motifs that do not |
|---|---|---|
| Precision hardware, engineering | Dimension arrows, section hatching, datum rules, registration crosses, tolerance callouts | Sparkles, blobs, soft 3D renders |
| Transit, logistics, maps | Route lines, station dots, interchange rings, platform numerals | Hand-drawn doodles, confetti |
| Finance, ledgers, accounting | Hairline rules, tick marks, dot leaders, column guides | Coins with sparkles, rockets, trophies |
| Editorial, publishing | Rules, folios, one fleuron used sparingly, pull-quote marks | Gradient badges, emoji |
| Health, clinical | Calm geometric pictograms, measurement scales, body-region outlines | Cartoon mascots, glossy 3D pills |
| Developer tools | The product's own syntax: brackets, carets, diff markers, a prompt glyph only if a CLI exists | Glowing circuit traces, fake terminals |
| Food, craft, retail | Marks from the real packaging: stamps, labels, grain, stitching | Generic leaf and heart doodles |

Five to nine motifs is enough for a whole product. More than that and the language stops being recognizable.

## Icon system

- **One family.** One library or one custom set per product. Never mix `lucide-react` with `react-icons`, or `react-icons/fa` with `react-icons/md` (`UNM-56`, foundations gate `icon-system`). Outline and solid variants of the same family count as one family.
- **One weight per size.** Every icon uses `--stroke-icon`; at most one optical variant (for example `1.5px` at 24px and `2px` at 16px) (`UNM-54`).
- **Three sizes at most,** tied to the type scale: the icon size equals the line height of the text beside it (`UNM-54`).
- **Color by inheritance.** `fill="none" stroke="currentColor"` (or `fill="currentColor"` for solid sets) so icons follow text tokens and dark mode. No hex inside an icon (`UNM-55`). Brand logos and flags are exempt.
- **Optical alignment.** Center icons on the cap height of adjacent text, not the line box: `display: inline-flex; align-items: center` on the row, or `vertical-align: -0.125em` inline.
- **Accessibility.** Decorative icons get `aria-hidden="true"`; icon-only buttons get an `aria-label` (`UNM-28`); destructive actions always carry a text label.
- **RTL.** Mirror directional icons (arrows, chevrons, progress) under `[dir="rtl"]`; never mirror checkmarks, clocks, or logos.
- **Custom icons.** Draw on the same grid with the same caps, joins, and weight; export with `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, no transforms, no embedded fonts, no raster.

## Micrographic tokens

```css
:root {
  --stroke-hairline: 1px;   /* rules, dividers, table lines, leader lines */
  --stroke-icon: 1.5px;     /* icons at 20-24px */
  --stroke-emphasis: 2px;   /* active state, single annotation layer */
  --icon-sm: 1rem;
  --icon-md: 1.25rem;
  --icon-lg: 1.5rem;
  --marker-size: 0.5rem;    /* status dots, list markers, map pin cores */
}
```

Add `vector-effect: non-scaling-stroke` to diagram paths so line weights stay constant when an SVG scales with its container.

## Small data graphics and status glyphs

- **Same pen.** Sparklines, meters, progress rings, and tick marks use the stroke tokens. No gradient fills, no glow, no 3D.
- **Labeled.** A sparkline shows its current value as text; a meter shows its number. Graphics support numbers, they do not replace them.
- **Status by shape plus color plus text.** For example: filled circle means done, ring means pending, triangle means warning, each with a word. Color alone fails color-blind users and `forced-colors` mode.
- **Real state only.** A pulsing dot means data is actually streaming (`UNM-08`); otherwise it is static.
- **Numbers** use `font-variant-numeric: tabular-nums` so values do not jitter as they update.

## Rules, dividers, markers, and annotations

- **One rule style.** `--stroke-hairline` in `--color-border`. No gradient-fade dividers, no wavy or zigzag section separators unless the inventory names them.
- **List markers** come from the inventory and are styled through `::marker` or a token-colored inline SVG. No emoji bullets or checkmark-emoji feature lists (`UNM-32`).
- **Callouts and leader lines** use the hairline or icon stroke with labels at `--text-sm`; one annotation color (`--color-accent`) per view.
- **Ornaments** are named motifs used at most once per view. Repetition turns an ornament into wallpaper.

## Spot illustrations and empty states

- **Built from the inventory.** Spot art is composed from the same motifs and stroke tokens as the icons, in `currentColor` plus at most the accent.
- **No stock illustration packs** (unDraw, Storyset, Humaaans, DrawKit, Open Peeps, ManyPixels, Blush) (`UNM-57`). Their figure style and default palettes (unDraw's `#6c63ff`) are recognized instantly as templates.
- **No 3D clay, glossy, or isometric renders** inside a flat UI.
- **Empty states:** one small motif, one sentence explaining why nothing is here, one action. The illustration is optional; the action is not.

## Generated imagery

When an image model produces assets (hero art, spot illustrations, social cards, README images):

- **Write one prompt base in `DESIGN.md`** naming the medium, exact palette values, line weight, motif inventory, composition grid, lighting, and explicit exclusions. Reuse it verbatim for every asset so the set stays one family.
- **Keep lettering out of the art** whenever the words matter. Image models misspell; real copy belongs in live HTML or SVG. When lettering is part of the art, keep it to a few short words, specify the exact strings, and proofread every glyph at 100% before approving.
- **Never present generated images as evidence.** They are not screenshots, metrics, customer photos, or testimonials. Label illustrations as illustrations.
- **Inspect at 100%** for garbled glyphs, stray lines, inconsistent perspective, and motifs outside the inventory.
- **Keep provenance** next to the asset (model, prompt, date, approval) so it can be regenerated in the same style.
- **Meet delivery constraints:** OpenGraph `1200x630`; GitHub social preview `1280x640` and under `1 MB`; favicons legible at `16px`.

## Social cards, favicons, and brand assets

- The OpenGraph image, favicon, app icon, email header, and documentation diagrams use the same graphic language as the product UI. A social card in a different style from the site breaks recognition at the first touchpoint.
- The favicon is the simplest form of the mark: one or two shapes that survive `16px`, as SVG with a `prefers-color-scheme` variant when the mark disappears on dark tabs.

## The belongs test

Run it on every screen during `graphics`, `critique`, and `polish`. For each graphic:

1. Which inventory motif is it? None means remove it, or add it to `DESIGN.md` deliberately.
2. Are its stroke, size, corner, and color all tokens?
3. Cover the logo. Does the graphic still say this brand? If it would fit any SaaS template, it is filler.
4. Does it carry information? Pure decoration must be a named motif and appear at most once per view.

## Anti-patterns

| Tell | Why it breaks coherence | Rule |
|---|---|---|
| Emoji as icons or bullets | A second, uncontrolled icon set with its own colors | `UNM-32` |
| Two or more icon libraries in one product | Different grids, weights, and metaphors side by side | `UNM-56`, gate `icon-system` |
| Stroke-weight or size drift across icons | Looks assembled from screenshots | `UNM-54` |
| Hex colors inside icon SVGs | Icons ignore the theme and break in dark mode | `UNM-55` |
| Stock illustration packs | The most recognized template look on the web | `UNM-57` |
| Gradient or glowing icons and icon tiles | Light effects the depth model forbids | `UNM-41`, `UNM-43` |
| Sparkle icon meaning "AI" | Universal shorthand that names nothing | review |
| Motifs from another world (circuit traces on a bakery, confetti on a bank) | Contradicts the OWN-WORLD | review |
| Generated art with garbled lettering | Instantly reads as unreviewed AI output | review |
| A different divider style in every section | No rule system | review |
| Icon-in-a-rounded-square tile on every feature | Container replacing meaning | review |
