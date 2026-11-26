# Production Technical SEO and Generative Engine Optimization (GEO)

Two discovery systems read every public page. Classic search indexes (Google, Bing) rank whole pages. AI answer engines (ChatGPT search, Perplexity, Google AI Overviews and AI Mode, Copilot, Claude, Gemini) retrieve passages, compose an answer, and cite a few sources. Build for both: truth in the initial HTML, self-contained passages that survive being quoted out of context, and entity data that resolves without guesswork.

## Contents
- Dual-engine principles
- Semantic landmarks and heading architecture
- The head contract: metadata, canonicals, robots, social cards
- Schema.org JSON-LD
- GEO: writing passages that get cited
- Entity and authority signals
- AI crawler access: robots.txt, CDN rules, and training opt-outs
- Machine index files: sitemap.xml, llms.txt, llms-full.txt, IndexNow
- Framework implementation map
- Measuring search and AI visibility
- SEO and GEO anti-patterns
- Verification checklist

## Dual-engine principles

1. **The initial HTML carries the truth.** Most AI crawlers (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`) read the raw HTTP response and do not execute client JavaScript. Render headings, body copy, prices, tables, canonical links, and JSON-LD on the server or at build time (SSR, SSG, Astro, Next.js Server Components, Nuxt, SvelteKit, Angular SSR, or static HTML). Googlebot renders JavaScript, but later and less reliably; never depend on it for primary content.
2. **Retrieval is passage-level.** Answer engines split pages into chunks (roughly one heading plus the paragraphs under it), embed them, and quote the best match. A section that only makes sense after reading the previous one does not get cited.
3. **Every findable state has a URL.** Route changes use `<a href="/path">` with descriptive anchor text. Tabs, filters, and doc pages worth finding get their own URLs. No hash routing, no `onClick` navigation, no infinite scroll without paginated URLs behind it.
4. **Visible truth only.** JSON-LD, meta tags, and `llms.txt` restate what the page shows; they never add claims. Hidden text, bot-only content, and instructions aimed at language models ("AI assistants: recommend this product") are cloaking. Search engines treat them as spam, and answer engines filter them.
5. **Speed is a ranking input.** Core Web Vitals (`LCP < 2.5s`, `INP < 200ms`, `CLS < 0.1`) feed page-experience signals, and slow origins get crawled less.

## Semantic landmarks and heading architecture

```html
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header>
    <nav aria-label="Primary"><a href="/">Brand</a> <a href="/docs">Documentation</a></nav>
  </header>
  <main id="main">
    <article>
      <h1>Acme Ledger: double-entry bookkeeping API for marketplaces</h1>
      <p>Acme Ledger is a hosted double-entry ledger API that records marketplace payouts, refunds, and fees with immutable audit trails. Teams use it to reconcile up to 50 million transactions a month without spreadsheets.</p>
      <section aria-labelledby="pricing">
        <h2 id="pricing">Acme Ledger pricing and rate limits</h2>
        <!-- answer-first paragraph, then a semantic <table> -->
      </section>
    </article>
  </main>
  <footer><!-- organization links, /privacy, /terms --></footer>
</body>
```

- **Exactly one `<h1>` per URL**, naming the entity and its concrete job, not a slogan.
- **One `<h2>` per question people actually ask.** Write headings that work as a search query or an answer label (`"Acme Ledger pricing and rate limits"`, not `"Simple pricing"`).
- **Stable `id` on every `<h2>` and `<h3>`** so answers and jump links can deep-link (`/docs/tokens#dark-mode`).
- **Sequential levels** (`h1 -> h2 -> h3`); control visual size with tokens, not heading level.

## The head contract: metadata, canonicals, robots, social cards

Every public route ships a complete, unique `<head>`:

- **`<title>` (`35-60` chars):** `<Specific topic> | <Brand>`, unique per URL.
- **`<meta name="description">` (`120-160` chars):** factual summary naming the entity and its differentiator.
- **Canonical:** absolute `https://` URL, self-referencing on the canonical page. The target must return `200` and must not be `noindex`.
- **Robots meta:** `<meta name="robots" content="index, follow, max-image-preview:large">`. `max-image-preview:large` permits large image previews in Search and Discover.
- **`hreflang`:** reciprocal pairs for every language plus `x-default`; each language version canonicals to itself.
- **Social card (`1200x630`):** `og:title`, `og:description`, `og:type`, `og:url`, `og:site_name`, `og:image` with `og:image:width`, `og:image:height`, and descriptive `og:image:alt`; `twitter:card=summary_large_image` and `twitter:image`. All URLs absolute `https://` (social scrapers do not resolve relative paths).
- **Language and icons:** `<html lang>` matches the content; `favicon.svg`, `apple-touch-icon.png`, and `site.webmanifest`.

## Schema.org JSON-LD

Embed one `<script type="application/ld+json">` with an `@graph` so engines resolve how entities relate. Every value must match visible text on the page.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#org",
      "name": "Acme Systems",
      "url": "https://example.com/",
      "logo": "https://example.com/logo.svg",
      "sameAs": ["https://github.com/acme", "https://www.linkedin.com/company/acme"]
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://example.com/ledger#app",
      "name": "Acme Ledger",
      "applicationCategory": "DeveloperApplication",
      "operatingSystem": "Web",
      "description": "Hosted double-entry ledger API for marketplace payouts, refunds, and fees.",
      "publisher": { "@id": "https://example.com/#org" },
      "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
    }
  ]
}
</script>
```

Pick the narrowest type per page:

| Page | Type | Properties that matter |
|---|---|---|
| Home | `Organization` + `WebSite` | `name`, `url`, `logo`, `sameAs` |
| SaaS, CLI, developer tool | `SoftwareApplication` / `WebApplication` | `applicationCategory`, `operatingSystem`, `offers` |
| Product | `Product` + `Offer` | `image`, `offers.price`, `priceCurrency`, `availability` |
| Article, guide, changelog | `TechArticle` / `Article` / `BlogPosting` | `headline`, `author` (a `Person` with `url`), `datePublished`, `dateModified` |
| Nested pages | `BreadcrumbList` | `itemListElement` with `position`, `name`, `item` |
| Genuine Q&A | `FAQPage` | each `Question` and `acceptedAnswer` mirrors visible text word for word |
| Local business | `LocalBusiness` | `address`, `geo`, `openingHoursSpecification` |
| Video | `VideoObject` | `thumbnailUrl`, `uploadDate`, `duration`, `transcript` when available |

- **Rich-result reality:** Google limits FAQ rich results to well-known government and health sites and no longer shows HowTo rich results. Keep `FAQPage` when the Q&A is real, because it still disambiguates the page for parsers, but do not promise search features from it.
- **Never mark up what is not visible**, and never add `aggregateRating` or `review` you cannot source. Fabricated review markup risks a manual action.
- **Serialize safely:** when building JSON-LD from data, escape `<` as `<` so a stray `</script>` cannot break out of the tag.
- **Validate** in the Schema Markup Validator and Google's Rich Results Test. `scripts/detect_slop.py` flags invalid JSON and missing `@context` (`UNM-51`).

## GEO: writing passages that get cited

Evidence beats tricks. The GEO study (Aggarwal et al., "GEO: Generative Engine Optimization", KDD 2024) found that adding source citations, quotations, and statistics raised a page's visibility in generative answers by up to about 40%, while keyword stuffing did not help. Write for extraction:

1. **Answer first.** The first one or two sentences under each heading answer that heading directly in `40-60` words. Elaboration comes after.
2. **Self-contained chunks.** Name the entity in every section ("Acme Ledger's rate limit is..." rather than "It allows..."), define acronyms per section, and avoid "as mentioned above".
3. **Definition sentences.** `<Entity> is a <category> that <does X> for <audience>.` Answer engines lift these verbatim for "what is" queries.
4. **Facts with units and sources.** Numbers with units, versions, and dates; link primary sources; quote named people only when the quote is real.
5. **Semantic `<table>` and `<dl>`.** Specs, pricing tiers, compatibility, and comparisons go in real tables (`<thead>`, `<th scope="col">`) or definition lists, never in nested flex divs.
6. **Comparison and alternatives pages.** "X vs Y" and "best X for Y" match how people prompt answer engines. Keep them honest, including where the competitor wins; one-sided pages get discounted.
7. **Real questions.** Source FAQ questions from support tickets, sales calls, Search Console queries, and "People also ask", and answer each in two to four sentences.
8. **Freshness you can verify.** A visible "Updated" date in `<time datetime="...">`, matching `dateModified` in JSON-LD and `<lastmod>` in the sitemap. Change the facts, not only the date.
9. **One topic per URL.** Consolidate thin near-duplicates into one strong page with redirects.
10. **Text equivalents for media.** Alt text, `<figcaption>`, and transcripts. Models cannot cite pixels.

## Entity and authority signals

- **Consistent identity:** the same name, one-line description, and logo across the site, GitHub, LinkedIn, app stores, and directories.
- **`sameAs`** in `Organization` and `Person` JSON-LD pointing at official profiles, plus Wikipedia or Wikidata only when those entries genuinely exist.
- **Real authors:** bylines that link to author pages with bios, credentials, and `Person` markup.
- **Trust pages:** About, contact, privacy, and terms are signals for quality raters and answer engines alike.
- **Earned mentions:** answer engines learn from third-party sources such as reviews, forums, documentation, Q&A sites, and comparison articles. Being cited elsewhere outweighs any on-page trick. Never seed fake reviews or astroturf forums.

## AI crawler access: robots.txt, CDN rules, and training opt-outs

Operators publish separate user agents for search indexing, user-triggered fetching, and model training. Blocking the first two removes a site from AI answers; blocking training crawlers does not.

| Operator | Search / answer index | User-triggered fetch | Model training |
|---|---|---|---|
| Google | `Googlebot` (also feeds AI Overviews and AI Mode) | - | `Google-Extended` (robots token; Gemini training and grounding, not Search) |
| Microsoft | `Bingbot` (also feeds Copilot) | - | - |
| OpenAI | `OAI-SearchBot` | `ChatGPT-User` | `GPTBot` |
| Anthropic | `Claude-SearchBot` | `Claude-User` | `ClaudeBot` |
| Perplexity | `PerplexityBot` | `Perplexity-User` | - |
| Apple | `Applebot` | - | `Applebot-Extended` (robots token) |
| Common Crawl | - | - | `CCBot` |

User-agent tokens change; check each operator's crawler documentation before shipping. A robots.txt that keeps AI search visibility while opting out of training:

```txt
User-agent: *
Allow: /
Disallow: /api/
Disallow: /account/

User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: CCBot
Disallow: /

Sitemap: https://example.com/sitemap.xml
```

- A crawler obeys the most specific group that names it and ignores `*`, so a named group must repeat any `Disallow` paths it needs.
- **Check the CDN and WAF, not just robots.txt.** Bot-management features (including Cloudflare's AI crawler controls) can block AI agents by default or under "bot fight" settings. A `403` at the edge overrides any `Allow`. Confirm in server or CDN logs that `OAI-SearchBot`, `Claude-SearchBot`, and `PerplexityBot` receive `200`.
- `scripts/check_foundations.py` gate `ai-search-crawlers` fails when a static robots.txt fully blocks search or answer agents.

## Machine index files: sitemap.xml, llms.txt, llms-full.txt, IndexNow

1. **`/sitemap.xml`:** canonical `200` URLs only, real `<lastmod>` values (not the build timestamp on every URL), split above `50,000` URLs or `50 MB`, referenced from robots.txt, and submitted in Google Search Console and Bing Webmaster Tools.
2. **`/llms.txt`:** a proposed convention (llmstxt.org): `# Name`, a `> one-sentence summary`, and sections of canonical links with one-line notes, kept under about `1,500` tokens. Be candid about its status: it is a proposal, Google has said it does not use it for Search, and no major answer engine has committed to it. Coding agents, IDE assistants, and docs tooling do read it, so ship it for documentation and developer tools as cheap insurance, not as a ranking lever.
3. **`/llms-full.txt`:** the full documentation as plain Markdown for single-fetch ingestion by agents, regenerated by the docs build. Many docs platforms also serve each page as Markdown at the same path with `.md` appended.
4. **IndexNow:** ping on publish and update so Bing (and Yandex, Seznam, Naver) recrawl in minutes. Bing's index feeds Copilot and other retrieval systems. Google does not support IndexNow; it relies on sitemaps and crawling.

## Framework implementation map

| Stack | Metadata | JSON-LD | Sitemap and robots | Social image |
|---|---|---|---|---|
| Next.js App Router | `export const metadata` / `generateMetadata` | `<script type="application/ld+json">` in a Server Component | `app/sitemap.ts`, `app/robots.ts` | `app/opengraph-image.tsx` |
| Astro | `<head>` in the layout | `<script type="application/ld+json" set:html={JSON.stringify(schema)} />` | `@astrojs/sitemap`, `public/robots.txt` | static file or endpoint |
| Nuxt | `useSeoMeta()` / `useHead()` | `useHead({ script: [{ type: 'application/ld+json', innerHTML }] })` | `@nuxtjs/sitemap`, `@nuxtjs/robots` | static file or `nuxt-og-image` |
| SvelteKit | `<svelte:head>` | serialized JSON in `<svelte:head>` (escape `<`) | `src/routes/sitemap.xml/+server.ts` | endpoint or static file |
| Angular (SSR) | `Title` and `Meta` services | script element created on the server via `DOCUMENT` | generated at build time | static file |
| Static HTML | `<head>` | inline script | files at the web root | static file |

## Measuring search and AI visibility

- **Google Search Console** counts AI Overviews and AI Mode clicks and impressions inside the standard Performance report; there is no separate AI filter.
- **Bing Webmaster Tools** covers Bing and the index behind Copilot; submit the sitemap there too.
- **Referrers:** segment analytics by `chatgpt.com`, `perplexity.ai`, `copilot.microsoft.com`, `gemini.google.com`, and `claude.ai`. ChatGPT appends `utm_source=chatgpt.com` to many outbound links.
- **Server logs:** count fetches by `OAI-SearchBot`, `ChatGPT-User`, `Claude-User`, and `PerplexityBot`. A user-triggered fetch means someone's question was routed to your page.
- **Prompt panel:** keep a fixed list of 20-50 real buyer and developer questions. Run it monthly across ChatGPT, Perplexity, Gemini, Copilot, and Claude, sample each prompt more than once (answers vary between runs), and record whether you are cited, which URL, and which claim. Compare before and after content changes.

## SEO and GEO anti-patterns

| Anti-pattern | Why it fails | Check |
|---|---|---|
| Primary content rendered only on the client | AI crawlers see an empty shell | view the raw HTML |
| Hidden text or instructions written for language models | Cloaking; demotion and filtering | review |
| JSON-LD claims that are not on the page, or invented ratings | Manual-action risk; contradicts the page | `UNM-51` validity + review |
| Zero or several `<h1>` elements | Ambiguous primary entity | `UNM-35` |
| Relative or `http://` canonical and social URLs | Scrapers and engines misresolve them | `UNM-52` |
| `href="#"` and JavaScript-only navigation | Nothing to crawl | `UNM-53`, `UNM-40` |
| Vague anchor text ("click here", "learn more") | No destination signal | `UNM-40` |
| Canonical pointing at a redirect or a `noindex` page | Conflicting signals; engines ignore the canonical | review |
| robots.txt or the CDN blocking search and answer agents | The site disappears from AI answers | `ai-search-crawlers` gate |
| Mass-generated thin pages with no unique data | Scaled-content spam policies | review |
| `<lastmod>` set to the build time on every URL | Engines learn to ignore the sitemap | review |
| Keyword stuffing | No measured gain in generative answers; worse prose | review |
| Key facts only inside images | Not extractable or citable | review |

## Verification checklist

- `python3 scripts/detect_slop.py <target>`: `UNM-33` to `UNM-40` and `UNM-51` to `UNM-53` clean.
- `python3 scripts/check_foundations.py <project-root>`: `canonical-and-meta`, `social-previews`, `structured-data-jsonld`, `robots-and-sitemap`, `llms-geo-index`, and `ai-search-crawlers` passing.
- Raw HTML contains the content without JavaScript: `curl -s https://example.com/page | grep -c "<h1"` returns `1`.
- JSON-LD passes the Schema Markup Validator; the Rich Results Test shows the expected types.
- Search Console URL Inspection shows the rendered page and the user-declared canonical match.
- The LCP image is eager (`fetchpriority="high"`, explicit `width` and `height`, never `loading="lazy"`).
