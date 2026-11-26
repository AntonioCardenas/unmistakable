# Security Policy

## Scope & Zero-Telemetry Guarantee

Unmistakable executes 100% locally:
- Bundled scripts (`scripts/detect_slop.py`, `scripts/check_foundations.py`, `scripts/render_brand_book.py`) use Python 3.8+ standard library modules only.
- No telemetry, analytics, or project source files are transmitted over the network.
- `scripts/check_foundations.py` redacts detected secret values and reports only `file:line` coordinates.

## Reporting a Vulnerability

Please report security issues privately via GitHub Security Advisories on the repository rather than opening a public issue containing exploit details.
