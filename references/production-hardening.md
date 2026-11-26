# Production Hardening, Accessibility, and Core Web Vitals

Interfaces that only survive happy-path mock data fail in production. Apply these framework-agnostic resilience patterns across React, Next.js, Vue, Nuxt, SvelteKit, Astro, Angular, Solid, Web Components, and plain HTML/CSS.

## Contents
- Text overflow, flex/grid shrinkage, and mobile input sizing
- Internationalization, RTL logical properties, and Arabic script fidelity
- Interactive states, error recovery, and concurrency locks
- Pointer-gesture cancellation and touch resilience
- Accessibility resilience (WCAG 2.2 AA)
- Core Web Vitals and rendering performance

## Text overflow, flex/grid shrinkage, and mobile input sizing

1. **Prevent flex and grid blowout:** Flex and CSS Grid children default to `min-width: auto`, causing long URLs, user names, or translations to blow past container boundaries. Add `min-width: 0` (and `min-height: 0` on scrollable grid tracks) to every text-bearing flex or grid child:
   ```css
   .row-item, .grid-cell {
     min-width: 0;
   }
   .truncate-1 {
     overflow: hidden;
     text-overflow: ellipsis;
     white-space: nowrap;
   }
   .clamp-3 {
     display: -webkit-box;
     -webkit-line-clamp: 3;
     -webkit-box-orient: vertical;
     overflow: hidden;
   }
   .prose-wrap {
     overflow-wrap: break-word;
     hyphens: auto;
   }
   ```
2. **Enforce a `16px` (`1rem`) minimum font size on form controls:** iOS Safari auto-zooms the viewport whenever a focused `<input>`, `<select>`, or `<textarea>` computes under `16px`, breaking sticky headers and modal layouts. Keep form control font-size `>= 1rem` at mobile breakpoints.
3. **200% zoom & dynamic type:** Never set fixed `height` on containers holding wrapping text; use `min-height` plus vertical padding so `200%` browser text zoom expands cleanly without clipping.

## Internationalization, RTL logical properties, and Arabic script fidelity

1. **Translation expansion budget:** German, Finnish, and Spanish strings routinely expand `30%-40%` past English labels. Size buttons and tabs with `padding-inline` and `min-width` rather than fixed widths (`width: 96px`).
2. **Logical CSS properties:** Author directional spacing, borders, and alignment with logical properties so `dir="rtl"` mirrors automatically without duplicate stylesheet overrides:
   - `margin-inline-start` / `margin-inline-end` instead of `margin-left` / `margin-right`
   - `padding-inline` / `padding-block` instead of physical shorthand asymmetries
   - `inset-inline-start` / `inset-inline-end` instead of `left` / `right` (exception: keep physical `left: 50%; transform: translateX(-50%)` for horizontal centering because `translateX` is physical)
   - `text-align: start` / `end` instead of `left` / `right`
   - Mirror directional progress/navigation icons (`chevrons`, `arrows`) under `[dir="rtl"] .icon-directional { transform: scaleX(-1); }`, leaving asymmetrical marks (checkmarks, clocks, logos) unflipped.
3. **Arabic, Persian, Urdu, and Kurdish script specifics:**
   - Declare explicit `dir="rtl"` on `<html>` or the localized container (`lang` alone does not set browser layout direction).
   - **Preserve Zero-Width Non-Joiner (`U+200C`):** Persian and Kurdish rely on ZWNJ between compound stems; input sanitizers that strip invisible characters corrupt word meaning.
   - **Normalize Yeh and Kaf only in search/matching:** Preserve original Persian (`\u06cc`, `\u06a9`) and Arabic (`\u064a`, `\u0643`) code points in storage, while treating both keyboard forms as equivalent during client/server search and validation.
   - **Format dates, numbers, and currencies via `Intl`:** Use `Intl.NumberFormat(locale, ...)` and `Intl.DateTimeFormat(locale, ...)` rather than string-concatenated `$` prefixes or English `count === 1 ? '' : 's'` plural checks (`Intl.PluralRules`).

## Interactive states, error recovery, and concurrency locks

Every data-driven region and interactive control requires five explicit states:
1. **Default & Hover/Focus:** Immediate visual affordance; keyboard `:focus-visible` matches or exceeds hover clarity.
2. **Loading:** Skeletons or inline progress matching final geometry so layout does not jump when data resolves. Label active loads (`aria-busy="true"` or polite status text).
3. **Empty:** Explain cleanly why nothing is shown and provide one direct action to create the first item or clear active filters.
4. **Error with recovery:** Map status classes to human recovery actions (`400` inline field message preserving typed input; `401` session re-auth preserving draft state; `403` permission explanation; `404` route recovery link; `429` retry backoff notice; `500`/offline retry button). Isolate component errors so one failed widget does not blank the entire page.
5. **Pending / Concurrency lock:** Disable or guard submit triggers (`aria-disabled="true"` / AbortController / idempotency lock) while a mutation is in flight so rapid double-clicks cannot fire duplicate writes, and roll back optimistic UI cleanly on failure.

## Pointer-gesture cancellation and touch resilience

Custom sliders, kanban cards, split panes, carousels, and Scrubbers break on touch devices when built with mouse-only events (`mousedown`/`mousemove`):
- Use **Pointer Events** (`pointerdown`, `pointermove`, `pointerup`) paired with `setPointerCapture(e.pointerId)` and explicit `touch-action` (`pan-y` for horizontal drags, `none` for 2D canvas surfaces).
- Track the active `pointerId` so a second finger landing mid-gesture does not teleport the drag target.
- Clear dragging state and release capture on **all four interruption paths**: `pointerup`, `pointercancel` (browser scroll takeover), `lostpointercapture`, and `window` `blur`, ensuring the very next tap or drag works without reloading the page.

## Accessibility resilience (WCAG 2.2 AA)

- **Native semantics first:** Use `<button type="button">` for actions and `<a href="...">` for navigation. Never attach click handlers to bare `<div>` or `<span>` elements.
- **Heading and landmark order:** Maintain one `<h1>` per route and sequential heading levels (`h1 -> h2 -> h3`) without skipping levels for visual size. Wrap content in `<header>`, `<nav>`, `<main>`, and `<footer>`, plus a first-focus `"Skip to main content"` link on multi-block pages.
- **Target sizes (WCAG 2.2 SC 2.5.8):** Aim for `>= 44x44px` on primary touch controls and never drop below `24x24px` CSS pixels (or provide `>= 24px` center-to-center spacing from adjacent targets).
- **Form labeling & live announcements:** Pair every input with an explicit `<label for="...">` (placeholder text is not a label), link inline hints/errors via `aria-describedby` + `aria-invalid="true"`, and announce asynchronous status updates with `aria-live="polite"`.
- **Non-color state cues:** Pair status colors with an icon, label, border weight, or pattern so color-blind and Windows High Contrast (`forced-colors: active`) users retain full meaning.

## Core Web Vitals and rendering performance

Measure bottlenecks before micro-optimizing, and enforce three production floors on every build:

### 1. Largest Contentful Paint (`LCP < 2.5s`)
- Render above-the-fold hero copy and primary imagery in initial HTML/SSR without blocking on client-only hydration waterfalls.
- Put `fetchpriority="high"` and `loading="eager"` (omit `loading="lazy"`) on the single LCP hero image, with responsive `srcset`/`sizes` in AVIF or WebP.
- Preconnect font origins (`<link rel="preconnect" ... crossorigin>`) and load only used weights (`font-display: swap` or `optional`) with metric-matched fallback `@font-face` (`size-adjust`).

### 2. Cumulative Layout Shift (`CLS < 0.1`)
- Set explicit `width` and `height` attributes (or CSS `aspect-ratio`) on every `<img>`, `<video>`, `<iframe>`, and async embed slot.
- Never inject banners, cookie bars, or dynamic callouts above already-rendered content; reserve fixed slot geometry or overlay cleanly.
- Animate `transform`, `opacity`, and `clip-path` rather than layout-inducing `height`, `top`, `margin`, or `width`.

### 3. Interaction to Next Paint (`INP < 200ms`)
- Avoid synchronous DOM read-then-write thrashing inside loops; batch measurements before mutations.
- Apply `content-visibility: auto; contain-intrinsic-size: auto 400px;` to long below-the-fold feeds or virtualize lists exceeding `~150` complex rows.
- Apply `will-change` only immediately before a known heavy transition, never across dozens of resting elements.
- Clean up event listeners, `IntersectionObserver`s, timers, and `AbortController` requests on component unmount.
