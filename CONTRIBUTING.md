# Contributing to Unmistakable

Contributions that sharpen deterministic rules, catch new AI tells, cut false positives, or reduce token footprint are welcome.

## Fastest ways to help

- **Report a tell the scanner misses:** open a [new slop pattern](https://github.com/AntonioCardenas/unmistakable/issues/new?template=new-slop-pattern.yml) issue with the smallest snippet that reproduces it and, ideally, a screenshot of real generated output.
- **Report a false positive:** open a [false positive](https://github.com/AntonioCardenas/unmistakable/issues/new?template=false-positive.yml) issue with the rule ID and why the usage is correct.

## Adding or changing a scanner rule

1. Add the rule to `RULES` in `scripts/detect_slop.py` with the next free `UNM-XX` ID, a severity (`P0` blocking to `P3` polish), a one-line description, and a concrete fix. Never renumber existing IDs; waivers in user code depend on them.
2. Name every new numeric threshold as a constant with a comment explaining why that value.
3. Add a positive test **and** a false-positive guard in `evals/test_unmistakable.py`. If the tell appears in typical generated pages, add it to `evals/fixtures/slop-landing.html` and keep `evals/fixtures/unmistakable-landing.html` at zero findings.
4. Document the rule in the catalog table in `references/commands-and-audit-rubric.md` and in the matching section of `references/anti-patterns.md`.
5. Update the rule count wherever it appears (`README.md`, `README.es.md`, `SKILL.md`, `llms.txt`, `llms-full.txt`, plugin manifests, `action.yml`). The test suite fails if `RULES` and the expected count disagree.

## Authoring standards (`skill-creator-plus` aligned)

1. **Absorb, do not layer:** fold refinements into existing rules rather than appending duplicate caveats. Keep `SKILL.md` well under 500 lines and link every file in `references/` directly from `SKILL.md` (one level deep).
2. **Contents headers on long references:** any Markdown file in `references/` over 100 lines opens with a `## Contents` list inside its first 50 lines.
3. **No em-dashes** in `SKILL.md` or `references/`; the test suite enforces it.
4. **Zero external runtime dependencies:** scripts in `scripts/` run on the Python 3.8+ standard library only and return deterministic exit codes (`0` clean, `2` findings, `1` error).
5. **Verify before opening a PR:**
   ```bash
   npm test
   python3 scripts/detect_slop.py evals/fixtures/unmistakable-landing.html
   ```
