# Design System: Unmistakable (repository assets)

Scope: the README images, GitHub social preview, showcase sheet, documentation diagrams, and any generated or rendered asset for this repository. Interfaces built *with* the skill follow each project's own `DESIGN.md`, not this one.

Source: extracted from the three approved assets in `assets/` (`before-after.png`, `social-preview.png`, `unmistakable-showcase.png`) and their generation prompts in the matching `.json` files. Ink and red values are sampled from the scans.

## Visual Thesis & Anti-References

- **Physical scene:** a specification sheet drafted by hand at a drawing table and scanned flat under even, shadowless light.
- **Thesis:** the repository looks like the discipline it teaches: measured, annotated, corrected in red, nothing decorative.
- **Color strategy:** Restrained: paper, one ink, one red correction pen.
- **Anti-references:** everything the skill bans, plus 3D device mockups, desks, pens or rulers in frame, photographs, color fills, gradients, glows, and dark "developer" UI.

## Color Tokens

| Token | Value | Role |
|---|---|---|
| `--paper` | `#FAF8F4` | Sheet ground (warm off-white millimeter graph paper) |
| `--grid` | `--ink` at about 12% opacity | Whisper-faint square coordinate grid |
| `--ink` | `#151423` (sampled) | All linework, hatching, and lettering (dark navy-black ballpoint) |
| `--redline` | `#AB343B` (sampled) | Corrections only: strike-throughs, revision slashes, callout ticks, the single accent rule, "0 FINDINGS" |

Red never fills an area and never appears on more than one idea per sheet.

## Typography

- **Lettering:** hand-drafted architectural block capitals. Short labels only (one to three words), exact strings specified in the prompt, proofread glyph by glyph.
- **Live text:** anything a reader must rely on (counts, commands, rule IDs) lives in the README as text, not inside an image.

## Graphic Language (Micrographics)

- **Source world:** architectural and engineering drafting sheets.
- **Construction:** one `0.38mm` ballpoint line weight throughout; flat orthographic 2D, no perspective; generous negative space on a 12-column Swiss modular grid.
- **Motif inventory:**
  1. Four corner crop registration crosses (`+`)
  2. Whisper-faint square coordinate grid with margin tick marks
  3. Datum rule: one ruled line that anchors a heading or divides the sheet
  4. Dimension arrows with extension lines
  5. 45-degree parallel hatching at three densities (dense, medium, light) standing in for color tokens
  6. Wireframe panels: browser and mobile frames with ruled hierarchy bars
  7. Technical cross-section with circular detail hatching
  8. Red corrections: diagonal revision slash, single horizontal strike-through, small callout tick
  9. Node-tree and spec-table diagrams in the same line weight
- **Never:** sparkles, blobs, gradients, shadows, color fills, emoji, 3D objects, mockup devices, pens or rulers on the page, filler or gibberish text.

## Image Prompt Base

Reuse verbatim, replacing only the bracketed parts:

> A 90-degree overhead archival flatbed scan of a minimalist hand-drawn architectural [SUBJECT] on warm off-white millimeter graph paper (#FAF8F4), illustrated with a fine 0.38mm dark navy-black ballpoint pen [and a fine red ballpoint drafting pen used only for corrections]. A whisper-faint square coordinate grid and four corner crop registration crosses (+) frame the [ASPECT] sheet. [COMPOSITION, using only motifs from the inventory above]. [EXACT LETTERING: list every string, or "no text"]. Uniform shadowless flatbed illumination, generous negative space, strictly flat 2D scan with no 3D mockup, no pens or rulers on the page, no gradients, and no other text.

Every generated asset keeps its prompt, model, date, and approval in a sidecar `.json` next to the image.

## Delivery Constraints

| Asset | Size | Limit |
|---|---|---|
| README images | 16:9, 2K | Keep under about 2 MB |
| GitHub social preview | 1280x640 (2:1) | Under 1 MB; GitHub rejects larger uploads |
| OpenGraph image (if a docs site exists) | 1200x630 | Absolute `https://` URL |
