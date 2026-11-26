# Unmistakable Evaluation Prompts & Baselines

Authored following `robonuggets/skill-creator-plus` (`references/testing.md`) to verify both trigger precision and behavioral lift over a no-skill baseline.

## Contents
- Prompt 1: Brand landing page without AI slop (Persuade)
- Prompt 2: Operational SaaS dashboard without hero banner (Operate)
- Prompt 3: Extract living design system and 1-page A4 brand book
- Prompt 4: Production hardening + Technical SEO & AI GEO audit
- Prompt 5: Negative control (should not trigger)
- Prompt 6: De-slop a generic SaaS page ("modern and premium")
- Prompt 7: AI answer-engine visibility without training access

### Prompt 1: Brand landing page without AI slop (`Persuade`)
Prompt: `Build a marketing landing page in Astro for a precision Swiss espresso grinder called Helvetia Mill. Make it production-ready and search-friendly.`
Should trigger: yes
First file agent should open: `references/agnostic-design-patterns.md` (plus `references/seo-and-geo-patterns.md`)
No-skill baseline misses: Defaults to warm cream/beige + Playfair Display italic serif + terracotta buttons, `50/50` left-text/right-box split hero, uppercase `.eyebrow` badges, 3-column icon cards, missing JSON-LD / `llms.txt`, and `loading="lazy"` on the hero image.
Done looks like: Non-split full-viewport opening bleeding to `y = 0`, palette derived from brushed steel/obsidian/espresso crema (`--color-*` tokens), max 2 font families and 3 body sizes (`tabular-nums`), zero eyebrows/badges, `Product` JSON-LD + `llms.txt`, and `0` findings from `scripts/detect_slop.py`.

### Prompt 2: Operational SaaS dashboard without hero banner (`Operate`)
Prompt: `Redesign our Next.js incident triage console so engineers can filter 2,000 live alerts, handle RTL locales, and navigate by keyboard.`
Should trigger: yes
First file agent should open: `references/agnostic-design-patterns.md` and `references/production-hardening.md`
No-skill baseline misses: Adds a decorative marketing banner above the table, uses `<div onClick>` rows, breaks flex cells on long stack traces, uses `< 16px` filter inputs, and omits `prefers-reduced-motion` and RTL logical properties.
Done looks like: Opens at `y = 0` directly into live triage controls (`Operate` mode), semantic `<button>`/`<table>`, `min-width: 0`, `>= 16px` filter inputs, logical CSS (`inline`/`block`), all 5 states (loading/empty/error/pending/focus), and `0` P0/P1 findings in `scripts/detect_slop.py`.

### Prompt 3: Extract living design system and 1-page A4 brand book
Prompt: `Extract the brand from our existing styles and logo in public/logo.svg, then generate a design system reference page and a 1-page A4 brand book PDF.`
Should trigger: yes
First file agent should open: `references/brand-and-design-system.md` (plus `assets/design-system-template.html` and `assets/brand-book-a4-template.html`)
No-skill baseline misses: Invents arbitrary brand principles, redraws the SVG logo inaccurately, forgets `@page { size: A4; margin: 0; }`, and hands over raw HTML that overflows onto 2-3 PDF pages.
Done looks like: Preserves `public/logo.svg` verbatim, drops unsourced sections, writes `DESIGN.md`, `design/tokens.css`, `design/design-system.html`, and renders a verified 1-page `design/brand-book-a4.pdf` via `scripts/render_brand_book.py`.

### Prompt 4: Production hardening + Technical SEO & AI GEO audit
Prompt: `Audit our marketing site for AI slop, accessibility, Core Web Vitals, and AI search visibility (ChatGPT / Perplexity / Google), then give me prioritized fixes.`
Should trigger: yes
First file agent should open: `references/commands-and-audit-rubric.md` and run `scripts/detect_slop.py` + `scripts/check_foundations.py`
No-skill baseline misses: Gives vague subjective prose without `file:line` citations, misses CLS/LCP attributes, and ignores `Schema.org` JSON-LD and `llms.txt`.
Done looks like: Runs `scripts/detect_slop.py --json` and `scripts/check_foundations.py --json`, delivers the 6-dimension `0-24` Audit Health Score ranked `P0-P3` with `file:line` evidence, and modifies zero files during `audit`.

### Prompt 5: Negative control (should not trigger)
Prompt: `Write a Python CLI script that parses PostgreSQL WAL binary logs and exports row counts to Parquet.`
Should trigger: no
Done looks like: Skill stays inactive because no web UI, frontend component, design system, or web SEO/GEO surface is involved.

### Prompt 6: De-slop a generic SaaS page ("modern and premium")
Prompt: `Our SaaS landing page looks generic. Make it look more modern and premium.`
Should trigger: yes
First file agent should open: `references/anti-patterns.md` (plus `references/agnostic-design-patterns.md`)
No-skill baseline misses: Reads "modern and premium" as permission for more effects: an indigo-to-violet gradient button with a colored glow, glass cards with `backdrop-blur`, blurred purple orbs behind the hero, `shadow-2xl` on every card, a floating animation on the mockup, and a new "Trusted by 10,000+ teams" line.
Done looks like: The 60-second slop review drops to `0-1`; the accent is derived from `DESIGN.md` (or two proposed options), depth uses `1px` borders and surface tints with one neutral `--shadow-overlay`, invented proof is removed rather than replaced, and `scripts/detect_slop.py` reports no `UNM-41` to `UNM-50` findings without a written waiver.

### Prompt 7: AI answer-engine visibility without training access
Prompt: `We want to show up in ChatGPT and Perplexity answers but we don't want our docs used for model training. Set up our Next.js site for that.`
Should trigger: yes
First file agent should open: `references/seo-and-geo-patterns.md`
No-skill baseline misses: Blocks every AI user agent in robots.txt (which also removes the site from AI answers), ignores the CDN's bot rules, leaves docs rendered client-side, and promises that `llms.txt` will improve rankings.
Done looks like: `app/robots.ts` allows search and user-triggered agents while disallowing training crawlers, a note to verify the CDN/WAF in logs, server-rendered answer-first docs with valid `@graph` JSON-LD, an honest `llms.txt`, and a passing `ai-search-crawlers` gate in `scripts/check_foundations.py`.
