# AI-Slop Anti-Patterns Catalog

The visual, structural, copy, motion, and craft tells that mark an interface as unreviewed model output. Each entry names the tell, why it reads as a default rather than a decision, what to do instead, and the `scripts/detect_slop.py` rule that enforces it (`review` means no reliable static signal: catch it in `critique` or the 60-second review).

## Contents
- How to use this catalog
- 1. Light, depth, and color
- 2. Layout and composition
- 3. Typography
- 4. Components and chrome
- 5. Copy and claims
- 6. Motion
- 7. Sloppy craft
- 8. The 60-second slop review
- Legitimate exceptions and waivers

## How to use this catalog

- Read it before `build`, `deslop`, `critique`, `quieter`, `distill`, and `polish`.
- One tell is rarely fatal. Three or more on a single screen read as unreviewed AI output, so the count is the signal.
- Fix at the token or component layer, not per instance: delete the `--shadow-glow` token instead of editing 14 `box-shadow` lines.
- The brief wins. When `DESIGN.md` or the user pins a pattern (a violet brand, a neobrutalist offset shadow), keep it and record a waiver with the reason.
- Never replace a removed fake with a new fake. Deleting an invented "10K+ users" stat is the fix; inventing "8,400 users" is not.

## 1. Light, depth, and color

**Default depth model.** Surfaces are flat and honest. Depth comes from `1px` borders and two or three surface tint steps (`--color-bg`, `--color-surface`, `--color-surface-raised`). One neutral shadow token exists for layers that genuinely float above content: menus, popovers, dialogs, toasts, and drag previews.

```css
:root {
  --shadow-overlay: 0 1px 2px oklch(0 0 0 / 0.06), 0 8px 24px oklch(0 0 0 / 0.08);
}
```

Resting cards, buttons, inputs, sections, and images get no shadow. No shadow is ever colored, because shadows are blocked light and light is not purple.

| Tell | Why it reads as default | Do instead | Rule |
|---|---|---|---|
| Stock purple accent: Tailwind `indigo`/`violet`/`purple` 400-700 (`#6366f1`, `#8b5cf6`, `#7c3aed`) | Framework default and the most common accent in generated SaaS UI; it signals that nobody chose a color | Derive the accent from the product's real materials in `DESIGN.md` | `UNM-42` |
| Purple-to-blue, cyan, or pink gradient | The house style of AI product launches, recognizable at a glance | One committed solid field; color-block if the page needs energy | `UNM-07` |
| Decorative gradients on backgrounds, buttons, borders, and icon tiles | A gradient postpones the choice between two colors | One solid semantic token; tonal steps via surface tokens | `UNM-41` |
| Gradient text on headlines | Emphasis by effect instead of by writing | Weight, scale, or one solid accent word | `UNM-03` |
| Neon glow halo (`box-shadow: 0 0 24px <color>`) | Borrowed from gaming and crypto templates to fake "energy" | Solid fill plus `1px` border; focus shown with `outline` | `UNM-06` |
| Colored drop shadow under buttons or cards (`shadow-indigo-500/50`) | Physically wrong and instantly templated | Neutral `--shadow-overlay`, floating layers only | `UNM-43` |
| Text glow (`text-shadow: 0 0 12px`) | Blurs letterforms and lowers effective contrast | More weight or more contrast | `UNM-43` |
| Heavy or stacked shadows on resting cards (blur `>= 48px`, `3+` layers, `shadow-2xl`) | When every card floats, nothing does; halos turn to mud on dark grounds | `1px` border and surface tint | `UNM-44` |
| Glassmorphism (`backdrop-filter: blur` over translucent white) | Contrast depends on whatever scrolls behind it, and it costs GPU time | Opaque surface token plus `1px` border | `UNM-45` |
| Blurred orbs and aurora blobs behind the hero | Atmosphere without content, identical across templates | Real imagery, a committed color field, or nothing | `UNM-46` |
| Slate `#0f172a` ground with a neon accent as the "dark mode" | Tailwind slate-900 plus glow is the developer-tool uniform | Dark neutrals tinted from the brand hue (OKLCH chroma `0.01-0.02`) | review |
| Cream ground, terracotta accent, italic display serif | The other half of the model's taste prior ("warm", "editorial", "craft") | Palette derived from the subject's physical scene | review |
| Low-contrast gray copy (`#9ca3af` on white is `2.5:1`; `#64748b` on `#0f172a` is under `4:1`) | Looks calm in a mockup, fails WCAG and sunlight | Body and placeholder text `>= 4.5:1`; tint muted text from the ground's hue | review (audit) |
| Pure `#000` ground with pure `#fff` text | Halation and eye strain on long reads | Off-black and off-white tinted toward the brand hue | review |
| Grain or noise overlay on every surface | Texture used as filler | Texture only when it is the material (paper, film, stone) | review |

## 2. Layout and composition

| Tell | Why it reads as default | Do instead | Rule |
|---|---|---|---|
| `50/50` split hero: copy left, mockup right, two buttons, stat strip below | The single most generated hero layout | Visitor-Mode opening from `SKILL.md` (monumental type, full-bleed stage, or straight into the workspace) | review |
| Three-column grid of icon-in-a-rounded-square feature cards | Template rhythm; the icons carry no information | Proof instruments: a live demo, a spec `<dl>`, a comparison `<table>`, an annotated screenshot | review |
| Bento grid as the default features layout | Trend copy; unequal tiles with no reason for their sizes | Use only when content has genuinely unequal weight | review |
| Fake product UI in a floating, tilted card or browser frame with traffic-light dots | Simulated proof | Real screenshots or a working interactive stage | review |
| Every section is a centered `<h2>`, gray subtitle, and grid | Monotone pacing from top to footer | Alternate full-bleed stages, `7/5` editorial splits, tables, and quiet reading passages | review |
| Everything center-aligned | Centered paragraphs are slow to scan | Left-aligned text on a `45ch-68ch` measure | review |
| Cards nested inside cards | Containers used instead of spacing | Proximity spacing, `1px` dividers, or surface tint | `UNM-04` |
| Infinite logo marquee ("Trusted by" strip) | Motion used to pad thin proof | A short static row of real, permitted logos, or nothing | `UNM-47` |
| Three pricing tiers with a glowing "Most popular" middle card | Template upsell staging | An honest comparison `<table>` with the recommended plan marked in text | `UNM-43`, `UNM-44` |
| Marketing hero on top of a dashboard, admin, or docs page | Wrong Visitor Mode | `Operate` and `Read` screens open directly into the work | review |
| Footer with five columns of links that go nowhere | Filler architecture | Only real routes | `UNM-53` |

## 3. Typography

| Tell | Why it reads as default | Do instead | Rule |
|---|---|---|---|
| Pill eyebrow above the `<h1>` ("NEW · AI-POWERED") | The most common generated hero ornament | Start the section with the heading | `UNM-01` |
| Tracked-out ALL CAPS micro labels | Fakes sophistication while hurting legibility | Sentence case, weight `500-600`, muted token color | `UNM-17` |
| Inter or `system-ui` as the display face by reflex | Zero point of view at the largest size on the page | A display face chosen for the subject; body face for legibility | review |
| More than two families, or a decorative third mono for numbers | Typographic noise | Two families max; `font-variant-numeric: tabular-nums` | `UNM-13` |
| Eight or more font sizes | No scale, just adjustments | Three body steps below the display size | `UNM-14` |
| Micro text below `12px` | Unreadable on real devices | `>= 13px` above the fold, `12px` absolute floor | `UNM-15` |
| Headline split with `<br><em>` italic flourish | Generated "editorial" cliche | One whole sentence with `text-wrap: balance` | `UNM-10` |
| Decorative `01 / 02 / 03` prefixes on non-sequential sections | Implies a procedure that does not exist | Plain headings | `UNM-02` |
| Title Case On Every Label, mixed with sentence case elsewhere | Inconsistent voice | Sentence case for UI, consistently | review |
| Oversized gray lead paragraph above smaller body text | Two body sizes competing | One body size; let the heading lead | review |

## 4. Components and chrome

| Tell | Why it reads as default | Do instead | Rule |
|---|---|---|---|
| Emoji or sparkle glyphs as icons or bullets (✨ for "AI", ⚡ for "fast", ✅ list items) | Placeholder iconography that shipped | One SVG icon family at one stroke weight | `UNM-32` |
| Two icon libraries in one product (lucide beside react-icons, Font Awesome beside Material) | Different grids, weights, and metaphors side by side | One family named in `DESIGN.md` | `UNM-56` |
| Stock illustration packs (unDraw, Storyset, Humaaans, DrawKit, Open Peeps) | The most recognized template look on the web | Spot art built from the `DESIGN.md` motif inventory | `UNM-57` |
| Generated hero or spot art with garbled lettering, or in a style unlike the rest of the product | Reads as unreviewed output and breaks the graphic language | One reusable prompt base in `DESIGN.md`; lettering in live HTML | review |
| Sparkle icon on anything AI-powered | The universal "magic" shorthand | Name the actual capability in words | review |
| Colored side-stripe on rounded callout cards (`border-left: 4px`) | Generated admonition style | Full `1px` border, tint, or a leading icon | `UNM-05` |
| Fake `LIVE` dots and `SCROLL DOWN` cues | Simulated activity | Real status only; let layout imply continuation | `UNM-08` |
| Terminal windows with traffic-light dots on a non-CLI product | Borrowed developer costume | Show the real product surface | review |
| Ghost "Learn more" button paired with every primary button | Two equal-weight actions dilute the one that matters | One primary action; a descriptive text link if needed | `UNM-40` |
| Clickable `<div>` cards | Keyboard and screen readers cannot reach them | `<a href>` for navigation, `<button>` for actions | `UNM-22` |
| Avatar stack with "+2k" | Unverifiable crowd | Named customers with permission, or nothing | `UNM-50` |
| Modals and toasts for every confirmation | Interrupts instead of informing | Inline status near the control that caused it | review |

## 5. Copy and claims

| Tell | Why it reads as default | Do instead | Rule |
|---|---|---|---|
| Filler verbs: elevate, unleash, supercharge, seamless, cutting-edge, game-changer, effortless, world-class, state-of-the-art, empower, "to the next level" | Words that fit every product say nothing about this one | Concrete capability plus measurable outcome | `UNM-09` |
| "X, reimagined", "The future of X", "Built for the future of X" | Interchangeable launch slogans | The specific thing that is different, in plain words | `UNM-09` |
| Triplet slogans ("Fast. Secure. Scalable.") | Rhythm without information | One claim with a number and a unit | review |
| Invented numbers: "10K+ users", "4.9★", "99.9% uptime", "Trusted by 10,000+" | Fabrication; a legal and trust liability | Sourced figures with dates, or remove | `UNM-50` |
| Em-dashes throughout generated UI copy | A recognizable model writing habit | Colon, comma, or period | `UNM-11` |
| Lorem ipsum, "John Doe", "Acme Inc", `example@example.com` | Placeholder that shipped | Real or clearly labeled sample data | `UNM-12` |
| "Get started" and "Learn more" as every call to action | Says nothing about what happens next | Name the action: "Reserve from batch 07", "Read the token docs" | `UNM-40` |
| Feature names where outcomes belong ("AI-powered engine") | Describes the inside, not the result | What the user gets, with evidence | review |

## 6. Motion

| Tell | Why it reads as default | Do instead | Rule |
|---|---|---|---|
| Idle loops: floating cards, bobbing badges, pulsing glows, bouncing arrows | Motion nobody asked for competes with reading | Animate only in response to input or real state | `UNM-47` |
| Animated gradient backgrounds | Decoration that never stops costing battery | A still, committed field | `UNM-47`, `UNM-41` |
| Fade-up reveal on every section | Delays content for no information gain | One orchestrated entrance at most | review |
| `hover: scale(1.05)` with a growing shadow on every card | Template hover | Subtle color or border change on interactive elements only | review |
| `transition: all`, `ease-in`, or UI transitions over `400ms` | Sluggish and layout-thrashing | `140ms-240ms` ease-out on `transform` and `opacity` | `UNM-18`, `UNM-19` |
| No reduced-motion path | Motion sensitivity ignored | `@media (prefers-reduced-motion: reduce)` | `UNM-20` |

## 7. Sloppy craft

The "nobody reviewed this" tells. Each is small; together they are why generated UI feels off even when nobody can say why.

| Tell | Why it reads as default | Do instead | Rule |
|---|---|---|---|
| Radius drift: `6px`, `8px`, `12px`, `16px`, `20px`, `24px` on one screen | Each component was styled in isolation | Three radius tokens plus `none` and `full` | `UNM-48` |
| Off-grid spacing (`13px`, `17px`, `37px`, `p-[13px]`) | Eyeballed nudges instead of a scale | 4px-based spacing tokens | `UNM-49` |
| `z-index: 9999` | Escalation instead of a layering model | Named scale: `--z-header`, `--z-overlay`, `--z-toast` | `UNM-49` |
| Raw hex values scattered through components | No token layer, so themes drift | Semantic `--color-*` tokens | `UNM-30` |
| Icon stroke weights or sizes drifting across one screen | Assembled from several sources | `--stroke-icon` and three `--icon-*` sizes | `UNM-54` |
| Hex colors hardcoded inside icon SVGs | Icons ignore the theme and break in dark mode | `currentColor` | `UNM-55` |
| A different divider or ornament style in every section | No rule system | One hairline rule; ornaments only from the motif inventory | review |
| Missing states: hover, focus, disabled, loading, empty, error | Only the happy path was built | All five states from `production-hardening.md` | `UNM-26` + audit |
| Buttons of different heights in one row; baselines that do not line up across columns | No control-height token | One control height; align on a shared baseline | review |
| Double borders where cards meet | Borders on both neighbors | Border on one side, or gap plus a single divider | review |
| A single orphan word on the last line of a heading | Unbalanced wrap | `text-wrap: balance` | review |
| Placeholder used as the label | Disappears on focus, fails screen readers | Visible `<label>` | `UNM-29` |
| Layout shift as images and fonts load | Missing dimensions and metric-matched fallbacks | `width`/`height` on media; `size-adjust` fallbacks | `UNM-24`, `UNM-25` |
| Long names and translations break the layout | Flex and grid children default to `min-width: auto` | `min-width: 0`, truncation or wrapping rules | review |
| Links to `#` | Unfinished navigation | Real routes, or `<button>` for actions | `UNM-53` |
| Browser defaults left untouched: selection color, focus ring, scrollbar, caret | Nobody themed the edges | The craft floor in `agnostic-design-patterns.md` | review |

## 8. The 60-second slop review

Run this on the first viewport before calling any UI done. Add one point per yes:

1. Squint. Is there a gradient, glow, glass panel, or blurred blob?
2. Is the accent indigo, violet, or purple without a brand reason?
3. Is there a pill or eyebrow label above the `<h1>`?
4. Is the opening a `50/50` split with a stat strip under it?
5. Is any number, rating, logo, or testimonial on screen unsourced?
6. Do resting cards cast shadows?
7. Is there a graphic `DESIGN.md` cannot name: an emoji, a sparkle, a stock illustration, or an icon from a second set?
8. Does any copy use the filler list in section 5?
9. Is anything moving that the user did not touch?
10. Are there more than three corner radii or more than five font sizes on screen?

**0-1:** ship. **2-3:** run `/unmistakable deslop`. **4+:** go back to the Direction Contract with `/unmistakable shape`. Then run `python3 scripts/detect_slop.py <target>` for the mechanical pass.

## Legitimate exceptions and waivers

- **The brand pins it.** A violet brand primary or a gradient logo stays. Keep it in tokens and waive at file level: `/* unmistakable-disable-file UNM-42: brand primary is violet per DESIGN.md */`.
- **Data encodings.** Heatmap scales, map legends, and chart ramps are information, not decoration. Use `var()` stops (not flagged) or waive the line.
- **Photography scrims.** Neutral black-to-transparent gradients for text legibility over photos are not flagged.
- **Real floating layers.** Menus, popovers, dialogs, and toasts use `--shadow-overlay`.
- **Modal scrims.** `::backdrop`, `.overlay`, and `fixed inset-0` layers may blur what is behind them; they are not flagged.
- **Loading indicators.** Spinners, skeleton shimmer, and progress bars may loop; they are not flagged, and they still need a reduced-motion path.
- **Committed styles.** A genuine neobrutalist brief can use hard offset shadows; a genuine retro-futurist brief can glow. The brief must say so in writing.

Waiver syntax, always with a reason: `/* unmistakable-disable UNM-XX: reason */` covers the same and next line, `unmistakable-disable-file` covers the file, and `--report-unused-ignores` fails on stale waivers.
