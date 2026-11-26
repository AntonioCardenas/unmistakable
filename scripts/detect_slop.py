#!/usr/bin/env python3
"""Deterministic anti-slop, sloppy-UI, accessibility, Core Web Vitals, and SEO/GEO scanner.

Scans HTML, JSX, TSX, Vue, Svelte, Astro, Angular templates, and CSS/SCSS files
for 53 common AI-slop, craft, accessibility, performance, and search-readiness
defects. Uses Python 3.8+ standard library only - zero external dependencies or API keys.

Exit codes:
  0 = clean scan (no findings at or above --fail-on, and zero unused waivers when requested)
  1 = target path missing or unreadable
  2 = one or more active findings at or above --fail-on severity
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

VERSION = "1.1.0"

# ---------------------------------------------------------------------------
# Named constants with explicit engineering rationale (no voodoo numbers).
# ---------------------------------------------------------------------------

# Files over 1.5 MB are bundled builds or data snapshots, not hand-authored UI.
MAX_SCAN_BYTES = 1_500_000

# 2-family typographic cap from agnostic-design-patterns.md (display + body).
MAX_FONT_FAMILIES = 2

# 3 body steps + 1 display + 1 optional table/caption step = 5 distinct sizes max.
MAX_FONT_SIZES_PER_FILE = 5

# Absolute legibility floor in CSS pixels; below 12px fails scanability.
MIN_READABLE_PX = 12.0

# iOS Safari force-zooms the page when a focused input computes below 16px.
IOS_INPUT_MIN_PX = 16.0

# More than 6 raw hex literals outside :root/@theme signals token drift.
MAX_RAW_HEX_OUTSIDE_TOKENS = 6

# Standard CSS base font size for rem-to-px checks.
REM_BASE_PX = 16.0

# Above-the-fold line window used to flag lazy-loaded hero images.
HERO_FOLD_MAX_LINE = 90

# RGB channel spread (0-255) above which a color reads as a hue rather than a tinted neutral.
CHROMA_MIN_RGB_SPREAD = 40

# OKLCH chroma above which a color reads as saturated; tinted neutrals sit at 0.005-0.03.
CHROMA_MIN_OKLCH = 0.06

# CIE LCH/Lab chroma equivalent of the OKLCH saturation threshold.
CHROMA_MIN_LAB = 15.0

# HSL saturation (percent) above which a color reads as chromatic.
HSL_MIN_SAT = 25.0

# HSL lightness window (percent); outside it a color reads as near-black or near-white.
HSL_LIGHTNESS_WINDOW = (8.0, 94.0)

# Alpha below which a color stop or shadow is effectively invisible.
MIN_VISIBLE_ALPHA = 0.08

# Mean RGB channel (0-255) above which a neutral reads as light (a white "glow").
LIGHT_NEUTRAL_MIN_RGB = 200

# Zero-offset box-shadows at or above this blur read as neon glow halos (UNM-06).
GLOW_MIN_BLUR_PX = 16.0

# Zero-offset text-shadow at or above this blur reads as neon text glow (UNM-43).
TEXT_GLOW_MIN_BLUR_PX = 6.0

# Shadow blur at or above this radius reads as heavy floating "elevation soup" (UNM-44).
HEAVY_SHADOW_MIN_BLUR_PX = 48.0

# Shadow spread at or above this radius stops reading as a ring and becomes a halo (UNM-44).
HEAVY_SHADOW_MIN_SPREAD_PX = 16.0

# Two blurred layers (contact + ambient) model real elevation; a third is decoration (UNM-44).
MAX_SHADOW_LAYERS = 2

# filter: blur() at or above this radius on an element is a decorative orb, not a UI effect (UNM-46).
ORB_MIN_BLUR_PX = 40.0

# Tailwind blur scale in px for orb detection (blur-2xl = 40px, blur-3xl = 64px).
TW_BLUR_PX = {"2xl": 40.0, "3xl": 64.0}

# Disciplined systems use at most 3 radius steps (control, container, sheet) plus none/full (UNM-48).
MAX_RADIUS_STEPS = 3

# Three or more off-grid spacing literals in one file signals eyeballed spacing (UNM-49).
MAX_OFF_GRID_SPACING = 2

# Spacing values at or below 2px are hairline/optical nudges, not layout rhythm (UNM-49).
SPACING_NUDGE_MAX_PX = 2.0

# z-index at or above this value is escalation ("z-index: 9999"), not a layering scale (UNM-49).
Z_INDEX_ESCALATION = 999

# sRGB/HSL hue windows (degrees) for the purple-to-blue/cyan/pink gradient cliche (UNM-07).
PURPLE_HUE = (236.0, 320.0)
BLUE_CYAN_HUE = (170.0, 236.0)
PINK_HUE = (320.0, 350.0)

# OKLCH hue windows (degrees); OKLCH hues sit ~30 degrees off sRGB/HSL hues.
OKLCH_PURPLE_HUE = (270.0, 325.0)
OKLCH_BLUE_HUE = (185.0, 270.0)
OKLCH_PINK_HUE = (325.0, 360.0)

# OKLCH window matching Tailwind v4 indigo/violet/purple 400-700 defaults (UNM-42).
STOCK_PURPLE_OKLCH_HUE = (265.0, 310.0)
STOCK_PURPLE_OKLCH_MIN_CHROMA = 0.15

# Tailwind v3 indigo/violet/purple 400-700: the default "AI product" accent family (UNM-42).
STOCK_PURPLE_HEX = frozenset({
    "#818cf8", "#6366f1", "#4f46e5", "#4338ca",
    "#a78bfa", "#8b5cf6", "#7c3aed", "#6d28d9",
    "#c084fc", "#a855f7", "#9333ea", "#7e22ce",
})

EM_DASH_CHAR = chr(0x2014)

MARKUP_EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
STYLE_EXTS = {".css", ".scss"}
ALL_SCAN_EXTS = MARKUP_EXTS | STYLE_EXTS

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".astro",
    ".angular",
    ".unmistakable",
    "node_modules",
    "dist",
    "build",
    "out",
    "coverage",
    "vendor",
    "__pycache__",
    "evals",
    "assets",
}

RULES: List[Dict[str, str]] = [
    {"id": "UNM-01", "sev": "P1", "cat": "Slop", "desc": "Pre-heading .eyebrow or .kicker label perched above a heading", "fix": "Delete the pre-heading eyebrow and start the section directly with <h1> or <h2>."},
    {"id": "UNM-02", "sev": "P2", "cat": "Slop", "desc": "Decorative 01/02/03 or [01] prefix inside a heading", "fix": "Remove decorative numbering unless steps represent a genuine sequential procedure."},
    {"id": "UNM-03", "sev": "P2", "cat": "Slop", "desc": "Gradient text fill (background-clip: text with transparent color)", "fix": "Create emphasis with typographic scale, weight, and solid contrast rather than gradient text."},
    {"id": "UNM-04", "sev": "P1", "cat": "Slop", "desc": "Nested card container inside another card container", "fix": "Group inner content with proximity spacing, 1px dividers, or subtle surface tint instead of nested cards."},
    {"id": "UNM-05", "sev": "P2", "cat": "Slop", "desc": "One-sided thick accent border bar on a rounded container", "fix": "Use a full 1px semantic border, subtle surface tint, or leading icon instead of a 3px-6px side bar."},
    {"id": "UNM-06", "sev": "P2", "cat": "Slop", "desc": "Zero-offset neon glow halo (box-shadow: 0 0 <blur> <color>)", "fix": "Delete the halo; use a solid fill, weight, or crisp 1px border for emphasis and neutral offset shadows only on floating layers."},
    {"id": "UNM-07", "sev": "P2", "cat": "Slop", "desc": "Purple-to-blue/cyan/pink AI cliche gradient", "fix": "Derive palette colors from the brand's real domain materials and DESIGN.md tokens; use one solid field."},
    {"id": "UNM-08", "sev": "P2", "cat": "Slop", "desc": "Synthetic LIVE dot or SCROLL DOWN decorative cue", "fix": "Remove fake telemetry badges and let layout framing signal scroll continuation naturally."},
    {"id": "UNM-09", "sev": "P2", "cat": "Copy", "desc": "Generic AI marketing filler phrase in UI copy", "fix": "State concrete product capabilities and measurable user outcomes in plain language."},
    {"id": "UNM-10", "sev": "P2", "cat": "Copy", "desc": "Headline split mid-phrase with <br><em> italic cliche", "fix": "Keep the headline whole and let text-wrap: balance handle line breaks cleanly."},
    {"id": "UNM-11", "sev": "P3", "cat": "Copy", "desc": "Em-dash character (U+2014) in UI markup copy", "fix": "Rewrite with a colon, comma, period, or spaced hyphen for cleaner UI scanability."},
    {"id": "UNM-12", "sev": "P2", "cat": "Copy", "desc": "Placeholder lorem ipsum or example@example.com left in UI", "fix": "Author realistic domain-specific copy and clearly labeled sample data."},
    {"id": "UNM-13", "sev": "P2", "cat": "Type", "desc": "More than 2 distinct font-family stacks declared", "fix": "Cap typography at 2 families max and use font-variant-numeric: tabular-nums for numbers."},
    {"id": "UNM-14", "sev": "P2", "cat": "Type", "desc": "Excessive distinct font-size steps (> 5) in one stylesheet", "fix": "Consolidate body typography into --text-heading, --text-body, and --text-sm."},
    {"id": "UNM-15", "sev": "P1", "cat": "Type", "desc": "Micro font-size below 12px (0.75rem)", "fix": "Raise secondary metadata to >= 0.8125rem (13px) above the fold or >= 0.75rem (12px) minimum."},
    {"id": "UNM-16", "sev": "P1", "cat": "Forms", "desc": "Form control font-size below 16px (1rem)", "fix": "Set input, select, and textarea font-size >= 1rem (16px) so iOS Safari does not force-zoom on focus."},
    {"id": "UNM-17", "sev": "P2", "cat": "Type", "desc": "Tracked-out ALL CAPS micro-label styling", "fix": "Use sentence-case labels differentiated by weight (500-600) and muted token color."},
    {"id": "UNM-18", "sev": "P1", "cat": "Perf", "desc": "transition: all or transition-all animating layout properties", "fix": "Name explicit compositor properties such as transition: transform 180ms, opacity 180ms."},
    {"id": "UNM-19", "sev": "P2", "cat": "Motion", "desc": "ease-in timing function used on UI transition", "fix": "Use responsive ease-out curves such as cubic-bezier(0.22, 1, 0.36, 1) for interactive feedback."},
    {"id": "UNM-20", "sev": "P1", "cat": "A11y", "desc": "Animations or transitions missing @media (prefers-reduced-motion: reduce)", "fix": "Add a @media (prefers-reduced-motion: reduce) guard preserving state clarity without motion."},
    {"id": "UNM-21", "sev": "P2", "cat": "Perf", "desc": "Broad or universal will-change declaration", "fix": "Scope will-change to specific active elements and properties rather than resting rules."},
    {"id": "UNM-22", "sev": "P0", "cat": "A11y", "desc": "Click handler attached to non-interactive <div> or <span>", "fix": "Replace with a native <button type=\"button\"> or <a href=\"...\"> for keyboard and screen-reader access."},
    {"id": "UNM-23", "sev": "P0", "cat": "A11y", "desc": "<img> element missing alt attribute", "fix": "Add descriptive alt text, or alt=\"\" when the image is purely decorative."},
    {"id": "UNM-24", "sev": "P1", "cat": "CWV", "desc": "<img> missing explicit width and height (or aspect-ratio), risking CLS", "fix": "Set intrinsic width and height attributes on every <img> so browsers reserve layout space."},
    {"id": "UNM-25", "sev": "P1", "cat": "CWV", "desc": "Above-the-fold hero image marked loading=\"lazy\"", "fix": "Use fetchpriority=\"high\" and eager loading on the primary LCP image; lazy-load below the fold only."},
    {"id": "UNM-26", "sev": "P0", "cat": "A11y", "desc": "Focus outline removed without a visible :focus-visible replacement", "fix": "Provide :focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }."},
    {"id": "UNM-27", "sev": "P1", "cat": "A11y", "desc": "Skipped heading level (e.g. <h1> jumping directly to <h3>)", "fix": "Keep heading hierarchy sequential (h1 -> h2 -> h3) and control visual size with CSS tokens."},
    {"id": "UNM-28", "sev": "P1", "cat": "A11y", "desc": "Icon-only <button> missing accessible text or aria-label", "fix": "Add aria-label naming the action (e.g. aria-label=\"Close dialog\") on icon-only buttons."},
    {"id": "UNM-29", "sev": "P1", "cat": "A11y", "desc": "Form <input> missing associated <label>, aria-label, or aria-labelledby", "fix": "Wrap in <label> or connect <label for=\"id\">; placeholder text is not an accessible label."},
    {"id": "UNM-30", "sev": "P2", "cat": "Tokens", "desc": "Scattered hardcoded hex literals outside :root/@theme token definitions", "fix": "Move raw hex colors into semantic CSS custom properties (--color-*) and consume via var()."},
    {"id": "UNM-31", "sev": "P2", "cat": "RTL", "desc": "Physical left/right margin or padding on an RTL-enabled document", "fix": "Use logical CSS properties (margin-inline-start/end, padding-inline) for clean RTL mirroring."},
    {"id": "UNM-32", "sev": "P2", "cat": "Icons", "desc": "Raw emoji glyph used inside button or navigation UI chrome", "fix": "Replace emoji chrome with crisp inline SVGs in one consistent stroke weight."},
    {"id": "UNM-33", "sev": "P1", "cat": "SEO", "desc": "Full HTML document missing lang attribute on <html>", "fix": "Set <html lang=\"en\"> (or the active BCP-47 locale) for screen readers and search engines."},
    {"id": "UNM-34", "sev": "P1", "cat": "SEO", "desc": "Full HTML document missing <main> landmark", "fix": "Wrap primary route content in a single <main id=\"main-content\"> landmark."},
    {"id": "UNM-35", "sev": "P1", "cat": "SEO", "desc": "Full HTML document has zero or multiple <h1> elements", "fix": "Provide exactly one primary <h1> naming the page entity and user outcome."},
    {"id": "UNM-36", "sev": "P1", "cat": "SEO", "desc": "Full HTML <head> missing <title> or <meta name=\"description\">", "fix": "Include a unique <title> (35-60 chars) and factual <meta name=\"description\"> (120-160 chars)."},
    {"id": "UNM-37", "sev": "P2", "cat": "SEO", "desc": "Full HTML <head> missing <link rel=\"canonical\">", "fix": "Add <link rel=\"canonical\" href=\"https://...\"> to prevent duplicate-URL dilution."},
    {"id": "UNM-38", "sev": "P2", "cat": "SEO", "desc": "Full HTML <head> missing og:image social preview metadata", "fix": "Add 1200x630 og:image and twitter:card=summary_large_image metadata."},
    {"id": "UNM-39", "sev": "P2", "cat": "GEO", "desc": "Full public HTML document missing Schema.org application/ld+json", "fix": "Embed validated <script type=\"application/ld+json\"> matching visible page facts."},
    {"id": "UNM-40", "sev": "P1", "cat": "SEO", "desc": "Anchor link missing href or using vague 'click here' / 'read more' text", "fix": "Give <a> a crawlable href and descriptive anchor text naming the destination."},
    {"id": "UNM-41", "sev": "P2", "cat": "Slop", "desc": "Decorative multi-color gradient fill on a background, button, or border", "fix": "Use one solid semantic surface token; reserve gradients for data scales, photo legibility scrims, or a brand that explicitly pins one."},
    {"id": "UNM-42", "sev": "P2", "cat": "Slop", "desc": "Stock AI purple accent (Tailwind indigo/violet/purple 400-700 or equivalent)", "fix": "Derive the accent from the product's real materials in DESIGN.md; waive with a reason only when the brand genuinely pins this hue."},
    {"id": "UNM-43", "sev": "P2", "cat": "Slop", "desc": "Colored shadow or glow (chromatic box-shadow, text-shadow, or drop-shadow)", "fix": "Keep shadows neutral and only on floating layers; show emphasis with solid fill, weight, or a 1px border instead of a colored halo."},
    {"id": "UNM-44", "sev": "P2", "cat": "Slop", "desc": "Heavy or stacked decorative drop shadow (elevation soup)", "fix": "Express depth with 1px borders and surface tint steps; keep one subtle neutral --shadow-overlay token for menus, popovers, and dialogs."},
    {"id": "UNM-45", "sev": "P2", "cat": "Slop", "desc": "Glassmorphism panel (backdrop-filter blur on a translucent surface)", "fix": "Use an opaque surface token with a 1px border; reserve backdrop blur for a modal scrim if at all."},
    {"id": "UNM-46", "sev": "P2", "cat": "Slop", "desc": "Blurred decorative orb or aurora blob (filter: blur >= 40px)", "fix": "Delete ambient blobs; let real product imagery, type scale, or a committed color field carry the atmosphere."},
    {"id": "UNM-47", "sev": "P2", "cat": "Motion", "desc": "Idle infinite decorative animation (float, bob, glow pulse, gradient shift, bounce)", "fix": "Animate only in response to user input or real state (loading, progress); remove ambient loops."},
    {"id": "UNM-48", "sev": "P3", "cat": "Sloppy", "desc": "Border-radius drift (more than 3 distinct radius steps in one file)", "fix": "Collapse radii into --radius-sm / --radius-md / --radius-lg tokens (plus none and full)."},
    {"id": "UNM-49", "sev": "P3", "cat": "Sloppy", "desc": "Magic-number drift (off-grid spacing, arbitrary spacing values, or z-index escalation)", "fix": "Use the 4px spacing scale tokens and a named z-index scale (--z-header, --z-overlay, --z-toast) instead of eyeballed values."},
    {"id": "UNM-50", "sev": "P2", "cat": "Copy", "desc": "Unverified social-proof filler (Trusted by 10,000+, Join 50k+, five-star strings)", "fix": "Show only sourced numbers and named customers with permission, or remove the claim; never invent counts, ratings, or logos."},
    {"id": "UNM-51", "sev": "P1", "cat": "GEO", "desc": "Malformed JSON-LD block (invalid JSON or missing @context)", "fix": "Emit valid JSON with \"@context\": \"https://schema.org\" and check it in the Schema Markup Validator."},
    {"id": "UNM-52", "sev": "P2", "cat": "SEO", "desc": "Relative or non-HTTPS canonical, og:url, og:image, or twitter:image URL", "fix": "Use absolute https:// URLs; social scrapers and search engines do not resolve relative paths reliably."},
    {"id": "UNM-53", "sev": "P2", "cat": "SEO", "desc": "Dead placeholder link (href=\"#\" or href=\"javascript:...\")", "fix": "Link to a real crawlable route, or use <button type=\"button\"> when the control performs an action."},
]

RULE_MAP: Dict[str, Dict[str, str]] = {r["id"]: r for r in RULES}
SARIF_LEVEL = {"P0": "error", "P1": "error", "P2": "warning", "P3": "note"}
SEV_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

AddFinding = Callable[..., None]

DISABLE_RE = re.compile(
    r"unmistakable-disable(?P<scope>-file)?\s+(?P<ids>UNM-\d{2}(?:\s*,\s*UNM-\d{2})*)\s*:\s*(?P<reason>[^*>\n]+)",
    re.I,
)
EYEBROW_RE = re.compile(r'class(?:Name)?\s*=\s*["\'][^"\']*\b(?:eyebrow|kicker|pre-title|overtitle|subheading-badge)\b', re.I)
HEADING_NUM_RE = re.compile(r"<h[1-3][^>]*>\s*(?:\[\s*0?\d+\s*(?:/\s*0?\d+)?\s*\]|0[1-9]\s*[./:-])\s*[A-Za-z]", re.I)
GRADIENT_TEXT_RE = re.compile(r"(?:background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text|\bbg-clip-text\b)", re.I)
SIDE_BAR_RE = re.compile(r"border-(?:left|inline-start)\s*:\s*(?:[3-9]|\d{2,})px\s+solid\b|\bborder-l-[48]\b", re.I)
FAKE_TELEMETRY_RE = re.compile(r">\s*(?:SCROLL\s+DOWN|SCROLL\s+TO\s+EXPLORE)\s*<|animate-ping[^>]*>[^<]*LIVE", re.I)
FILLER_COPY_RE = re.compile(
    r">\s*[^<{]*\b(?:seamless(?:ly)?|reimagined|unleash\s+the\s+power|elevate\s+your|next-generation\s+platform"
    r"|revolutionize\s+your|supercharge\s+your|unlock\s+the\s+(?:full\s+)?(?:power|potential)|harness\s+the\s+power"
    r"|game[-\s]chang(?:er|ing)|cutting[-\s]edge|state[-\s]of[-\s]the[-\s]art|blazing(?:ly)?[-\s]fast|world[-\s]class"
    r"|effortless(?:ly)?|to\s+the\s+next\s+level|in\s+today'?s\s+fast[-\s]paced|transform\s+the\s+way\s+you"
    r"|empower(?:s|ing)?\s+(?:you|your|teams|developers)|built\s+for\s+the\s+future\s+of)\b[^<]*<",
    re.I,
)
BR_EM_HEADING_RE = re.compile(r"<h[1-2]\b[^>]*>(?:(?!</h[1-2]>).)*<br\s*/?>\s*<(?:em|i)\b", re.I | re.S)
LOREM_RE = re.compile(r"\blorem\s+ipsum\b|\bexample@example\.com\b", re.I)
TRANSITION_ALL_RE = re.compile(r"transition\s*:\s*all\b|\btransition-all\b", re.I)
EASE_IN_RE = re.compile(r"transition[^;{}]*\bease-in\b(?!-out)", re.I)
WILL_CHANGE_BROAD_RE = re.compile(r"\*\s*\{[^}]*will-change\s*:|will-change\s*:\s*all\b|will-change\s*:[^;{}]+,[^;{}]+,[^;{}]+", re.I)
NON_INTERACTIVE_CLICK_RE = re.compile(
    r"<(?P<tag>div|span)\b(?P<attrs>[^>]*?)\b(?:onClick|@click|\(click\)|on:click)\s*=",
    re.I | re.S,
)
IMG_TAG_RE = re.compile(r"<img\b(?P<attrs>[^>]*?)/?>", re.I | re.S)
OUTLINE_NONE_RE = re.compile(r"outline\s*:\s*(?:none|0)\b|\boutline-none\b", re.I)
HEADING_TAG_RE = re.compile(r"<h([1-6])\b", re.I)
BUTTON_BLOCK_RE = re.compile(r"<button\b(?P<attrs>[^>]*)>(?P<body>.*?)</button>", re.I | re.S)
INPUT_TAG_RE = re.compile(r"<input\b(?P<attrs>[^>]*?)/?>", re.I | re.S)
HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
EMOJI_IN_CHROME_RE = re.compile(
    r"<(?:button|a|nav)\b[^>]*>[^<]*[\U0001F300-\U0001FAFF☀-➿]",
    re.I,
)
VAGUE_LINK_RE = re.compile(
    r"<a\b(?P<attrs>[^>]*)>\s*(?P<label>click\s+here|read\s+more|learn\s+more|here)\s*</a>",
    re.I,
)
ANCHOR_NO_HREF_RE = re.compile(r"<a\b(?![^>]*\bhref\s*=)[^>]*>", re.I)

# --- Color, light, and depth (UNM-06, UNM-07, UNM-41 to UNM-47) ---------------
COLOR_TOKEN_RE = re.compile(
    r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b|\b(?:rgba?|hsla?|oklch|oklab|lch|lab)\([^()]*\)|\b[a-zA-Z]{3,}\b",
    re.I,
)
COLOR_FUNC_PARSE_RE = re.compile(r"(rgba?|hsla?|oklch|oklab|lch|lab)\((.*)\)$", re.I | re.S)
GRADIENT_FN_RE = re.compile(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(", re.I)
PROP_BEFORE_RE = re.compile(r"([A-Za-z-]+)\s*:\s*[^;:{}]*$")
SHADOW_DECL_RE = re.compile(r"(?<![\w-])(box-shadow|text-shadow|boxShadow|textShadow)\s*:\s*[\"'`]?([^;{}\"'`]+)", re.I)
DROP_SHADOW_FN_RE = re.compile(r"(?<![\w-])drop-shadow\(", re.I)
ORB_FILTER_RE = re.compile(r"(?<![\w-])filter\s*:\s*[\"'`]?[^;{}\"'`]*?blur\(\s*(\d*\.?\d+)(px|rem)", re.I)
GLASS_DECL_RE = re.compile(r"(?:-webkit-)?(?:backdrop-filter|backdropFilter|WebkitBackdropFilter)\s*:\s*[\"'`]?[^;{}\"'`]*blur\(", re.I)
INFINITE_ANIM_RE = re.compile(r"(?<![\w-])animation(?:-iteration-count|IterationCount)?\s*:\s*[\"'`]?([^;{}\"'`]*\binfinite\b[^;{}\"'`]*)", re.I)
IDLE_ALLOW_RE = re.compile(r"spin|rotat|load|skeleton|shimmer|progress|indeterminate|caret|cursor|blink|typing|busy|pending", re.I)
OVERLAY_SELECTOR_RE = re.compile(r"overlay|backdrop|scrim|modal-bg|lightbox", re.I)

# --- Tailwind utility patterns ---------------------------------------------------
TW_NEUTRAL_FAMILIES = frozenset({
    "slate", "gray", "zinc", "neutral", "stone", "black", "white", "transparent",
    "current", "inherit", "mauve", "olive", "mist", "taupe",
})
TW_PURPLE_FAMILIES = frozenset({"indigo", "violet", "purple"})
TW_BLUE_FAMILIES = frozenset({"sky", "blue", "cyan", "teal"})
TW_PINK_FAMILIES = frozenset({"pink", "fuchsia", "rose"})
TW_GRADIENT_RE = re.compile(
    r"(?<![\w-])bg-(?:gradient-to-[a-z]{1,2}|linear-(?:to-[a-z]{1,2}|\d+|\[[^\]]+\])|radial(?:-\[[^\]]+\])?|conic(?:-\d+)?)(?![\w-])"
)
TW_STOP_RE = re.compile(r"(?<![\w-])(?:[a-z-]+:)?(?:from|via|to)-(?:([a-z]+)(?:-(\d{2,3}))?|\[([^\]]+)\])(?:/\d{1,3})?(?![\w-])")
TW_COLORED_SHADOW_RE = re.compile(r"(?<![\w-])shadow-([a-z]+)-\d{2,3}(?:/\d{1,3})?(?![\w-])")
TW_ARBITRARY_SHADOW_RE = re.compile(r"(?<![\w-])(drop-)?shadow-\[([^\]]+)\]")
TW_HEAVY_SHADOW_RE = re.compile(r"(?<![\w-])shadow-2xl(?![\w-])")
TW_GLASS_RE = re.compile(r"(?<![\w-])backdrop-blur(?:-(?!none\b)(?:xs|sm|md|lg|xl|2xl|3xl|\[[^\]]+\]))?(?![\w-])")
TW_ORB_RE = re.compile(r"(?<![\w-])blur-(?:(2xl|3xl)|\[(\d*\.?\d+)px\])(?![\w-])")
TW_IDLE_ANIM_RE = re.compile(
    r"(?<![\w-])animate-(?:bounce|float[\w-]*|glow[\w-]*|blob[\w-]*|gradient[\w-]*|wiggle|tilt|aurora[\w-]*|marquee[\w-]*|spin-slow|pulse-slow|shine[\w-]*)(?![\w-])"
)
TW_STOCK_PURPLE_RE = re.compile(
    r"(?<![\w-])(?:[a-z-]+:)*(?:bg|text|border|ring|outline|from|via|to|shadow|fill|stroke|accent|decoration|divide|caret)-(?:indigo|violet|purple)-(?:400|500|600|700)(?:/\d{1,3})?(?![\w-])"
)
TW_ROUNDED_RE = re.compile(
    r"(?<![\w-])rounded(?:-(?:t|b|l|r|s|e|tl|tr|bl|br|ss|se|es|ee))?(?:-(none|xs|sm|md|lg|xl|2xl|3xl|4xl|full|\[[^\]]+\]))?(?![\w-])"
)
TW_ARBITRARY_SPACING_RE = re.compile(
    r"(?<![\w-])-?(?:p|px|py|pt|pr|pb|pl|ps|pe|m|mx|my|mt|mr|mb|ml|ms|me|gap|gap-x|gap-y|space-x|space-y|inset|inset-x|inset-y|top|right|bottom|left)-\[(\d*\.?\d+)px\]"
)
TW_Z_RE = re.compile(r"(?<![\w-])z-\[(\d+)\]")
CLASS_ATTR_RE = re.compile(
    r"(?<![\w-])(?::?class|className|class:list|\[class\]|\[ngClass\])\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|\{\s*`([^`]*)`\s*\})"
)
CLASS_FN_RE = re.compile(r"\b(?:cn|clsx|cva|twMerge|classNames)\(([^()]*)\)")

# --- Sloppy-UI drift (UNM-48, UNM-49) --------------------------------------------
RADIUS_DECL_RE = re.compile(r"(?<![\w-])(?:border(?:-[a-z]+)*-radius|borderRadius)\s*:\s*[\"'`]?([^;{}\"'`]+)", re.I)
SPACING_DECL_RE = re.compile(
    r"(?<![\w-])(?:margin|padding|gap|row-gap|column-gap|inset|top|right|bottom|left)(?:-[a-z]+)*\s*:\s*([^;{}\"'`]+)",
    re.I,
)
PX_VALUE_RE = re.compile(r"(?<![\w.#-])(\d*\.?\d+)px\b")
Z_INDEX_RE = re.compile(r"(?:z-index|zIndex)\s*:\s*[\"'`]?(\d+)", re.I)
FUNC_CALL_RE = re.compile(r"\b[a-z-]+\([^()]*(?:\([^()]*\)[^()]*)*\)", re.I)

# --- Copy, structured data, and links (UNM-50 to UNM-53) -------------------------
SOCIAL_PROOF_RE = re.compile(
    r"\b(?:trusted|loved|used|chosen)\s+by\s+(?:over\s+|more\s+than\s+)?(?:\d[\d,.]*\s*[kKmM]?\+?|thousands|millions|hundreds\s+of\s+thousands)"
    r"|\bjoin\s+(?:over\s+|more\s+than\s+)?\d[\d,.]*\s*[kKmM]?\+"
    r"|\b\d[\d,.]*\s*[kKmM]?\+\s+(?:happy|satisfied|active)\s+(?:customers|users|developers|teams|creators|members)"
    "|[★⭐]{4,}",
    re.I,
)
JSONLD_BLOCK_RE = re.compile(r"<script\b[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.I | re.S)
META_TAG_RE = re.compile(r"<meta\b[^>]*>", re.I)
LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.I)
ATTR_RE = re.compile(r"([\w:-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')")
ABSOLUTE_URL_META = frozenset({"og:image", "og:image:url", "og:image:secure_url", "og:url", "twitter:image"})
DEAD_LINK_RE = re.compile(r"<a\b[^>]*\bhref\s*=\s*(?:\"(?:#|javascript:[^\"]*)\"|'(?:#|javascript:[^']*)')", re.I)

NEUTRAL_COLOR_WORDS = frozenset({
    "black", "white", "transparent", "currentcolor", "gray", "grey", "silver", "gainsboro",
    "whitesmoke", "dimgray", "dimgrey", "darkgray", "darkgrey", "lightgray", "lightgrey", "snow",
    "ivory", "linen", "beige",
})
LIGHT_COLOR_WORDS = frozenset({"white", "snow", "ivory", "whitesmoke", "linen", "gainsboro"})
PURPLE_WORDS = frozenset({
    "purple", "violet", "indigo", "blueviolet", "rebeccapurple", "mediumpurple", "darkviolet",
    "darkorchid", "mediumslateblue", "slateblue",
})
BLUE_WORDS = frozenset({
    "blue", "navy", "royalblue", "dodgerblue", "skyblue", "deepskyblue", "steelblue", "cyan", "aqua",
    "teal", "turquoise", "darkcyan", "lightblue", "cornflowerblue",
})
PINK_WORDS = frozenset({"pink", "hotpink", "deeppink", "fuchsia", "magenta", "orchid", "plum", "mediumvioletred"})
OTHER_CHROMATIC_WORDS = frozenset({
    "red", "orange", "yellow", "green", "lime", "gold", "coral", "crimson", "tomato", "salmon",
    "maroon", "olive", "chartreuse", "orangered", "firebrick", "seagreen", "forestgreen",
})


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def collect_targets(target: Path) -> List[Path]:
    if target.is_file():
        return [target] if target.suffix.lower() in ALL_SCAN_EXTS else []
    found: List[Path] = []
    for root, dirs, files in os.walk(target):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for fname in sorted(files):
            p = Path(root) / fname
            if p.suffix.lower() in ALL_SCAN_EXTS:
                try:
                    if p.stat().st_size <= MAX_SCAN_BYTES:
                        found.append(p)
                except OSError:
                    continue
    return found


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def keep_newlines(m: "re.Match[str]") -> str:
    return "\n" * m.group(0).count("\n")


def strip_comments(text: str) -> str:
    text = re.sub(r"<!--.*?-->", keep_newlines, text, flags=re.S)
    return re.sub(r"/\*.*?\*/", keep_newlines, text, flags=re.S)


def parse_waivers(lines: Sequence[str]) -> Tuple[Dict[Tuple[Optional[int], str], int], Set[Tuple[Optional[int], str]]]:
    """Return waiver map {(line_or_None, rule_id): decl_line} and empty used set."""
    waivers: Dict[Tuple[Optional[int], str], int] = {}
    for idx, raw in enumerate(lines, 1):
        for m in DISABLE_RE.finditer(raw):
            is_file = bool(m.group("scope"))
            ids = [tok.strip().upper() for tok in m.group("ids").split(",")]
            for rid in ids:
                if is_file:
                    waivers[(None, rid)] = idx
                else:
                    waivers[(idx, rid)] = idx
                    waivers[(idx + 1, rid)] = idx
    return waivers, set()


def parse_px(size_value: str) -> Optional[float]:
    val = size_value.strip().lower()
    m_px = re.fullmatch(r"([0-9]*\.?[0-9]+)px", val)
    if m_px:
        return float(m_px.group(1))
    m_rem = re.fullmatch(r"([0-9]*\.?[0-9]+)rem", val)
    if m_rem:
        return float(m_rem.group(1)) * REM_BASE_PX
    return None


def extract_style_blocks(text: str, suffix: str) -> List[Tuple[int, str]]:
    if suffix in STYLE_EXTS:
        return [(1, text)]
    blocks: List[Tuple[int, str]] = []
    for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", text, re.I | re.S):
        blocks.append((line_of(text, m.start(1)), m.group(1)))
    return blocks


def balanced_inner(text: str, open_paren_idx: int, limit: int = 2000) -> str:
    """Return the text inside the parenthesis group opening at open_paren_idx."""
    depth = 0
    end = min(len(text), open_paren_idx + limit)
    for i in range(open_paren_idx, end):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren_idx + 1:i]
    return text[open_paren_idx + 1:end]


def split_top_level(value: str, sep: str = ",") -> List[str]:
    parts: List[str] = []
    depth = 0
    buf: List[str] = []
    for ch in value:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def class_strings(text: str) -> List[Tuple[int, str]]:
    """Return (offset, value) for class attributes and cn()/clsx() arguments."""
    out: List[Tuple[int, str]] = []
    for m in CLASS_ATTR_RE.finditer(text):
        for g in (1, 2, 3):
            if m.group(g) is not None:
                out.append((m.start(g), m.group(g)))
                break
    for m in CLASS_FN_RE.finditer(text):
        out.append((m.start(1), m.group(1)))
    return out


def enclosing_string(text: str, pos: int, max_span: int = 1200) -> str:
    """Return the quoted class/string literal surrounding pos (best effort)."""
    start = max(0, pos - max_span)
    left = max(text.rfind('"', start, pos), text.rfind("'", start, pos), text.rfind("`", start, pos))
    if left == -1:
        return text[start:min(len(text), pos + max_span)]
    right = text.find(text[left], pos)
    if right == -1:
        right = min(len(text), pos + max_span)
    return text[left + 1:right]


# ---------------------------------------------------------------------------
# Color model helpers (stdlib-only approximations, good enough for lint heuristics)
# ---------------------------------------------------------------------------

def _num(tok: str, pct_scale: float = 1.0) -> float:
    tok = tok.replace("deg", "")
    if tok.endswith("%"):
        return float(tok[:-1]) * pct_scale
    return float(tok)


def _family(hue: float, purple: Tuple[float, float], blue: Tuple[float, float], pink: Tuple[float, float]) -> str:
    if purple[0] <= hue < purple[1]:
        return "purple"
    if blue[0] <= hue < blue[1]:
        return "blue"
    if pink[0] <= hue < pink[1]:
        return "pink"
    return "other"


def _rgb_info(r: float, g: float, b: float, alpha: float) -> Dict[str, object]:
    mx, mn = max(r, g, b), min(r, g, b)
    spread = mx - mn
    chromatic = spread >= CHROMA_MIN_RGB_SPREAD and alpha >= MIN_VISIBLE_ALPHA
    family: Optional[str] = None
    if chromatic:
        if mx == r:
            hue = (60.0 * ((g - b) / spread)) % 360.0
        elif mx == g:
            hue = 60.0 * ((b - r) / spread) + 120.0
        else:
            hue = 60.0 * ((r - g) / spread) + 240.0
        family = _family(hue, PURPLE_HUE, BLUE_CYAN_HUE, PINK_HUE)
    return {
        "chromatic": chromatic,
        "family": family,
        "light": (r + g + b) / 3.0 >= LIGHT_NEUTRAL_MIN_RGB and alpha >= MIN_VISIBLE_ALPHA,
        "rgb": (int(round(r)), int(round(g)), int(round(b))),
        "oklch": None,
    }


def color_info(token: str) -> Optional[Dict[str, object]]:
    """Classify a CSS color token. Returns None when the token is not a color."""
    t = token.strip().lower()
    if t.startswith("#"):
        h = t[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8) or not re.fullmatch(r"[0-9a-f]+", h):
            return None
        alpha = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
        return _rgb_info(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    m = COLOR_FUNC_PARSE_RE.match(t)
    if m:
        fn, inner = m.group(1), m.group(2)
        if "var(" in inner or "from " in inner or "calc(" in inner:
            return None
        nums = re.findall(r"-?\d*\.?\d+(?:%|deg)?", inner)
        if len(nums) < 3:
            return None
        try:
            alpha = _num(nums[3], 0.01) if len(nums) >= 4 else 1.0
            if fn.startswith("rgb"):
                r, g, b = (_num(n, 2.55) for n in nums[:3])
                return _rgb_info(r, g, b, alpha)
            if fn.startswith("hsl"):
                hue = _num(nums[0]) % 360.0
                sat, light = float(nums[1].rstrip("%")), float(nums[2].rstrip("%"))
                chromatic = sat >= HSL_MIN_SAT and HSL_LIGHTNESS_WINDOW[0] < light < HSL_LIGHTNESS_WINDOW[1] and alpha >= MIN_VISIBLE_ALPHA
                return {
                    "chromatic": chromatic,
                    "family": _family(hue, PURPLE_HUE, BLUE_CYAN_HUE, PINK_HUE) if chromatic else None,
                    "light": light >= 85.0,
                    "rgb": None,
                    "oklch": None,
                }
            if fn == "oklch":
                lightness = _num(nums[0], 0.01)
                chroma = _num(nums[1], 0.004)
                hue = _num(nums[2]) % 360.0
                chromatic = chroma >= CHROMA_MIN_OKLCH and alpha >= MIN_VISIBLE_ALPHA
                return {
                    "chromatic": chromatic,
                    "family": _family(hue, OKLCH_PURPLE_HUE, OKLCH_BLUE_HUE, OKLCH_PINK_HUE) if chromatic else None,
                    "light": lightness >= 0.85,
                    "rgb": None,
                    "oklch": (chroma, hue),
                }
            if fn == "lch":
                chroma = _num(nums[1], 1.5)
                return {"chromatic": chroma >= CHROMA_MIN_LAB and alpha >= MIN_VISIBLE_ALPHA, "family": None,
                        "light": _num(nums[0]) >= 85.0, "rgb": None, "oklch": None}
            if fn in ("oklab", "lab"):
                scale = 0.004 if fn == "oklab" else 1.25
                chroma = math.hypot(_num(nums[1], scale), _num(nums[2], scale))
                floor = CHROMA_MIN_OKLCH if fn == "oklab" else CHROMA_MIN_LAB
                light_floor = 0.85 if fn == "oklab" else 85.0
                return {"chromatic": chroma >= floor and alpha >= MIN_VISIBLE_ALPHA, "family": None,
                        "light": _num(nums[0], 0.01 if fn == "oklab" else 1.0) >= light_floor, "rgb": None, "oklch": None}
        except ValueError:
            return None
        return None
    if t in NEUTRAL_COLOR_WORDS:
        return {"chromatic": False, "family": None, "light": t in LIGHT_COLOR_WORDS, "rgb": None, "oklch": None}
    for words, fam in ((PURPLE_WORDS, "purple"), (BLUE_WORDS, "blue"), (PINK_WORDS, "pink"), (OTHER_CHROMATIC_WORDS, "other")):
        if t in words:
            return {"chromatic": True, "family": fam, "light": False, "rgb": None, "oklch": None}
    return None


def is_stock_purple(token: str) -> bool:
    t = token.strip().lower()
    if t.startswith("#"):
        return t in STOCK_PURPLE_HEX
    info = color_info(t)
    if not info or not info["chromatic"]:
        return False
    if info["rgb"] is not None:
        return info["rgb"] in STOCK_PURPLE_RGB
    if info["oklch"] is not None:
        chroma, hue = info["oklch"]  # type: ignore[misc]
        return chroma >= STOCK_PURPLE_OKLCH_MIN_CHROMA and STOCK_PURPLE_OKLCH_HUE[0] <= hue <= STOCK_PURPLE_OKLCH_HUE[1]
    return False


STOCK_PURPLE_RGB = frozenset(
    (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)) for h in STOCK_PURPLE_HEX
)


def classify_gradient(args: str) -> Optional[str]:
    """Return UNM-07 for the purple/blue/pink cliche, UNM-41 for any other multi-hue fill."""
    stops: List[Tuple[str, Optional[str]]] = []
    for m in COLOR_TOKEN_RE.finditer(args):
        info = color_info(m.group(0))
        if info and info["chromatic"]:
            stops.append((re.sub(r"\s+", "", m.group(0).lower()), info["family"]))  # type: ignore[arg-type]
    families = {f for _, f in stops}
    if "purple" in families and families & {"blue", "pink"}:
        return "UNM-07"
    if len({s for s, _ in stops}) >= 2:
        return "UNM-41"
    return None


def parse_shadow_layer(layer: str) -> Tuple[List[float], Optional[Dict[str, object]], bool]:
    low = layer.lower()
    color: Optional[Dict[str, object]] = None
    for m in COLOR_TOKEN_RE.finditer(low):
        info = color_info(m.group(0))
        if info is not None:
            color = info
            break
    stripped = re.sub(r"#[0-9a-f]{3,8}\b|\b[a-z-]+\([^()]*\)", " ", low)
    lengths: List[float] = []
    for tok in stripped.split():
        mm = re.fullmatch(r"(-?\d*\.?\d+)(px|rem|em)?", tok)
        if mm:
            val = float(mm.group(1))
            if mm.group(2) in ("rem", "em"):
                val *= REM_BASE_PX
            lengths.append(val)
    return lengths, color, "inset" in low


def classify_shadow(prop: str, value: str) -> Optional[str]:
    """Return UNM-06 (neon halo), UNM-43 (colored glow), UNM-44 (heavy/stacked), or None."""
    prop_l = prop.lower()
    if value.strip().lower() in ("none", "inherit", "initial", "unset"):
        return None
    is_text = "text" in prop_l
    is_drop = prop_l == "drop-shadow"
    glow = chroma = heavy = False
    blurred_layers = 0
    for layer in split_top_level(value):
        lengths, color, inset = parse_shadow_layer(layer)
        if len(lengths) < 2:
            continue
        x, y = lengths[0], lengths[1]
        blur = lengths[2] if len(lengths) > 2 else 0.0
        spread = lengths[3] if (len(lengths) > 3 and not is_text and not is_drop) else 0.0
        chromatic = bool(color and color["chromatic"])
        light = bool(color and color["light"])
        zero_offset = x == 0 and y == 0
        if blur > 0 and not inset:
            blurred_layers += 1
        if is_text:
            if (zero_offset and blur >= TEXT_GLOW_MIN_BLUR_PX) or (chromatic and blur > 0):
                chroma = True
            continue
        if zero_offset and blur >= GLOW_MIN_BLUR_PX and not inset and (chromatic or light):
            if is_drop:
                chroma = True
            else:
                glow = True
        elif chromatic and blur > 0 and not inset:
            chroma = True
        if not inset and (blur >= HEAVY_SHADOW_MIN_BLUR_PX or spread >= HEAVY_SHADOW_MIN_SPREAD_PX):
            heavy = True
    if blurred_layers > MAX_SHADOW_LAYERS and not is_text:
        heavy = True
    if glow:
        return "UNM-06"
    if chroma:
        return "UNM-43"
    if heavy:
        return "UNM-44"
    return None


# ---------------------------------------------------------------------------
# Property-level scans shared by stylesheets, inline styles, and JSX style objects
# ---------------------------------------------------------------------------

def scan_style_values(text: str, ln: Callable[[int], int], add_finding: AddFinding) -> None:
    for m in GRADIENT_FN_RE.finditer(text):
        prop_m = PROP_BEFORE_RE.search(text[max(0, m.start() - 300):m.start()])
        prop = prop_m.group(1).lower() if prop_m else ""
        if "mask" in prop:
            continue
        rule = classify_gradient(balanced_inner(text, m.end() - 1))
        if rule:
            add_finding(rule, ln(m.start()))

    for m in SHADOW_DECL_RE.finditer(text):
        rule = classify_shadow(m.group(1), m.group(2))
        if rule:
            add_finding(rule, ln(m.start()))
    for m in DROP_SHADOW_FN_RE.finditer(text):
        rule = classify_shadow("drop-shadow", balanced_inner(text, m.end() - 1))
        if rule:
            add_finding(rule, ln(m.start()))

    for m in ORB_FILTER_RE.finditer(text):
        px = float(m.group(1)) * (REM_BASE_PX if m.group(2).lower() == "rem" else 1.0)
        if px >= ORB_MIN_BLUR_PX:
            add_finding("UNM-46", ln(m.start()), extra=f"blur({m.group(1)}{m.group(2)}).")


def scan_tailwind(text: str, add_finding: AddFinding) -> None:
    for m in TW_GRADIENT_RE.finditer(text):
        klass = enclosing_string(text, m.start())
        families: Set[str] = set()
        chromatic_stops: Set[str] = set()
        for s in TW_STOP_RE.finditer(klass):
            fam, shade, arbitrary = s.group(1), s.group(2), s.group(3)
            if arbitrary:
                info = color_info(arbitrary.replace("_", " "))
                if info and info["chromatic"]:
                    chromatic_stops.add(arbitrary.lower())
                    families.add(str(info["family"]))
                continue
            if not fam or fam in TW_NEUTRAL_FAMILIES or not shade:
                continue
            chromatic_stops.add(f"{fam}-{shade}")
            if fam in TW_PURPLE_FAMILIES:
                families.add("purple")
            elif fam in TW_BLUE_FAMILIES:
                families.add("blue")
            elif fam in TW_PINK_FAMILIES:
                families.add("pink")
        if "purple" in families and families & {"blue", "pink"}:
            add_finding("UNM-07", line_of(text, m.start()))
        elif len(chromatic_stops) >= 2:
            add_finding("UNM-41", line_of(text, m.start()))

    for m in TW_COLORED_SHADOW_RE.finditer(text):
        if m.group(1) not in TW_NEUTRAL_FAMILIES:
            add_finding("UNM-43", line_of(text, m.start()), extra=m.group(0))
    for m in TW_ARBITRARY_SHADOW_RE.finditer(text):
        rule = classify_shadow("drop-shadow" if m.group(1) else "box-shadow", m.group(2).replace("_", " "))
        if rule:
            add_finding(rule, line_of(text, m.start()))
    for m in TW_HEAVY_SHADOW_RE.finditer(text):
        add_finding("UNM-44", line_of(text, m.start()), extra="shadow-2xl")
    for m in TW_GLASS_RE.finditer(text):
        klass = enclosing_string(text, m.start())
        if re.search(r"(?<![\w-])inset-0(?![\w-])", klass):
            continue
        add_finding("UNM-45", line_of(text, m.start()), extra=m.group(0))
    for m in TW_ORB_RE.finditer(text):
        px = TW_BLUR_PX.get(m.group(1) or "", 0.0) if m.group(1) else float(m.group(2))
        if px >= ORB_MIN_BLUR_PX:
            add_finding("UNM-46", line_of(text, m.start()), extra=m.group(0))
    for m in TW_IDLE_ANIM_RE.finditer(text):
        add_finding("UNM-47", line_of(text, m.start()), extra=m.group(0))


# ---------------------------------------------------------------------------
# Whole-file aggregate checks (reported once per file)
# ---------------------------------------------------------------------------

def scan_file_aggregates(text: str, is_markup: bool, add_finding: AddFinding) -> None:
    # UNM-42 stock AI purple accent
    purple_hits: List[int] = []
    for m in re.finditer(r"#[0-9a-fA-F]{6}\b|\brgba?\([^()]*\)|\boklch\([^()]*\)", text):
        if is_stock_purple(m.group(0)):
            purple_hits.append(m.start())
    if is_markup:
        purple_hits.extend(m.start() for m in TW_STOCK_PURPLE_RE.finditer(text))
    if purple_hits:
        first = min(purple_hits)
        add_finding("UNM-42", line_of(text, first), extra=f"{len(purple_hits)} stock indigo/violet/purple reference(s) in file.")

    # UNM-48 radius drift
    radii: Dict[str, int] = {}
    for m in RADIUS_DECL_RE.finditer(text):
        value = FUNC_CALL_RE.sub(" ", m.group(1).lower())
        for tok in re.split(r"[\s/,]+", value):
            tok = tok.strip()
            if not tok or tok in {"0", "0px", "50%", "100%", "inherit", "initial", "unset", "full"}:
                continue
            if re.fullmatch(r"\d+", tok):
                tok = f"{tok}px"
            num = re.match(r"(\d*\.?\d+)px$", tok)
            if num and float(num.group(1)) >= Z_INDEX_ESCALATION:
                continue  # 999px / 9999px pill radius is "full"
            if re.fullmatch(r"\d*\.?\d+(?:px|rem|em|%)", tok):
                radii.setdefault(tok, m.start())
    if len(radii) > MAX_RADIUS_STEPS:
        add_finding("UNM-48", line_of(text, min(radii.values())),
                    extra=f"{len(radii)} radius literals: {', '.join(sorted(radii))}.")
    elif is_markup:
        tw_radii: Dict[str, int] = {}
        for start, klass in class_strings(text):
            for m in TW_ROUNDED_RE.finditer(klass):
                size = m.group(1) or "base"
                if size not in {"none", "full"}:
                    tw_radii.setdefault(size, start + m.start())
        if len(tw_radii) > MAX_RADIUS_STEPS:
            add_finding("UNM-48", line_of(text, min(tw_radii.values())),
                        extra=f"{len(tw_radii)} rounded-* steps: {', '.join(sorted(tw_radii))}.")

    # UNM-49 magic-number drift: off-grid spacing, arbitrary spacing, z-index escalation
    off_grid: List[Tuple[int, str]] = []
    for m in SPACING_DECL_RE.finditer(text):
        for pm in PX_VALUE_RE.finditer(m.group(1)):
            val = float(pm.group(1))
            if val > SPACING_NUDGE_MAX_PX and (val % 2 != 0):
                off_grid.append((m.start(), f"{pm.group(1)}px"))
    if is_markup:
        for m in TW_ARBITRARY_SPACING_RE.finditer(text):
            off_grid.append((m.start(), m.group(0)))
    if len(off_grid) > MAX_OFF_GRID_SPACING:
        sample = ", ".join(v for _, v in off_grid[:4])
        add_finding("UNM-49", line_of(text, off_grid[0][0]), extra=f"{len(off_grid)} off-grid spacing values ({sample}).")
    z_hits = [(m.start(), m.group(1)) for m in Z_INDEX_RE.finditer(text) if int(m.group(1)) >= Z_INDEX_ESCALATION]
    if is_markup:
        z_hits.extend((m.start(), m.group(1)) for m in TW_Z_RE.finditer(text) if int(m.group(1)) >= Z_INDEX_ESCALATION)
    if z_hits:
        first_pos, first_val = min(z_hits)
        add_finding("UNM-49", line_of(text, first_pos), extra=f"z-index escalation ({first_val}).")


# ---------------------------------------------------------------------------
# Stylesheet and markup scanners
# ---------------------------------------------------------------------------

def scan_css_block(css: str, base_line: int, add_finding: AddFinding) -> None:
    def ln(offset: int) -> int:
        return base_line + css.count("\n", 0, offset)

    for m in GRADIENT_TEXT_RE.finditer(css):
        add_finding("UNM-03", ln(m.start()))
    for m in SIDE_BAR_RE.finditer(css):
        add_finding("UNM-05", ln(m.start()))
    for m in TRANSITION_ALL_RE.finditer(css):
        add_finding("UNM-18", ln(m.start()))
    for m in EASE_IN_RE.finditer(css):
        add_finding("UNM-19", ln(m.start()))
    for m in WILL_CHANGE_BROAD_RE.finditer(css):
        add_finding("UNM-21", ln(m.start()))

    scan_style_values(css, ln, add_finding)

    has_motion = bool(re.search(r"@keyframes\b|\btransition\s*:(?!\s*none)|\banimation\s*:(?!\s*none)", css, re.I))
    has_rm_guard = bool(re.search(r"prefers-reduced-motion\s*:\s*reduce", css, re.I))
    if has_motion and not has_rm_guard:
        m_first = re.search(r"@keyframes\b|\btransition\s*:|\banimation\s*:", css, re.I)
        add_finding("UNM-20", ln(m_first.start()) if m_first else base_line)

    has_focus_visible = bool(re.search(r":focus-visible\b", css))
    for m in OUTLINE_NONE_RE.finditer(css):
        if not has_focus_visible:
            add_finding("UNM-26", ln(m.start()))

    # Font families (excluding generic fallbacks and var() references)
    families: Set[str] = set()
    first_fam_line = base_line
    for m in re.finditer(r"font-family\s*:\s*([^;{}]+)", css, re.I):
        raw = m.group(1).strip()
        if raw.startswith("var(") or "{{" in raw:
            continue
        primary = raw.split(",")[0].strip().strip("\"'").lower()
        if primary and primary not in {"inherit", "system-ui", "sans-serif", "serif", "monospace", "ui-sans-serif", "ui-monospace"}:
            if not families:
                first_fam_line = ln(m.start())
            families.add(primary)
    if len(families) > MAX_FONT_FAMILIES:
        add_finding("UNM-13", first_fam_line, extra=f"Found {len(families)} families: {', '.join(sorted(families))}.")

    # Per-rule checks: font sizes, form controls, glassmorphism, idle infinite animation
    distinct_sizes: Set[str] = set()
    first_size_line = base_line
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", css, re.S):
        selector = m.group(1).strip()
        body = m.group(2)
        body_offset = m.start(2)
        is_form_ctrl = bool(re.search(r"\b(?:input|select|textarea)\b", selector, re.I))
        has_uppercase = bool(re.search(r"text-transform\s*:\s*uppercase", body, re.I))
        has_wide_track = bool(re.search(r"letter-spacing\s*:\s*(?:0?\.[1-9]|[1-9])", body, re.I))
        for sm in re.finditer(r"font-size\s*:\s*([^;{}]+)", body, re.I):
            sval = sm.group(1).strip()
            sline = ln(body_offset + sm.start())
            if not sval.startswith("var("):
                if not distinct_sizes:
                    first_size_line = sline
                distinct_sizes.add(sval.lower())
            px = parse_px(sval)
            if px is not None:
                if px < MIN_READABLE_PX:
                    add_finding("UNM-15", sline, extra=f"Computed {px:.1f}px ('{sval}').")
                if is_form_ctrl and px < IOS_INPUT_MIN_PX:
                    add_finding("UNM-16", sline, extra=f"Form control size {px:.1f}px ('{sval}') < 16px.")
                if has_uppercase and has_wide_track and px <= 13.0:
                    add_finding("UNM-17", sline)

        glass = GLASS_DECL_RE.search(body)
        if glass and not OVERLAY_SELECTOR_RE.search(selector):
            add_finding("UNM-45", ln(body_offset + glass.start()))

        anim = INFINITE_ANIM_RE.search(body)
        if anim and not IDLE_ALLOW_RE.search(selector + " " + body):
            add_finding("UNM-47", ln(body_offset + anim.start()), extra=anim.group(1).strip()[:60])

    if len(distinct_sizes) > MAX_FONT_SIZES_PER_FILE:
        add_finding("UNM-14", first_size_line, extra=f"Found {len(distinct_sizes)} literal font sizes.")

    # Scattered raw hex values outside :root / [data-theme] / @theme blocks
    stripped_tokens = re.sub(r"(?::root|\[data-theme[^\]]*\]|@theme[^{]*)\{[^{}]*\}", "", css, flags=re.S)
    raw_hex_matches = list(HEX_COLOR_RE.finditer(stripped_tokens))
    if len(raw_hex_matches) > MAX_RAW_HEX_OUTSIDE_TOKENS:
        add_finding("UNM-30", base_line, extra=f"Found {len(raw_hex_matches)} raw hex literals outside token blocks.")


def scan_markup(text: str, add_finding: AddFinding) -> None:
    # Strip HTML and JSX block comments so documentation comments do not false-positive
    clean = re.sub(r"<!--.*?-->", keep_newlines, text, flags=re.S)
    clean = re.sub(r"\{/\*.*?\*/\}", keep_newlines, clean, flags=re.S)

    for m in EYEBROW_RE.finditer(clean):
        add_finding("UNM-01", line_of(clean, m.start()))
    for m in HEADING_NUM_RE.finditer(clean):
        add_finding("UNM-02", line_of(clean, m.start()))
    for m in GRADIENT_TEXT_RE.finditer(clean):
        add_finding("UNM-03", line_of(clean, m.start()))
    for m in FAKE_TELEMETRY_RE.finditer(clean):
        add_finding("UNM-08", line_of(clean, m.start()))
    for m in FILLER_COPY_RE.finditer(clean):
        add_finding("UNM-09", line_of(clean, m.start()))
    for m in BR_EM_HEADING_RE.finditer(clean):
        add_finding("UNM-10", line_of(clean, m.start()))
    for m in LOREM_RE.finditer(clean):
        add_finding("UNM-12", line_of(clean, m.start()))
    for m in TRANSITION_ALL_RE.finditer(clean):
        add_finding("UNM-18", line_of(clean, m.start()))
    for m in EMOJI_IN_CHROME_RE.finditer(clean):
        add_finding("UNM-32", line_of(clean, m.start()))

    # Inline styles, JSX style objects, and Tailwind utilities (stylesheet blocks are scanned separately)
    no_style = re.sub(r"<style\b[^>]*>.*?</style>", keep_newlines, clean, flags=re.I | re.S)
    scan_style_values(no_style, lambda off: line_of(no_style, off), add_finding)
    scan_tailwind(no_style, add_finding)
    for m in GLASS_DECL_RE.finditer(no_style):
        add_finding("UNM-45", line_of(no_style, m.start()))
    for m in INFINITE_ANIM_RE.finditer(no_style):
        if not IDLE_ALLOW_RE.search(m.group(1)):
            add_finding("UNM-47", line_of(no_style, m.start()), extra=m.group(1).strip()[:60])

    # Visible prose only (outside <script> and <style>)
    prose_only = re.sub(r"<(?:script|style)\b[^>]*>.*?</(?:script|style)>", keep_newlines, clean, flags=re.I | re.S)
    for m in re.finditer(r">([^<]*" + re.escape(EM_DASH_CHAR) + r"[^<]*)<", prose_only):
        add_finding("UNM-11", line_of(prose_only, m.start()))
    for seg in re.finditer(r">([^<]+)<", prose_only):
        sp = SOCIAL_PROOF_RE.search(seg.group(1))
        if sp:
            add_finding("UNM-50", line_of(prose_only, seg.start(1) + sp.start()), extra=f"'{sp.group(0).strip()}'.")

    # Nested card detection: class="...card..." containing another class="...card..."
    card_open_re = re.compile(r'<(?:div|article|section)\b[^>]*\bclass(?:Name)?\s*=\s*["\'][^"\']*\bcard\b(?![-a-z])[^"\']*["\'][^>]*>', re.I)
    cards = list(card_open_re.finditer(clean))
    if len(cards) >= 2:
        for idx in range(len(cards) - 1):
            between = clean[cards[idx].end():cards[idx + 1].start()]
            closes = len(re.findall(r"</(?:div|article|section)>", between, re.I))
            opens = len(re.findall(r"<(?:div|article|section)\b", between, re.I))
            if closes <= opens:
                add_finding("UNM-04", line_of(clean, cards[idx + 1].start()))
                break

    # Non-interactive click handlers
    for m in NON_INTERACTIVE_CLICK_RE.finditer(clean):
        attrs = m.group("attrs")
        if not re.search(r"\brole\s*=", attrs, re.I) or not re.search(r"\btab[Ii]ndex\s*=", attrs):
            add_finding("UNM-22", line_of(clean, m.start()))

    # <img> alt, dimensions/aspect-ratio, and above-the-fold lazy loading
    has_aspect_css = bool(re.search(r"aspect-ratio\s*:", clean, re.I))
    for idx, m in enumerate(IMG_TAG_RE.finditer(clean)):
        attrs = m.group("attrs")
        ln = line_of(clean, m.start())
        if not re.search(r"\balt\s*=", attrs, re.I):
            add_finding("UNM-23", ln)
        has_wh = bool(re.search(r"\bwidth\s*=", attrs, re.I) and re.search(r"\bheight\s*=", attrs, re.I))
        has_inline_ar = bool(re.search(r"aspect-ratio|\baspect-", attrs, re.I))
        if not (has_wh or has_inline_ar or has_aspect_css):
            add_finding("UNM-24", ln)
        if idx == 0 and ln <= HERO_FOLD_MAX_LINE and re.search(r'loading\s*=\s*["\']lazy["\']', attrs, re.I):
            add_finding("UNM-25", ln)

    # Heading hierarchy
    prev_level = 0
    for m in HEADING_TAG_RE.finditer(clean):
        lvl = int(m.group(1))
        if prev_level and lvl > prev_level + 1:
            add_finding("UNM-27", line_of(clean, m.start()), extra=f"<h{prev_level}> jumped directly to <h{lvl}>.")
        prev_level = lvl

    # Icon-only <button> without aria-label
    for m in BUTTON_BLOCK_RE.finditer(clean):
        attrs, body = m.group("attrs"), m.group("body")
        if re.search(r"\baria-label(?:ledby)?\s*=", attrs, re.I):
            continue
        visible_text = re.sub(r"<[^>]+>", "", body).strip()
        if not visible_text:
            add_finding("UNM-28", line_of(clean, m.start()))

    # Form <input> without label / aria-label (excluding hidden/submit/button/reset)
    label_fors = set(re.findall(r'<label\b[^>]*\b(?:for|htmlFor)\s*=\s*["\']([^"\']+)["\']', clean, re.I))
    label_spans = [(m.start(), m.end()) for m in re.finditer(r"<label\b.*?</label>", clean, re.I | re.S)]
    for m in INPUT_TAG_RE.finditer(clean):
        attrs = m.group("attrs")
        if re.search(r'\btype\s*=\s*["\'](?:hidden|submit|button|reset|image)["\']', attrs, re.I):
            continue
        if re.search(r"\baria-label(?:ledby)?\s*=", attrs, re.I):
            continue
        id_m = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', attrs, re.I)
        if id_m and id_m.group(1) in label_fors:
            continue
        pos = m.start()
        if any(s <= pos <= e for s, e in label_spans):
            continue
        add_finding("UNM-29", line_of(clean, pos))

    # RTL physical properties check when dir="rtl" is declared
    if re.search(r'\bdir\s*=\s*["\']rtl["\']', clean, re.I):
        m_phys = re.search(r"(?:margin|padding)-(?:left|right)\s*:\s*[^0;{}]", clean, re.I)
        if m_phys:
            add_finding("UNM-31", line_of(clean, m_phys.start()))

    # Anchor links
    for m in VAGUE_LINK_RE.finditer(clean):
        add_finding("UNM-40", line_of(clean, m.start()), extra=f"Vague anchor label '{m.group('label').strip()}'.")
    for m in ANCHOR_NO_HREF_RE.finditer(clean):
        add_finding("UNM-40", line_of(clean, m.start()), extra="<a> tag is missing href attribute.")
    for m in DEAD_LINK_RE.finditer(clean):
        add_finding("UNM-53", line_of(clean, m.start()))

    # JSON-LD validity (skip template expressions such as {JSON.stringify(...)} or {{ ... }})
    for m in JSONLD_BLOCK_RE.finditer(clean):
        body = m.group(1).strip()
        if not body or re.search(r"\{\{|\{%|\$\{|<%", body) or re.match(r"\{\s*[^\s\"}]", body):
            continue
        try:
            data = json.loads(body)
        except ValueError as exc:
            add_finding("UNM-51", line_of(clean, m.start(1)), extra=f"Invalid JSON: {str(exc)[:80]}.")
            continue
        if '"@context"' not in body:
            add_finding("UNM-51", line_of(clean, m.start(1)), extra="Missing \"@context\": \"https://schema.org\".")
        elif not isinstance(data, (dict, list)):
            add_finding("UNM-51", line_of(clean, m.start(1)), extra="JSON-LD root must be an object or array.")

    # Absolute HTTPS URLs for canonical and social cards
    for m in META_TAG_RE.finditer(clean):
        attrs = {a.group(1).lower(): (a.group(2) if a.group(2) is not None else a.group(3)) for a in ATTR_RE.finditer(m.group(0))}
        key = (attrs.get("property") or attrs.get("name") or "").lower()
        content = attrs.get("content")
        if key in ABSOLUTE_URL_META and content and "{" not in content and not content.startswith("https://"):
            add_finding("UNM-52", line_of(clean, m.start()), extra=f"{key} = '{content[:60]}'.")
    for m in LINK_TAG_RE.finditer(clean):
        attrs = {a.group(1).lower(): (a.group(2) if a.group(2) is not None else a.group(3)) for a in ATTR_RE.finditer(m.group(0))}
        href = attrs.get("href")
        if (attrs.get("rel") or "").lower() == "canonical" and href and "{" not in href and not href.startswith("https://"):
            add_finding("UNM-52", line_of(clean, m.start()), extra=f"canonical = '{href[:60]}'.")

    # Full HTML document SEO & GEO checks (only on standalone <!doctype html> or <html> documents,
    # skipping print-only @page A4 templates)
    is_full_html = bool(re.search(r"<!doctype\s+html|<html\b", clean, re.I))
    is_print_sheet = bool(re.search(r"@page\s*\{\s*size\s*:\s*A4", clean, re.I))
    if is_full_html and not is_print_sheet:
        html_m = re.search(r"<html\b([^>]*)>", clean, re.I)
        if html_m and not re.search(r"\blang\s*=", html_m.group(1), re.I):
            add_finding("UNM-33", line_of(clean, html_m.start()))
        if not re.search(r"<main\b", clean, re.I):
            add_finding("UNM-34", 1)
        h1_matches = list(re.finditer(r"<h1\b", clean, re.I))
        if len(h1_matches) == 0:
            add_finding("UNM-35", 1, extra="No <h1> found in document.")
        elif len(h1_matches) > 1:
            add_finding("UNM-35", line_of(clean, h1_matches[1].start()), extra=f"Found {len(h1_matches)} <h1> elements.")
        if not (re.search(r"<title\b[^>]*>\S", clean, re.I) and re.search(r'<meta\b[^>]*name\s*=\s*["\']description["\']', clean, re.I)):
            add_finding("UNM-36", 1)
        if not re.search(r'<link\b[^>]*rel\s*=\s*["\']canonical["\']', clean, re.I):
            add_finding("UNM-37", 1)
        if not re.search(r'property\s*=\s*["\']og:image["\']', clean, re.I):
            add_finding("UNM-38", 1)
        if not re.search(r'type\s*=\s*["\']application/ld\+json["\']', clean, re.I):
            add_finding("UNM-39", 1)


def scan_file(path: Path, base: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], []
    lines = text.splitlines()
    waivers, used_waivers = parse_waivers(lines)
    rel_path = path.relative_to(base).as_posix() if base.is_dir() else path.name
    findings: List[Dict[str, object]] = []
    seen: Set[Tuple[str, int]] = set()

    def add_finding(rule_id: str, line_no: int, extra: str = "") -> None:
        if (None, rule_id) in waivers:
            used_waivers.add((None, rule_id))
            return
        if (line_no, rule_id) in waivers:
            used_waivers.add((line_no, rule_id))
            return
        if (rule_id, line_no) in seen:
            return
        seen.add((rule_id, line_no))
        meta = RULE_MAP[rule_id]
        msg = meta["desc"] + (f" ({extra})" if extra else "")
        findings.append({
            "rule": rule_id,
            "severity": meta["sev"],
            "category": meta["cat"],
            "file": rel_path,
            "line": line_no,
            "message": msg,
            "fix": meta["fix"],
        })

    suffix = path.suffix.lower()
    for style_line, css_block in extract_style_blocks(text, suffix):
        scan_css_block(css_block, style_line, add_finding)
    if suffix in MARKUP_EXTS:
        scan_markup(text, add_finding)
    scan_file_aggregates(strip_comments(text), suffix in MARKUP_EXTS, add_finding)

    # Compute unused waivers by declaration line
    declared_by_decl: Dict[Tuple[int, str], List[Tuple[Optional[int], str]]] = {}
    for key, decl_ln in waivers.items():
        declared_by_decl.setdefault((decl_ln, key[1]), []).append(key)
    unused: List[Dict[str, object]] = []
    for (decl_ln, rid), keys in sorted(declared_by_decl.items()):
        if not any(k in used_waivers for k in keys):
            unused.append({
                "rule": rid,
                "file": rel_path,
                "line": decl_ln,
                "message": f"Unused inline waiver for {rid}; remove stale suppression comment.",
            })
    return findings, unused


def scan_path(target_str: str) -> Dict[str, object]:
    target = Path(target_str).expanduser()
    if not target.exists():
        raise FileNotFoundError(f"Target path '{target_str}' does not exist. Pass an existing file or directory.")
    base = target.resolve() if target.is_dir() else target.resolve().parent
    files = collect_targets(target.resolve())
    all_findings: List[Dict[str, object]] = []
    all_unused: List[Dict[str, object]] = []
    for f in files:
        f_items, u_items = scan_file(f, base)
        all_findings.extend(f_items)
        all_unused.extend(u_items)

    all_findings.sort(key=lambda x: (SEV_RANK.get(str(x["severity"]), 9), str(x["file"]), int(x["line"])))
    counts = {s: sum(1 for x in all_findings if x["severity"] == s) for s in ("P0", "P1", "P2", "P3")}
    return {
        "target": str(target),
        "scanned_files": len(files),
        "counts": counts,
        "total_findings": len(all_findings),
        "findings": all_findings,
        "unused_ignores": all_unused,
    }


def to_sarif(result: Dict[str, object], execution_successful: bool = True) -> Dict[str, object]:
    sarif_rules = [{
        "id": r["id"],
        "name": r["id"].replace("-", ""),
        "shortDescription": {"text": r["desc"]},
        "help": {"text": r["fix"]},
        "defaultConfiguration": {"level": SARIF_LEVEL[r["sev"]]},
        "properties": {"category": r["cat"], "severity": r["sev"]},
    } for r in RULES]
    sarif_results = []
    for f in result.get("findings", []):
        sarif_results.append({
            "ruleId": f["rule"],
            "level": SARIF_LEVEL[str(f["severity"])],
            "message": {"text": f"{f['message']} Fix: {f['fix']}"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f["file"]},
                    "region": {"startLine": int(f["line"])},
                }
            }],
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "unmistakable-detect",
                    "version": VERSION,
                    "informationUri": "https://github.com/AntonioCardenas/unmistakable",
                    "rules": sarif_rules,
                }
            },
            "invocations": [{"executionSuccessful": execution_successful}],
            "results": sarif_results,
        }],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan frontend markup and CSS for AI-slop, sloppy-UI, a11y, CWV, and SEO/GEO issues."
    )
    parser.add_argument("target", nargs="?", default=".", help="File or directory to scan (default: .)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--sarif", action="store_true", help="Emit SARIF 2.1.0 log for GitHub Code Scanning")
    parser.add_argument("--list-rules", action="store_true", help=f"Print all {len(RULES)} UNM rules and exit")
    parser.add_argument("--fail-on", choices=["P0", "P1", "P2", "P3"], default="P3",
                        help="Exit 2 only when findings at or above this severity exist (default: P3, any finding)")
    parser.add_argument("--report-unused-ignores", action="store_true", help="Fail when inline waivers match nothing")
    parser.add_argument("--version", action="version", version=f"unmistakable-detect {VERSION}")
    args = parser.parse_args(argv)

    if args.list_rules:
        if args.json:
            print(json.dumps(RULES, indent=2))
        else:
            for r in RULES:
                print(f"{r['id']}  [{r['sev']}]  {r['cat']:<6}  {r['desc']}")
        return 0

    try:
        res = scan_path(args.target)
    except FileNotFoundError as exc:
        if args.sarif:
            print(json.dumps(to_sarif({"findings": []}, execution_successful=False), indent=2))
        elif args.json:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    threshold = SEV_RANK[args.fail_on]
    blocking = [f for f in res["findings"] if SEV_RANK[str(f["severity"])] <= threshold]  # type: ignore[union-attr]
    has_issues = bool(blocking) or (args.report_unused_ignores and bool(res["unused_ignores"]))
    if args.sarif:
        print(json.dumps(to_sarif(res, execution_successful=True), indent=2))
    elif args.json:
        print(json.dumps(res, indent=2))
    else:
        c = res["counts"]
        print(f"Unmistakable Scan: {res['scanned_files']} file(s) | "
              f"P0={c['P0']} P1={c['P1']} P2={c['P2']} P3={c['P3']}")  # type: ignore[index]
        for f in res["findings"]:  # type: ignore[union-attr]
            print(f"  [{f['severity']}] {f['rule']} {f['file']}:{f['line']} - {f['message']}")
            print(f"       Fix: {f['fix']}")
        if args.report_unused_ignores:
            for u in res["unused_ignores"]:  # type: ignore[union-attr]
                print(f"  [WARN] UNUSED-WAIVER {u['file']}:{u['line']} - {u['message']}")
        if not res["total_findings"]:
            print("  Clean: zero findings.")
        elif not has_issues:
            print(f"  Pass: zero findings at or above {args.fail_on}.")
    return 2 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main())
