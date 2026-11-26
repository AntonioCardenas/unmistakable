#!/usr/bin/env python3
"""Offline 18-gate production readiness, design-system, and SEO/GEO checker.

Inspects a repository offline to report which product, accessibility, token,
and search-engine foundations are in place, failing, or not applicable.
Never prints secret values when reporting credential leaks.

Exit codes:
  0 = all applicable gates pass (or single requested --id gate passes/N/A)
  1 = target directory does not exist
  2 = one or more applicable gates are failing
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect_slop

# Hand-authored source files above 1,000 lines become brittle to maintain and review.
MAX_SOURCE_LINES = 1000

# Skip large binary or generated files above 1.5 MB during offline repo walks.
MAX_READ_BYTES = 1_500_000

SKIP_DIRS = {
    ".git",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".astro",
    "node_modules",
    "dist",
    "build",
    "out",
    "coverage",
    "vendor",
    "__pycache__",
    "evals",
}

UI_CODE_EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
SOURCE_LINE_EXTS = UI_CODE_EXTS | {".ts", ".js", ".css", ".scss"}
ENV_SAMPLE_RE = re.compile(r"\.(?:example|sample|template|dist)$", re.I)

PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PRIVATE )?PRIVATE KEY-----")
TOKEN_FORMAT_RE = re.compile(
    r"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-(?:live|proj)-[A-Za-z0-9_-]{24,}|xox[baprs]-[A-Za-z0-9-]{20,})\b"
)
ENV_SECRET_LINE_RE = re.compile(
    r"^\s*(?!(?:NEXT_PUBLIC_|VITE_|PUBLIC_|NUXT_PUBLIC_))[A-Z0-9_]*(?:SECRET|PASSWORD|PASSWD|PRIVATE_KEY|API_KEY|ACCESS_TOKEN)[A-Z0-9_]*\s*=\s*(.+)$"
)
PLACEHOLDER_VAL_RE = re.compile(
    r"^(?:your[_-]|replace[_-]|changeme|example|xxx|test|dummy|<|\$\{|process\.env)", re.I
)

# Search-index and user-triggered retrieval agents. Blocking these removes a site from classic
# search results and from AI answer citations. Training-only crawlers (GPTBot, ClaudeBot,
# Google-Extended, Applebot-Extended, CCBot) are deliberately absent: opting out of training
# is a legitimate policy choice and does not remove search visibility.
SEARCH_RETRIEVAL_AGENTS = (
    "googlebot",
    "bingbot",
    "oai-searchbot",
    "chatgpt-user",
    "claude-searchbot",
    "claude-user",
    "perplexitybot",
    "perplexity-user",
    "applebot",
    "duckassistbot",
)
ROBOTS_PATHS = ("robots.txt", "public/robots.txt", "static/robots.txt", "src/robots.txt")


def walk_repo(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in SKIP_DIRS and (d == ".github" or not d.startswith("."))
        )
        for fname in sorted(filenames):
            if fname == ".DS_Store" or fname.endswith(".pyc"):
                continue
            p = here / fname
            files.append(p)
    return files


def safe_read(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size > MAX_READ_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def check_secrets(root: Path, files: Sequence[Path]) -> Tuple[str, str]:
    leaks: List[str] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        if f.name.startswith(".env") and not ENV_SAMPLE_RE.search(f.name):
            txt = safe_read(f) or ""
            for ln, line in enumerate(txt.splitlines(), 1):
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                m = ENV_SECRET_LINE_RE.match(s)
                if m:
                    val = m.group(1).strip().strip("\"'")
                    if val and not PLACEHOLDER_VAL_RE.search(val):
                        leaks.append(f"{rel}:{ln}")
                        break
            continue
        if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".woff2", ".ico"}:
            continue
        txt = safe_read(f)
        if not txt:
            continue
        for ln, line in enumerate(txt.splitlines(), 1):
            if PRIVATE_KEY_RE.search(line) or TOKEN_FORMAT_RE.search(line):
                leaks.append(f"{rel}:{ln}")
                break
    if leaks:
        return "failing", f"Potential credential leak at {', '.join(leaks[:4])} (value redacted; move to untracked env and rotate)."
    return "checked", "Zero tracked private keys or live secret tokens detected."


def parse_robots_groups(txt: str) -> List[Tuple[List[str], List[Tuple[str, str]]]]:
    """Parse robots.txt into (user_agents, [(directive, path)]) groups per RFC 9309."""
    groups: List[Tuple[List[str], List[Tuple[str, str]]]] = []
    agents: List[str] = []
    rules: List[Tuple[str, str]] = []
    last_was_agent = False
    for raw in txt.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, val = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not last_was_agent and (agents or rules):
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(val.lower())
            last_was_agent = True
        elif key in ("allow", "disallow"):
            rules.append((key, val))
            last_was_agent = False
        else:
            last_was_agent = False
    if agents:
        groups.append((agents, rules))
    return groups


def blocked_search_agents(robots_txt: str) -> List[str]:
    """Return search/retrieval agents fully blocked (Disallow: / with no Allow) by robots.txt."""
    groups = parse_robots_groups(robots_txt)

    def fully_blocked(rules: List[Tuple[str, str]]) -> bool:
        return ("disallow", "/") in rules and not any(k == "allow" and v for k, v in rules)

    blocked: List[str] = []
    for agent in SEARCH_RETRIEVAL_AGENTS:
        specific = [r for a, r in groups if agent in a]
        applicable = specific or [r for a, r in groups if "*" in a]
        if applicable and any(fully_blocked(r) for r in applicable):
            blocked.append(agent)
    return blocked


def evaluate_foundations(root_str: str) -> Dict[str, object]:
    root = Path(root_str).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Project root '{root_str}' is not an existing directory.")

    files = walk_repo(root)
    rel_map = {f.relative_to(root).as_posix(): f for f in files}
    ui_files = [
        f for rel, f in rel_map.items()
        if f.suffix.lower() in UI_CODE_EXTS and not rel.startswith("assets/")
    ]
    style_files = [
        f for rel, f in rel_map.items()
        if f.suffix.lower() in {".css", ".scss"} and not rel.startswith("assets/")
    ]
    is_web_app = len(ui_files) > 0

    items: Dict[str, Dict[str, str]] = {}

    def record(gate_id: str, status: str, detail: str, fix: str) -> None:
        items[gate_id] = {"status": status, "detail": detail, "fix": fix}

    # 1. secrets-out-of-repo
    sec_status, sec_detail = check_secrets(root, files)
    record("secrets-out-of-repo", sec_status, sec_detail, "Move secrets to untracked .env.local / host secret manager and rotate exposed keys.")

    ui_and_style_corpus = "\n".join((safe_read(f) or "") for f in (ui_files + style_files))

    # 2. design-tokens
    if not is_web_app and not style_files:
        record("design-tokens", "not_applicable", "No web UI or stylesheet files in repository.", "")
    else:
        defines_token = bool(re.search(r"--(?:color|bg|surface|text|primary|space|radius)-[a-z0-9-]+\s*:", ui_and_style_corpus))
        uses_token = bool(re.search(r"var\(\s*--(?:color|bg|surface|text|primary|space|radius)-", ui_and_style_corpus))
        has_tokens_json = any(rel.endswith(("tokens.json", "design.json")) for rel in rel_map)
        if (defines_token and uses_token) or has_tokens_json:
            record("design-tokens", "checked", "Semantic CSS custom properties defined and consumed via var().", "")
        else:
            record("design-tokens", "failing", "No semantic --color-* / --space-* custom properties defined and consumed.", "Create design/tokens.css or :root semantic tokens and reference them via var().")

    # 3. no-ai-slop-patterns
    if not is_web_app and not style_files:
        record("no-ai-slop-patterns", "not_applicable", "No web UI files to scan.", "")
    else:
        scan = detect_slop.scan_path(str(root))
        blocking = scan["counts"]["P0"] + scan["counts"]["P1"]
        if blocking == 0:
            record("no-ai-slop-patterns", "checked", f"Zero P0/P1 findings across {scan['scanned_files']} UI/style file(s).", "")
        else:
            record("no-ai-slop-patterns", "failing", f"{blocking} P0/P1 finding(s) detected by scripts/detect_slop.py.", "Run python3 scripts/detect_slop.py . and fix P0/P1 issues.")

    # 4. reduced-motion-guard
    has_motion = bool(re.search(r"@keyframes\b|\btransition\s*:(?!\s*none)|\banimation\s*:(?!\s*none)|\banimate-", ui_and_style_corpus))
    if not has_motion:
        record("reduced-motion-guard", "not_applicable", "No CSS animations or transitions present.", "")
    elif re.search(r"prefers-reduced-motion\s*:\s*reduce|\bmotion-reduce:", ui_and_style_corpus):
        record("reduced-motion-guard", "checked", "prefers-reduced-motion guard present.", "")
    else:
        record("reduced-motion-guard", "failing", "Animations/transitions present without prefers-reduced-motion guard.", "Add @media (prefers-reduced-motion: reduce) fallback rules.")

    # 5. semantic-landmarks
    if not is_web_app:
        record("semantic-landmarks", "not_applicable", "Not a web UI project.", "")
    elif re.search(r"<main\b", ui_and_style_corpus, re.I) and re.search(r"<h1\b", ui_and_style_corpus, re.I):
        record("semantic-landmarks", "checked", "<main> landmark and <h1> heading found.", "")
    else:
        record("semantic-landmarks", "failing", "Missing <main> landmark or primary <h1> in web templates.", "Wrap route content in <main> with a single descriptive <h1>.")

    # 6. not-found-route
    if not is_web_app:
        record("not-found-route", "not_applicable", "Not a web UI project.", "")
    else:
        has_404 = any(
            re.search(r"(?:^|/)(?:404\.(?:html|astro|tsx|jsx|vue|md)|not-found\.(?:tsx|jsx|js|ts)|\+error\.svelte|error\.vue)$", rel)
            for rel in rel_map
        ) or bool(re.search(r'path\s*=\s*["\']\*["\']', ui_and_style_corpus))
        record(
            "not-found-route",
            "checked" if has_404 else "failing",
            "Custom 404 / not-found route detected." if has_404 else "No custom 404 or not-found page found.",
            "Add the framework's native not-found page (app/not-found.tsx, src/pages/404.astro, +error.svelte, or 404.html).",
        )

    # 7. app-icons
    if not is_web_app:
        record("app-icons", "not_applicable", "Not a web UI project.", "")
    else:
        has_icons = any(
            re.search(r"(?:favicon\.|apple-touch-icon\.|icon\.(?:svg|png)|site\.webmanifest|manifest\.json)", rel, re.I)
            for rel in rel_map
        )
        record(
            "app-icons",
            "checked" if has_icons else "failing",
            "Favicon or app icon assets present." if has_icons else "Missing favicon and apple-touch-icon assets.",
            "Add favicon.svg and apple-touch-icon.png in public/ and link them in <head>.",
        )

    # 8. social-previews
    if not is_web_app:
        record("social-previews", "not_applicable", "Not a web UI project.", "")
    else:
        meta_corpus = ui_and_style_corpus + "\n" + "\n".join(
            (safe_read(f) or "") for rel, f in rel_map.items() if f.suffix.lower() in {".ts", ".js"} and ("layout" in rel or "config" in rel or "seo" in rel)
        )
        has_og = bool(re.search(r"og:image|openGraph\s*:|opengraph-image", meta_corpus)) or any("opengraph-image" in rel for rel in rel_map)
        record(
            "social-previews",
            "checked" if has_og else "failing",
            "OpenGraph social image configured." if has_og else "No og:image or openGraph.images metadata found.",
            "Configure a 1200x630 og:image and twitter:card=summary_large_image.",
        )

    # 9. canonical-and-meta
    if not is_web_app:
        record("canonical-and-meta", "not_applicable", "Not a web UI project.", "")
    else:
        has_meta = bool(
            re.search(r"<title\b|title\s*:", meta_corpus)
            and re.search(r'name\s*=\s*["\']description["\']|description\s*:', meta_corpus)
            and re.search(r'rel\s*=\s*["\']canonical["\']|alternates\s*:\s*\{[^}]*canonical', meta_corpus)
        )
        record(
            "canonical-and-meta",
            "checked" if has_meta else "failing",
            "Title, description, and canonical URL metadata found." if has_meta else "Missing <title>, meta description, or canonical URL.",
            "Add unique <title>, factual meta description, and canonical URL metadata.",
        )

    # 10. structured-data-jsonld
    if not is_web_app:
        record("structured-data-jsonld", "not_applicable", "Not a web UI project.", "")
    else:
        has_ld = bool(re.search(r"application/ld\+json|schema\.org", meta_corpus, re.I))
        record(
            "structured-data-jsonld",
            "checked" if has_ld else "failing",
            "Schema.org JSON-LD structured data present." if has_ld else "No application/ld+json structured data found.",
            "Embed validated <script type=\"application/ld+json\"> matching visible page entities.",
        )

    # 11. robots-and-sitemap
    if not is_web_app:
        record("robots-and-sitemap", "not_applicable", "Not a web UI project.", "")
    else:
        has_robots = any(re.search(r"(?:^|/)(?:robots\.(?:txt|ts|js))$", rel) for rel in rel_map)
        has_sitemap = any(re.search(r"(?:^|/)(?:sitemap\.(?:xml|ts|js)|sitemap-index\.xml)$", rel) for rel in rel_map)
        ok_rs = has_robots and has_sitemap
        record(
            "robots-and-sitemap",
            "checked" if ok_rs else "failing",
            "robots.txt and sitemap configured." if ok_rs else "Missing robots.txt or sitemap.xml route.",
            "Add public/robots.txt (referencing Sitemap) and sitemap.xml.",
        )

    # 12. llms-geo-index
    has_llms = any(rel in {"llms.txt", "public/llms.txt", "static/llms.txt", "src/pages/llms.txt.ts"} for rel in rel_map)
    record(
        "llms-geo-index",
        "checked" if has_llms else "failing",
        "llms.txt AI crawler index present." if has_llms else "No llms.txt found at root or public/llms.txt.",
        "Create llms.txt summarizing canonical pages, capabilities, and docs for AI answer engines.",
    )

    # 13. legal-routes
    if not is_web_app:
        record("legal-routes", "not_applicable", "Documentation or skill package without end-user web auth.", "")
    else:
        has_privacy = any("privacy" in rel.lower() for rel in rel_map)
        has_terms = any(("terms" in rel.lower() or "tos" in rel.lower()) for rel in rel_map)
        record(
            "legal-routes",
            "checked" if (has_privacy and has_terms) else "failing",
            "Privacy and terms routes present." if (has_privacy and has_terms) else "Missing /privacy or /terms route.",
            "Ask the user before drafting placeholder /privacy and /terms pages for legal review.",
        )

    # 14. readme-commands
    readme_file = rel_map.get("README.md") or rel_map.get("readme.md")
    pkg_file = rel_map.get("package.json")
    if not readme_file:
        record("readme-commands", "failing", "No README.md at project root.", "Add README.md with installation and verification commands.")
    else:
        rtxt = safe_read(readme_file) or ""
        has_code = "```" in rtxt
        missing_scripts: List[str] = []
        if pkg_file:
            try:
                pkg = json.loads(safe_read(pkg_file) or "{}")
                scripts = set((pkg.get("scripts") or {}).keys())
                for m in re.finditer(r"\b(?:npm|pnpm|yarn|bun)\s+run\s+([a-zA-Z0-9:_-]+)", rtxt):
                    if m.group(1) not in scripts:
                        missing_scripts.append(m.group(1))
            except ValueError:
                pass
        if has_code and not missing_scripts:
            record("readme-commands", "checked", "README.md includes runnable commands matching package scripts.", "")
        else:
            detail = f"README references missing script(s): {', '.join(missing_scripts)}" if missing_scripts else "README.md lacks runnable command blocks."
            record("readme-commands", "failing", detail, "Document working install/test commands in README.md.")

    # 15. ci-verification
    workflow_files = [f for rel, f in rel_map.items() if rel.startswith(".github/workflows/") and f.suffix.lower() in {".yml", ".yaml"}]
    ci_runs_checks = False
    for wf in workflow_files:
        wtxt = safe_read(wf) or ""
        if re.search(r"\b(?:pytest|unittest|vitest|jest|playwright|npm\s+test|pnpm\s+test|test_unmistakable|detect_slop|validate_skill)\b", wtxt):
            ci_runs_checks = True
            break
    record(
        "ci-verification",
        "checked" if ci_runs_checks else "failing",
        "CI workflow runs automated tests/checks." if ci_runs_checks else "No CI workflow running automated tests found.",
        "Add .github/workflows/ci.yml running unit tests and scripts/detect_slop.py on push and pull_request.",
    )

    # 16. no-giant-files
    giant: List[str] = []
    for rel, f in rel_map.items():
        if f.suffix.lower() not in SOURCE_LINE_EXTS:
            continue
        if rel.endswith((".min.js", ".min.css", "lock.json")):
            continue
        txt = safe_read(f)
        if txt and len(txt.splitlines()) > MAX_SOURCE_LINES:
            giant.append(f"{rel} ({len(txt.splitlines())} lines)")
    record(
        "no-giant-files",
        "failing" if giant else "checked",
        f"Oversized source file(s): {', '.join(giant[:3])}" if giant else f"All source files <= {MAX_SOURCE_LINES} lines.",
        "Split files exceeding 1,000 lines along clean component or module seams.",
    )

    # 17. ai-search-crawlers
    robots_rel = next((p for p in ROBOTS_PATHS if p in rel_map), None)
    if not is_web_app or not robots_rel:
        record("ai-search-crawlers", "not_applicable",
               "No static robots.txt to inspect (dynamic robots routes need a manual check)." if is_web_app else "Not a web UI project.", "")
    else:
        blocked = blocked_search_agents(safe_read(rel_map[robots_rel]) or "")
        record(
            "ai-search-crawlers",
            "failing" if blocked else "checked",
            f"{robots_rel} blocks search/answer agents: {', '.join(blocked)}." if blocked
            else f"{robots_rel} allows search and AI answer retrieval agents.",
            "Allow Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, and PerplexityBot; "
            "opt out of training crawlers (GPTBot, ClaudeBot, Google-Extended, CCBot) separately. Check CDN/WAF bot rules too.",
        )

    # 18. icon-system
    if not is_web_app:
        record("icon-system", "not_applicable", "Not a web UI project.", "")
    else:
        icon_sources: Dict[str, str] = {}
        for rel, f in rel_map.items():
            if f.suffix.lower() in UI_CODE_EXTS | {".ts", ".js", ".mjs"}:
                for _, family, _ in detect_slop.icon_imports(safe_read(f) or ""):
                    icon_sources.setdefault(family, rel)
        if pkg_file:
            try:
                pkg_data = json.loads(safe_read(pkg_file) or "{}")
                for dep in {**(pkg_data.get("dependencies") or {}), **(pkg_data.get("devDependencies") or {})}:
                    family = detect_slop.icon_family(dep)
                    if family:
                        icon_sources.setdefault(family, "package.json")
            except ValueError:
                pass
        if any(f.startswith("react-icons/") for f in icon_sources):
            icon_sources.pop("react-icons", None)
        if len(icon_sources) > 1:
            listed = ", ".join(f"{fam} ({src})" for fam, src in sorted(icon_sources.items()))
            record("icon-system", "failing", f"{len(icon_sources)} icon families in use: {listed}.",
                   "Name one icon family in DESIGN.md (Graphic Language), migrate the rest, and remove unused icon packages.")
        else:
            only = next(iter(icon_sources), None)
            record("icon-system", "checked",
                   f"One icon family ({only})." if only else "No icon library; inline SVG only.", "")

    failing_ids = [k for k, v in items.items() if v["status"] == "failing"]
    checked_ids = [k for k, v in items.items() if v["status"] == "checked"]
    na_ids = [k for k, v in items.items() if v["status"] == "not_applicable"]
    return {
        "root": str(root),
        "summary": {
            "checked": len(checked_ids),
            "failing": len(failing_ids),
            "not_applicable": len(na_ids),
            "next_up": failing_ids[0] if failing_ids else None,
        },
        "items": items,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check 18 production, design-system, and SEO/GEO foundations.")
    parser.add_argument("root", nargs="?", default=".", help="Project root directory (default: .)")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    parser.add_argument("--id", dest="gate_id", help="Check a single foundation gate ID")
    args = parser.parse_args(argv)

    try:
        report = evaluate_foundations(args.root)
    except FileNotFoundError as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.gate_id:
        item = report["items"].get(args.gate_id)
        if not item:
            avail = ", ".join(report["items"].keys())
            msg = f"Unknown gate '{args.gate_id}'. Available gates: {avail}"
            print(json.dumps({"error": msg}) if args.json else f"ERROR: {msg}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps({"id": args.gate_id, **item}, indent=2))
        else:
            print(f"{args.gate_id}: {item['status']} - {item['detail']}")
            if item["status"] == "failing":
                print(f"  Fix: {item['fix']}")
        return 2 if item["status"] == "failing" else 0

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        s = report["summary"]
        print(f"Foundations: {s['checked']} checked, {s['failing']} failing, {s['not_applicable']} N/A")
        if s["next_up"]:
            nxt = report["items"][s["next_up"]]
            print(f"Next up: {s['next_up']} - {nxt['detail']}")
            print(f"  Fix: {nxt['fix']}")
        symbols = {"checked": "[PASS]", "failing": "[FAIL]", "not_applicable": "[N/A ]"}
        for gid, val in report["items"].items():
            print(f"  {symbols[val['status']]} {gid:<24} {val['detail']}")
    return 2 if report["summary"]["failing"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
