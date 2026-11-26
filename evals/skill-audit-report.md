# Skill Audit: unmistakable

Validator (`robonuggets/skill-creator-plus/scripts/validate_skill.py --ban-em-dash`): **0 errors, 0 warnings, 0 notes** (last run on v1.0.0; v1.1.0 structure rules re-verified by `evals/test_unmistakable.py`).
Checklist (`robonuggets/skill-creator-plus/references/audit-checklist.md`): **36 pass, 0 fail, 3 not applicable**.

## Rule-by-Rule Verification

| Rule | Result | Evidence | Proposed change |
|---|---|---|---|
| HK1 Hook enforcement | N/A | Portable frontmatter (`claude.ai` / Antigravity / Cursor / Claude Code compatible) intentionally omits Claude-Code-only `hooks:`; deterministic checks run via `scripts/detect_slop.py` and CI | - |
| LB1 No overlapping descriptions | N/A | Standalone single-skill repository | - |
| LB2 Unused skills turned off | N/A | Standalone single-skill repository | - |
| FM1 Frontmatter parses | Pass | `SKILL.md:1-14` valid YAML starting on line 1 | - |
| FM2 Valid name | Pass | `SKILL.md:2` `name: unmistakable` matches folder `unmistakable`, 12 chars, `[a-z0-9-]+` | - |
| FM3 Name says the identity/activity | Pass | `SKILL.md:2` distinct non-vague craft standard name (`unmistakable`) | - |
| FM4 Only recognised portable fields | Pass | `SKILL.md:2-13` uses only `name`, `description`, `license`, `compatibility`, `metadata` | - |
| FM5 Invocation set on purpose | Pass | Model- and user-invocable across coding agents without conflicting flags | - |
| DS1 Present and within limits | Pass | `SKILL.md:3` 873 chars (`<= 1,024`), plain text, zero XML tags | - |
| DS2 Third person | Pass | `SKILL.md:3` `"Designs, extracts, audits, hardens, and ships..."` | - |
| DS3 What and when, in user words | Pass | `SKILL.md:3` states capabilities then `"Use when building or redesigning websites...; when a UI looks generic, templated, or AI-generated..."` | - |
| DS4 Key use case first | Pass | `SKILL.md:3` 873 chars (`<= 1,536`), anti-slop UI triggers upfront | - |
| ST1 SKILL.md body under 500 lines | Pass | 101 body lines | - |
| ST2 Most important instructions near top | Pass | `SKILL.md:22-41` Standing Rules & Command Router well inside 5,000-token budget | - |
| ST3 Split by area, details on demand | Pass | 7 domain-focused files under `references/` loaded only per active command | - |
| ST4 One level deep | Pass | Every file in `references/` and `assets/` linked directly from `SKILL.md`; zero reference-to-reference link chains | - |
| ST5 Contents list on long files | Pass | All 7 `references/*.md` files open with `## Contents` inside lines 1-20 | - |
| ST6 Every file reachable and well named | Pass | Validator: `0` dead links, `0` orphan files, `0` vague names | - |
| ST7 Forward slashes only | Pass | Validator: `0` backslash paths | - |
| CT1 Concise | Pass | `SKILL.md` holds routing and non-default anti-slop rules only | - |
| CT2 Freedom matches risk | Pass | High freedom on open aesthetic worlds; templates for HTML brand assets; exact scripts for slop/secret checks | - |
| CT3 Nothing time-sensitive | Pass | Validator: `0` dated rules or stale temporal phrases | - |
| CT4 One term per concept | Pass | Consistent terms (`Visitor Mode`, `Direction Contract`, `Foundations`) across files | - |
| CT5 Templates say how strict they are | Pass | `references/brand-and-design-system.md:45` ("sensible defaults") vs `references/seo-and-geo-patterns.md` JSON-LD accuracy | - |
| CT6 Examples where style matters | Pass | Concrete CSS token tiers, optical trim, JSON-LD `@graph`, and semantic HTML landmarks | - |
| CT7 A default, not a menu | Pass | Standard CSS Custom Properties (`:root`) as universal default | - |
| CT8 MCP tools named in full | Pass | No bare MCP tool names referenced | - |
| CT9 Nothing unfinished | Pass | Validator: `0` `TODO`, `FIXME`, or `[FILL:]` placeholders in skill instructions | - |
| CT10 One rule, one place | Pass | Token architecture in `agnostic-design-patterns.md`; banned patterns and depth model in `anti-patterns.md`; graphic language in `micrographics.md`; hardening in `production-hardening.md`; SEO/GEO in `seo-and-geo-patterns.md`; rule catalog in `commands-and-audit-rubric.md` | - |
| WF1 Checklist with finish lines & way back | Pass | `SKILL.md:67-99` copyable `- [ ]` checklists with `"Done when"` and `"If any check fails, return to Step 3"` | - |
| WF2 Feedback loop on quality output | Pass | `detect_slop.py` + `check_foundations.py` + `1440x900` / `390x844` viewport loop | - |
| WF3 Plan, validate, execute | Pass | Direction Contract + brand extraction confirmation before generating multi-file artifacts | - |
| WF4 Standing instructions | Pass | `SKILL.md:22-41` phrased as standing rules across every turn | - |
| SC1 Solve, don't defer | Pass | All 3 scripts handle missing files/browsers cleanly with `0`/`1`/`2` exit codes | - |
| SC2 No voodoo constants | Pass | Every constant in `scripts/*.py` has an inline comment stating its reason | - |
| SC3 Run or read is explicit | Pass | `SKILL.md:122-125` explicitly says `Run python3 scripts/...` | - |
| SC4 Errors that help | Pass | Every `UNM-01..57` finding prints `Fix:` remediation; `check_foundations.py` prints valid gate IDs | - |
| SC5 Packages listed / stdlib only | Pass | Python 3.8+ standard library only (`0` external imports) | - |
| NM1 Not too prescriptive | Pass | Avoids basic HTML/CSS tutorials; specifies only non-default craft and anti-slop invariants | - |
| NM2 No reasoning echo | Pass | Validator: `0` chain-of-thought extraction prompts | - |
| NM3 The reason, not only the request | Pass | Explains *why* (`<16px` triggers iOS Safari zoom; `min-width: auto` blows out flex cells; AI crawlers skip client JS) | - |
| NM4 Brief steering | Pass | Validator: `<= 2` uppercase emphasis words per file (`SHOUT_MAX = 5`), `--ban-em-dash` clean | - |
| NM5 Verification made explicit | Pass | Explicit CLI checks + dual-viewport rendered inspection | - |
| TS1 Evaluations first | Pass | `evals/prompts.md` + `evals/evals.json` (7 positive + 1 negative control) + `evals/test_unmistakable.py` (15 tests incl. before/after fixtures and false-positive guards) | - |
| TS2 Fresh-session readiness | Pass | Self-contained portable layout ready for fresh-session A/B runs | - |
| TS3 Cross-model efficiency | Pass | Compact ~110-line `SKILL.md` router works cleanly across fast and frontier models | - |
