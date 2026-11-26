#!/usr/bin/env python3
"""Automated verification suite for the Unmistakable skill and offline CLI tools."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_foundations  # noqa: E402
import detect_slop  # noqa: E402
import render_brand_book  # noqa: E402


SLOP_HTML_FIXTURE = """<!doctype html>
<html>
<head>
  <style>
    .hero-title {
      background: linear-gradient(90deg, #8b5cf6, #06b6d4);
      -webkit-background-clip: text;
      color: transparent;
      transition: all 0.3s ease-in;
    }
    input {
      font-size: 13px;
      outline: none;
    }
    .micro {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.2em;
    }
  </style>
</head>
<body>
  <div class="card">
    <span class="eyebrow">NEW RELEASE</span>
    <h2>01. Unleash the power <br><em>reimagined</em></h2>
    <div class="card" onClick="openModal()">
      <img src="/hero.jpg" loading="lazy" />
      <p>Lorem ipsum — seamlessly elevate your workflow.</p>
      <a href="/docs">Click here</a>
      <button><svg viewBox="0 0 10 10"></svg></button>
      <input type="text" placeholder="Email" />
    </div>
  </div>
</body>
</html>
"""

CLEAN_PRODUCTION_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Helvetia Mill | Precision Single-Dose Burr Grinder</title>
  <meta name="description" content="Helvetia Mill machines 83mm flat titanium burrs to 2-micron concentricity for zero-retention espresso extraction." />
  <link rel="canonical" href="https://helvetiamill.example/grinder" />
  <meta property="og:title" content="Helvetia Mill | Precision Single-Dose Burr Grinder" />
  <meta property="og:image" content="https://helvetiamill.example/og-grinder-1200x630.png" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Helvetia Mill 83",
    "description": "Single-dose 83mm flat-burr espresso grinder."
  }
  </script>
  <style>
    :root {
      --color-bg: #0e1116;
      --color-surface: #171b22;
      --color-text: #f4f2ec;
      --color-text-muted: #b8b4a8;
      --color-border: #2a303c;
      --color-primary: #ff4f1f;
      --text-heading: 1.75rem;
      --text-body: 1rem;
      --text-sm: 0.875rem;
    }
    body {
      background: var(--color-bg);
      color: var(--color-text);
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      font-size: var(--text-body);
    }
    :focus-visible {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }
    input {
      font-size: 1rem;
    }
    .cta {
      background: var(--color-primary);
      color: var(--color-bg);
      transition: transform 160ms cubic-bezier(0.22, 1, 0.36, 1), opacity 160ms cubic-bezier(0.22, 1, 0.36, 1);
    }
    @media (prefers-reduced-motion: reduce) {
      .cta { transition-duration: 0.01ms; }
    }
  </style>
</head>
<body>
  <header>
    <nav aria-label="Primary"><a href="/specs">Read burr tolerance specifications</a></nav>
  </header>
  <main id="main-content">
    <h1>Zero-retention 83mm flat burrs machined to two microns</h1>
    <img src="/grinder-hero.webp" alt="Helvetia Mill 83 anodized obsidian grinder on steel bench" width="1440" height="900" fetchpriority="high" />
    <section aria-labelledby="spec-heading">
      <h2 id="spec-heading">Measured extraction consistency</h2>
      <p>Each burr carrier is line-bored in one clamping setup so particle distribution stays bimodal across espresso and filter settings.</p>
      <label for="serial-input">Register serial number</label>
      <input id="serial-input" type="text" />
      <button type="button" class="cta">Reserve batch allocation</button>
    </section>
  </main>
</body>
</html>
"""


class UnmistakableSkillTests(unittest.TestCase):
    def test_detect_slop_catches_slop_a11y_cwv_and_seo_defects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "slop.html"
            bad.write_text(SLOP_HTML_FIXTURE, encoding="utf-8")
            res = detect_slop.scan_path(str(bad))
            triggered = {f["rule"] for f in res["findings"]}
            expected_subset = {
                "UNM-01",  # eyebrow
                "UNM-02",  # 01. heading prefix
                "UNM-03",  # background-clip: text
                "UNM-04",  # nested card
                "UNM-07",  # purple-to-cyan gradient
                "UNM-09",  # filler word
                "UNM-10",  # <br><em> split
                "UNM-11",  # em-dash
                "UNM-12",  # lorem ipsum
                "UNM-15",  # <12px micro text
                "UNM-16",  # <16px input
                "UNM-18",  # transition: all
                "UNM-19",  # ease-in
                "UNM-20",  # missing prefers-reduced-motion
                "UNM-22",  # div onClick
                "UNM-23",  # img missing alt
                "UNM-24",  # img missing width/height
                "UNM-25",  # lazy hero img
                "UNM-26",  # outline: none without :focus-visible
                "UNM-28",  # icon-only button without aria-label
                "UNM-29",  # input without label
                "UNM-33",  # missing html lang
                "UNM-34",  # missing main
                "UNM-35",  # missing h1
                "UNM-36",  # missing title/description
                "UNM-37",  # missing canonical
                "UNM-38",  # missing og:image
                "UNM-39",  # missing ld+json
                "UNM-40",  # "Click here" anchor
            }
            self.assertTrue(
                expected_subset.issubset(triggered),
                f"Missing expected rules: {sorted(expected_subset - triggered)}",
            )

    def test_detect_slop_passes_clean_production_html_and_emits_valid_sarif(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "index.html"
            good.write_text(CLEAN_PRODUCTION_HTML, encoding="utf-8")
            res = detect_slop.scan_path(str(good))
            self.assertEqual(res["total_findings"], 0, f"Unexpected findings: {res['findings']}")

            sarif = detect_slop.to_sarif(res)
            self.assertEqual(sarif["version"], "2.1.0")
            self.assertEqual(len(sarif["runs"][0]["tool"]["driver"]["rules"]), len(detect_slop.RULES))
            self.assertEqual(len(detect_slop.RULES), 53)
            self.assertEqual([r["id"] for r in detect_slop.RULES], [f"UNM-{i:02d}" for i in range(1, 54)])
            self.assertTrue(sarif["runs"][0]["invocations"][0]["executionSuccessful"])
            self.assertEqual(sarif["runs"][0]["results"], [])

    def test_before_after_fixtures(self) -> None:
        slop = detect_slop.scan_path(str(FIXTURES / "slop-landing.html"))
        triggered = {f["rule"] for f in slop["findings"]}
        visual_and_sloppy = {
            "UNM-06", "UNM-07", "UNM-41", "UNM-42", "UNM-43", "UNM-44", "UNM-45",
            "UNM-46", "UNM-47", "UNM-48", "UNM-49", "UNM-50", "UNM-53",
        }
        self.assertTrue(visual_and_sloppy.issubset(triggered), f"Missing: {sorted(visual_and_sloppy - triggered)}")
        self.assertGreaterEqual(len(triggered), 35)

        clean = detect_slop.scan_path(str(FIXTURES / "unmistakable-landing.html"))
        self.assertEqual(clean["total_findings"], 0, f"Unexpected findings: {clean['findings']}")

    def test_light_and_depth_rules_avoid_false_positives(self) -> None:
        legit_css = """
        :root { --shadow-overlay: 0 1px 2px oklch(0 0 0 / 0.06), 0 8px 24px oklch(0 0 0 / 0.08); }
        .scrim { background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent); }
        .mask { mask-image: linear-gradient(90deg, #ff0000, #0000ff); }
        .heat { background: linear-gradient(90deg, var(--heat-0), var(--heat-1)); }
        .ring:focus-visible { box-shadow: 0 0 0 3px #6d28d9; }
        .menu { box-shadow: var(--shadow-overlay); border-radius: 6px; }
        .dialog::backdrop { backdrop-filter: blur(4px); }
        .modal-overlay { backdrop-filter: blur(6px); }
        .spinner { animation: spin 800ms linear infinite; }
        .skeleton { animation: shimmer 1.2s ease-in-out infinite; }
        .pill { border-radius: 9999px; }
        .avatar { border-radius: 50%; }
        .card { border-radius: 12px; padding: 16px 24px; margin-block: 2px; }
        @media (prefers-reduced-motion: reduce) { .spinner, .skeleton { animation: none; } }
        """
        flagged = self._scan_text("legit.css", legit_css)
        noisy = flagged & {"UNM-06", "UNM-07", "UNM-41", "UNM-43", "UNM-44", "UNM-45", "UNM-46", "UNM-47", "UNM-48", "UNM-49"}
        self.assertEqual(noisy, set(), f"False positives on legitimate patterns: {sorted(noisy)}")

    def test_light_and_depth_rules_catch_css_slop(self) -> None:
        slop_css = """
        .a { background: linear-gradient(135deg, oklch(0.62 0.25 293), oklch(0.7 0.15 230)); }
        .b { background-image: radial-gradient(circle, #ff7a18, #af002d); }
        .c { box-shadow: 0 12px 32px hsl(262 83% 58% / 0.45); }
        .d { box-shadow: 0 1px 2px #0002, 0 4px 8px #0002, 0 16px 32px #0002; }
        .e { text-shadow: 0 0 12px #ffffff; }
        .f { -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px); background: rgb(255 255 255 / 0.1); }
        .g { filter: blur(4rem); }
        .h { animation: glow-pulse 3s ease-in-out infinite; }
        .i { z-index: 2147483647; }
        """
        flagged = self._scan_text("slop.css", slop_css)
        for rule in ("UNM-07", "UNM-41", "UNM-43", "UNM-44", "UNM-45", "UNM-46", "UNM-47", "UNM-49"):
            self.assertIn(rule, flagged)

    def test_tailwind_slop_detection(self) -> None:
        jsx = (
            'export function Hero() {\n'
            '  return (\n'
            '    <section className="relative">\n'
            '      <div className="absolute -top-40 size-96 rounded-full bg-purple-500 blur-3xl animate-blob" />\n'
            '      <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl p-[13px] mt-[7px] gap-[19px]">\n'
            '        <h1 className="bg-gradient-to-r from-purple-500 to-cyan-400 bg-clip-text text-transparent">Ship faster</h1>\n'
            '        <button className="rounded-lg bg-gradient-to-r from-orange-500 to-rose-500 shadow-lg shadow-indigo-500/50">Start</button>\n'
            '        <span className="rounded-md rounded-xl rounded-sm z-[9999] animate-bounce">Loved by 50,000+ developers</span>\n'
            '        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" />\n'
            '      </div>\n'
            '    </section>\n'
            '  );\n'
            '}\n'
        )
        flagged = self._scan_text("Hero.tsx", jsx)
        for rule in ("UNM-03", "UNM-07", "UNM-41", "UNM-42", "UNM-43", "UNM-44", "UNM-45", "UNM-46", "UNM-47", "UNM-48", "UNM-49"):
            self.assertIn(rule, flagged)
        overlay_hits = [f for f in self._findings if f["rule"] == "UNM-45" and f["line"] == 9]
        self.assertEqual(overlay_hits, [], "Full-screen overlay scrim should not count as glassmorphism")

    def test_structured_data_and_link_rules(self) -> None:
        page = """<!doctype html>
<html lang="en"><head>
<title>Broken metadata example page for tests</title>
<meta name="description" content="Fixture">
<link rel="canonical" href="/pricing">
<meta property="og:image" content="/og.png">
<script type="application/ld+json">{ "@type": "Product", "name": "X", }</script>
<script type="application/ld+json">{ "@type": "Organization", "name": "Y" }</script>
<script type="application/ld+json">{JSON.stringify(schema)}</script>
</head><body><main><h1>Pricing</h1><a href="#">Docs</a><a href="javascript:void(0)">Open</a></main></body></html>
"""
        flagged = self._scan_text("page.html", page)
        self.assertIn("UNM-51", flagged)
        self.assertIn("UNM-52", flagged)
        self.assertIn("UNM-53", flagged)
        jsonld_lines = sorted(f["line"] for f in self._findings if f["rule"] == "UNM-51")
        self.assertEqual(jsonld_lines, [7, 8], "Invalid JSON and missing @context flagged; template expression skipped")

    def test_fail_on_threshold_controls_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p3_only = Path(tmp) / "spacing.css"
            p3_only.write_text(".a { padding: 13px 7px; margin: 5px; }\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(detect_slop.main([str(p3_only)]), 2)
                self.assertEqual(detect_slop.main([str(p3_only), "--fail-on", "P1"]), 0)
                self.assertEqual(detect_slop.main([str(FIXTURES / "slop-landing.html"), "--fail-on", "P0"]), 2)

    def test_ai_search_crawler_gate(self) -> None:
        blocked = "User-agent: *\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /\n"
        self.assertNotIn("googlebot", check_foundations.blocked_search_agents(blocked))
        self.assertIn("oai-searchbot", check_foundations.blocked_search_agents(blocked))
        self.assertIn("perplexitybot", check_foundations.blocked_search_agents(blocked))

        training_opt_out = (
            "User-agent: GPTBot\nDisallow: /\n\nUser-agent: ClaudeBot\nDisallow: /\n\n"
            "User-agent: Google-Extended\nDisallow: /\n\nUser-agent: *\nAllow: /\n"
        )
        self.assertEqual(check_foundations.blocked_search_agents(training_opt_out), [])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "public").mkdir()
            (root / "index.html").write_text("<main><h1>x</h1></main>", encoding="utf-8")
            (root / "public" / "robots.txt").write_text("User-agent: OAI-SearchBot\nDisallow: /\n", encoding="utf-8")
            gate = check_foundations.evaluate_foundations(str(root))["items"]["ai-search-crawlers"]
            self.assertEqual(gate["status"], "failing")
            self.assertIn("oai-searchbot", gate["detail"])

    _findings: list = []

    def _scan_text(self, name: str, content: str) -> set:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / name
            target.write_text(content, encoding="utf-8")
            res = detect_slop.scan_path(str(target))
        self._findings = res["findings"]
        return {f["rule"] for f in res["findings"]}

    def test_inline_waivers_and_unused_waiver_reporting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "fragment.jsx"
            page.write_text(
                'export function Card() {\n'
                '  return (\n'
                '    <div>\n'
                '      {/* unmistakable-disable UNM-01: legacy migration */}\n'
                '      <span className="eyebrow">Legacy</span>\n'
                '      {/* unmistakable-disable UNM-08: stale waiver */}\n'
                '      <h2> Direct benefit heading </h2>\n'
                '    </div>\n'
                '  );\n'
                '}\n',
                encoding="utf-8",
            )
            res = detect_slop.scan_path(str(page))
            self.assertEqual(res["total_findings"], 0)
            self.assertEqual(len(res["unused_ignores"]), 1)
            self.assertEqual(res["unused_ignores"][0]["rule"], "UNM-08")

    def test_check_foundations_self_repo_and_secret_redaction(self) -> None:
        self_report = check_foundations.evaluate_foundations(str(REPO_ROOT))
        self.assertEqual(
            self_report["summary"]["failing"],
            0,
            f"Self foundations failed: {self_report['items']}",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_secret = "ghp_" + ("A1b2C3d4E5" * 4)
            (root / ".env").write_text(f"API_SECRET={fake_secret}\n", encoding="utf-8")
            rep = check_foundations.evaluate_foundations(str(root))
            sec = rep["items"]["secrets-out-of-repo"]
            self.assertEqual(sec["status"], "failing")
            self.assertNotIn(fake_secret, json.dumps(rep), "Secret value must never appear in report output!")

    def test_render_brand_book_rejects_unreplaced_tokens_and_renders_single_page_pdf(self) -> None:
        raw_template = REPO_ROOT / "assets" / "brand-book-a4-template.html"
        browser = render_brand_book.find_browser()
        with tempfile.TemporaryDirectory() as tmp:
            out_pdf = Path(tmp) / "out.pdf"
            code, msg = render_brand_book.render_pdf(raw_template, out_pdf, browser or "echo")
            self.assertEqual(code, 1)
            self.assertIn("unreplaced template token", msg)

            if browser:
                template_txt = raw_template.read_text(encoding="utf-8")
                replacements = {
                    "{{BRAND_NAME}}": "Unmistakable",
                    "{{GOOGLE_FONTS_QUERY}}": "Plus+Jakarta+Sans:wght@400;700;800&family=JetBrains+Mono:wght@500",
                    "{{PRIMARY_HEX}}": "#FF4F1F",
                    "{{SECONDARY_HEX}}": "#0E1116",
                    "{{TERTIARY_HEX}}": "#D9D4C7",
                    "{{BG_HEX}}": "#0E1116",
                    "{{SURFACE_HEX}}": "#161B22",
                    "{{BORDER_HEX}}": "#2A313C",
                    "{{TEXT_HEX}}": "#F4F2EC",
                    "{{MUTED_HEX}}": "#A9A59B",
                    "{{DISPLAY_FONT_NAME}}": "Plus Jakarta Sans",
                    "{{BODY_FONT_NAME}}": "Plus Jakarta Sans",
                    "{{MONO_FONT_NAME}}": "JetBrains Mono",
                    "{{LOGO_SVG}}": '<svg width="28" height="28" viewBox="0 0 28 28"><rect width="28" height="28" rx="4" fill="#FF4F1F"/></svg>',
                    "{{LOGO_SVG_SMALL}}": '<svg width="18" height="18" viewBox="0 0 28 28"><rect width="28" height="28" rx="4" fill="#FF4F1F"/></svg>',
                    "{{TAGLINE}}": "Production frontend systems without AI slop",
                    "{{SOURCE_LABEL}}": "Verified Local Tokens",
                    "{{PRIMARY_USAGE}}": "Primary actions, focus rings, key callouts",
                    "{{SECONDARY_USAGE}}": "Obsidian structural canvas",
                    "{{TERTIARY_USAGE}}": "Warm bone paper contrast fields",
                    "{{DISPLAY_SAMPLE_LINE_1}}": "Committed form.",
                    "{{DISPLAY_SAMPLE_LINE_2}}": "Zero slop.",
                    "{{TYPOGRAPHY_DESCRIPTION}}": "Two-family pairing with 3 body steps and tabular numerals.",
                    "{{PRINCIPLE_1_TITLE}}": "Mode honesty",
                    "{{PRINCIPLE_1_BODY}}": "Match the opening screen to Persuade, Operate, Read, or Experience.",
                    "{{PRINCIPLE_2_TITLE}}": "Token authority",
                    "{{PRINCIPLE_2_BODY}}": "Semantic custom properties govern every surface and state.",
                    "{{PRINCIPLE_3_TITLE}}": "Dual discovery",
                    "{{PRINCIPLE_3_BODY}}": "Semantic landmarks, JSON-LD, and llms.txt ship together.",
                    "{{LOCKUP_PART_1}}": "UNMIS",
                    "{{LOCKUP_PART_2}}": "TAKABLE",
                }
                for k, v in replacements.items():
                    template_txt = template_txt.replace(k, v)
                filled_html = Path(tmp) / "brand-book-a4.html"
                filled_html.write_text(template_txt, encoding="utf-8")
                rc, rmsg = render_brand_book.render_pdf(filled_html, out_pdf, browser)
                self.assertEqual(rc, 0, rmsg)
                self.assertTrue(out_pdf.is_file() and out_pdf.stat().st_size > 1000)

    def test_skill_structure_conforms_to_skill_creator_plus_rules(self) -> None:
        skill_md = REPO_ROOT / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertEqual(lines[0], "---")
        end_fm = lines.index("---", 1)
        body_lines = lines[end_fm + 1:]
        self.assertLess(len(body_lines), 500, "ST1: SKILL.md body must stay under 500 lines")

        em_dash = chr(0x2014)
        for md_file in [skill_md, *sorted((REPO_ROOT / "references").glob("*.md"))]:
            content = md_file.read_text(encoding="utf-8")
            self.assertNotIn(em_dash, content, f"Em-dash found in {md_file.name}")
            if md_file != skill_md and len(content.splitlines()) > 100:
                top_50 = "\n".join(content.splitlines()[:50])
                self.assertIn("## Contents", top_50, f"ST5: {md_file.name} > 100 lines must open with ## Contents")


if __name__ == "__main__":
    unittest.main(verbosity=2)
