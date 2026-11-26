#!/usr/bin/env python3
"""Render a self-contained A4 Brand Book HTML file to a print-ready 1-page PDF.

Locates headless Google Chrome, Chromium, Brave, or Microsoft Edge across macOS,
Linux, and Windows, renders the HTML with exact A4 print colors and zero browser
headers/footers, and verifies that the output PDF fits onto a single page.

Exit codes:
  0 = PDF rendered and verified as 1 page
  1 = missing input HTML, unreplaced {{TOKEN}} placeholder, or no Chromium browser found
  2 = PDF rendered, but content overflowed onto more than 1 page
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

# 30 seconds covers cold browser startup plus Google Fonts fetch on slow links.
BROWSER_TIMEOUT_SECONDS = 30

# Target page count for a single-sheet A4 Brand Book poster.
EXPECTED_PAGES = 1

PLACEHOLDER_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
PDF_PAGE_RE = re.compile(rb"/Type\s*/Page\b(?!s)")

CANDIDATE_BROWSERS: List[str] = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser(explicit: Optional[str] = None) -> Optional[str]:
    if explicit:
        resolved = shutil.which(explicit) or (explicit if Path(explicit).is_file() else None)
        return resolved
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin:
        resolved = shutil.which(env_bin) or (env_bin if Path(env_bin).is_file() else None)
        if resolved:
            return resolved
    for candidate in CANDIDATE_BROWSERS:
        if os.path.isabs(candidate):
            if Path(candidate).is_file():
                return candidate
        else:
            found = shutil.which(candidate)
            if found:
                return found
    return None


def count_pdf_pages(pdf_bytes: bytes) -> int:
    return len(PDF_PAGE_RE.findall(pdf_bytes))


def render_pdf(html_path: Path, pdf_path: Path, browser_bin: str) -> Tuple[int, str]:
    html_text = html_path.read_text(encoding="utf-8", errors="replace")
    uncommented_html = re.sub(r"<!--.*?-->", "", html_text, flags=re.S)
    leftover = sorted(set(PLACEHOLDER_TOKEN_RE.findall(uncommented_html)))
    if leftover:
        return 1, (
            f"Input HTML still contains unreplaced template token(s): {', '.join(leftover[:6])}. "
            "Replace every {{TOKEN}} or remove unused blocks before rendering."
        )

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    file_uri = html_path.resolve().as_uri()
    cmd = [
        browser_bin,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        file_uri,
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=BROWSER_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 1, f"Browser timed out after {BROWSER_TIMEOUT_SECONDS}s while rendering '{html_path}'."
    except OSError as exc:
        return 1, f"Failed to execute browser '{browser_bin}': {exc}"

    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        return 1, f"Browser exited with code {proc.returncode} and wrote no PDF. Details: {err[:240]}"

    data = pdf_path.read_bytes()
    if not data.startswith(b"%PDF-"):
        return 1, f"Output '{pdf_path}' is not a valid PDF header."

    pages = count_pdf_pages(data)
    if pages > EXPECTED_PAGES:
        return 2, (
            f"Rendered '{pdf_path}' ({len(data):,} bytes), but it spanned {pages} pages instead of {EXPECTED_PAGES}. "
            "Tighten .page vertical gaps or omit an optional block in brand-book-a4.html and re-render."
        )
    return 0, f"Rendered single-page A4 PDF '{pdf_path}' ({len(data):,} bytes, {max(pages, 1)} page)."


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Render an A4 Brand Book HTML sheet to a 1-page PDF.")
    parser.add_argument("input_html", help="Path to brand-book-a4.html")
    parser.add_argument("output_pdf", nargs="?", help="Output PDF path (defaults to <input>.pdf)")
    parser.add_argument("--browser", help="Explicit path to Chrome, Chromium, or Edge binary")
    args = parser.parse_args(argv)

    html_path = Path(args.input_html).expanduser()
    if not html_path.is_file():
        print(f"ERROR: HTML file not found: '{html_path}'. Generate brand-book-a4.html first.", file=sys.stderr)
        return 1

    pdf_path = Path(args.output_pdf).expanduser() if args.output_pdf else html_path.with_suffix(".pdf")
    browser = find_browser(args.browser)
    if not browser:
        print(
            "ERROR: No Chromium-based browser (Chrome, Chromium, Brave, or Edge) found. "
            "Install Chrome/Chromium or pass --browser /path/to/browser.",
            file=sys.stderr,
        )
        return 1

    code, msg = render_pdf(html_path, pdf_path, browser)
    stream = sys.stdout if code == 0 else sys.stderr
    print(msg, file=stream)
    return code


if __name__ == "__main__":
    sys.exit(main())
