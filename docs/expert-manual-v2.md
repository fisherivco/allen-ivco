# IVCO Expert Manual v2.0

> Architecture, operations, and data constitution for the IVCO content + research platform.
> Replaces NotebookLM v1.0. Reflects actual deployed code as of 2026-02-16.

---

## Part 1: Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Payload CMS (Next.js 15)              │
│            Content management + SSR frontend              │
│   Posts • Authors • Categories • Companies • Events       │
│            @payloadcms/db-postgres (Drizzle ORM)          │
├─────────────────────────────────────────────────────────┤
│                    Supabase (PostgreSQL)                   │
│        Financial data + AI analysis (Python CLI)          │
│  historical_owner_earnings • company_financials           │
│  watchlist_signals • iv_calculations                      │
│           JSONB columns for AI flexibility                │
├─────────────────────────────────────────────────────────┤
│                    Python CLI v0.2.0                       │
│     ivco calc-oe • ivco calc-iv • ivco fetch              │
│     ivco analyze • ivco collect • ivco-xsearch            │
├─────────────────────────────────────────────────────────┤
│                    n8n Automation (Phase 1.0)              │
│     Deep Value Council • Triple Output Pipeline           │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Python CLI** fetches financial data → stores in **Supabase** tables
2. **Python CLI** calculates OE/IV → stores results in `iv_calculations`
3. **X Intel pipeline** (`ivco-xsearch`) → stores signals in `watchlist_signals`
4. **Payload CMS** manages blog content, author bios, company profiles
5. **Next.js frontend** renders articles with SEO metadata + JSON-LD structured data
6. **Vercel** hosts the production deployment at `ivco.io`

### Separation of Concerns

| System | Owns | Does NOT own |
|--------|------|-------------|
| **Payload CMS** | Blog content, authors, categories, company display data, SEO metadata | Financial calculations, IV computations, signal processing |
| **Supabase** | Historical financials, OE data, IV results, watchlist signals, AI analysis JSONB | Content display, SEO, blog rendering |
| **Python CLI** | Calculation logic, data fetching, analysis pipelines | Content management, frontend rendering |

### Key Files

| File | Purpose |
|------|---------|
| `cms/src/payload.config.ts` | Payload configuration (collections, DB adapter) |
| `cms/src/app/(frontend)/layout.tsx` | Root layout with metadataBase |
| `cms/src/app/(frontend)/posts/[slug]/page.tsx` | Article page (rich text + SEO + JSON-LD) |
| `cms/src/lib/structured-data.ts` | JSON-LD generators (Article, FAQ, HowTo) |
| `cli/ivco-calc/` | Python CLI package |
| `supabase/migrations/` | Database schema migrations |

> For development disciplines (atomic commits, TDD, PDCA), see `~/.claude/rules/02-development-disciplines.md`.

---

## Part 2: AI Operation Manual

### Content Creation Workflow

**Persona**: IVCO Fisher — American value investor, English-native, nearly three decades of experience. Voice: calm, factual, quietly authoritative. No hype words.

**Pipeline**:
```
1. Draft    → Codex/Claude Desktop writes in Fisher voice
2. Review   → Jane 8-dimension review (test, verify, document, version, maintain, upgrade, atomic, rollback)
3. Edit     → Fix issues from review
4. Approve  → Allen final review
5. Publish  → Admin UI: paste content → add FAQ → set ogImage → publish
```

**Fisher Persona Prompt** (for draft generation):
```
You are IVCO Fisher, a rational value investor who has studied annual reports since the 1990s.
Write in English. Tone: calm, factual, "quietly authoritative."
Philosophy: Graham's margin of safety, Buffett's Owner Earnings, Fisher's management insight, Munger's inversion.
Rules:
- Facts before opinions. Historical OE CAGR anchors every claim.
- Intrinsic value is always a RANGE, never a single number.
- Always ask "how could this fail?" before concluding.
- No hype words: skyrocket, moon, guaranteed, explosive.
- Include Python code examples where relevant (readers can verify).
- End with FAQ (min 3 questions for structured data).
```

### Vercel Deployment SOP

**Configuration**:
- Repository: `fisherivco/allen-ivco`
- Root Directory: `cms/`
- Framework: Next.js
- Build Command: `pnpm build`
- Install Command: `pnpm install`
- Region: `hnd1` (Tokyo — matches Supabase ap-northeast-1)
- Node.js: 20.x

**Environment Variables on Vercel**:
| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | Supabase Session Pooler URL | `aws-0-ap-northeast-1.pooler.supabase.com:5432` |
| `PAYLOAD_SECRET` | Random 32-char string | Generate with `openssl rand -hex 16` |
| `NEXT_PUBLIC_SERVER_URL` | `https://ivco.io` | Used by Payload for absolute URLs |

**Deploy Process**:
```
git push origin main → Vercel auto-deploys → Preview URL → Promote to production
```

**Media Storage Caveat**: MVP uses Vercel's ephemeral filesystem for uploads. On redeploy, uploaded images may be lost. Phase 2 adds `@payloadcms/storage-s3` or Supabase Storage for persistent media.

### @vercel/og Integration

Dynamic OG images generated at `/api/og?title=...&category=...`.

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `title` | No | "IVCO Fisher" | Article title, max ~80 chars |
| `category` | No | "framework" | Badge color: framework=blue, case-study=green, brand-story=purple, opinion=amber |

Output: 1200×630 PNG with dark background (#1a1a1a), white text, IVCO branding.

**Usage in CMS**: When creating a post, if no ogImage is uploaded, the frontend falls back to `/api/og?title={title}&category={category}` for social sharing previews.

### Content Import Workflow

**Seed Script** (`scripts/seed-blog.ts`):
```bash
cd /path/to/allen-ivco/cms
npx tsx ../scripts/seed-blog.ts
```
Creates: 1 author (IVCO Fisher), 4 categories, 7 posts as drafts with placeholder content.

**Manual Content Entry** (per article, ~15 min each):
1. Open Admin UI → Posts → select draft article
2. Clear placeholder paragraph from Content field
3. Paste markdown content into Lexical editor (supports headings, code blocks, tables, lists, images)
4. Scroll to FAQ section → replace 3 placeholder Q&As with real questions
5. Set `schema.authorBio` to article-specific author bio
6. Upload or generate ogImage (via `/api/og` route)
7. Set SEO title (≤60 chars) and description (≤160 chars)
8. Change status to `published`, set `publishedAt` date
9. Save → verify on frontend

### RSC Data Fetching Patterns

Payload CMS 3.x with Next.js 15 uses React Server Components. All data fetching happens server-side:

```typescript
// In page.tsx (Server Component)
import { getPayload } from 'payload'
import config from '@/payload.config'

const payload = await getPayload({ config: await config })
const result = await payload.find({
  collection: 'posts',
  where: { slug: { equals: slug }, status: { equals: 'published' } },
  depth: 2,  // Populate relationships (author, category, ogImage)
  limit: 1,
})
```

**Key patterns**:
- `depth: 0` = IDs only, `depth: 1` = first-level relationships, `depth: 2` = nested relationships
- Use `select` to limit returned fields for performance
- `where` filters run server-side (no client-side filtering needed)
- Rich text renders via `<RichText data={post.content} />` from `@payloadcms/richtext-lexical/react`

---

## Part 3: Data Constitution

### Payload CMS Collections (7 total)

#### Posts (`posts`) — Blog articles with built-in SEO

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | text | ✅ | Article title |
| `slug` | text | ✅ | URL path, lowercase alphanumeric + hyphens, unique |
| `author` | relationship → authors | ✅ | Article author |
| `content` | richText (Lexical) | ✅ | Full article body |
| `excerpt` | textarea | | Preview text for cards/RSS |
| `category` | relationship → categories | ✅ | Single category |
| `tags` | array of `{tag: text}` | | Freeform tags |
| `relatedCompany` | relationship → companies | | Link to company for case studies |
| `coverImage` | upload → media | | Cover image |
| `status` | select | ✅ | draft → ai_reviewing → ready → published |
| `publishedAt` | date | | Shown when status = published |
| `seo.title` | text (max 60) | ✅ | SERP title |
| `seo.description` | textarea (max 160) | ✅ | Meta description |
| `seo.ogImage` | upload → media | ✅ | 1200×630px social preview |
| `seo.canonicalUrl` | text | | Only if cross-posted |
| `faq[]` | array (min 3) | ✅ | Q&A pairs → FAQPage JSON-LD |
| `faq[].question` | text | ✅ | |
| `faq[].answer` | textarea | ✅ | |
| `schema.enableHowTo` | checkbox | | For step-by-step articles |
| `schema.authorBio` | textarea | ✅ | E-E-A-T signal, article-specific |

#### Authors (`authors`)

| Field | Type | Required |
|-------|------|----------|
| `name` | text | ✅ |
| `bio` | textarea | ✅ |
| `avatar` | upload → media | |

#### Categories (`categories`)

| Field | Type | Required |
|-------|------|----------|
| `name` | text | ✅ |
| `slug` | text | ✅ (unique) |

#### Companies (`companies`) — 5-tab Allen Framework stages

**Tab 1: Basic Info**: name, ticker (unique), exchange, status, industry, country, website, monitoring_level, keywords, notes

**Tab 2: Integrity Gate (Stage 1)**: integrity_score (0-100%), integrity_status (pass/warning/fail), integrity_notes

**Tab 3: Historical Facts (Stage 2)**: latest_oe, oe_currency, historical_cagr_7y, total_shares, maintenance_capex_ratio, historical_notes

**Tab 4: Forward Factors (Stage 3)**: confidence_low, confidence_high, iv_total_low/high, iv_per_share_low/high (computed, optional), forward_factors

**Tab 5: Real-time Navigation (Stage 4)**: current_price, price_updated_at, deviation_percentage, investment_decision, stress_test_50, navigation_notes

#### CompanyEvents (`company-events`)

| Field | Type | Required |
|-------|------|----------|
| `company` | relationship → companies | ✅ |
| `event_date` | date | ✅ |
| `source` | select | ✅ |
| `importance` | select | default: medium |
| `title` | text | ✅ |
| `summary` | textarea | |
| `raw_content` | textarea | |
| `source_url` | text | |
| `keywords` | text (comma-separated) | |
| `ivco_impact` | select | |

#### Media (`media`) — Upload collection (images)

#### Users (`users`) — Payload default auth collection

### SEO Schema Requirements

Every published post MUST have:
1. **SEO group filled**: `seo.title` (≤60 chars), `seo.description` (≤160 chars), `seo.ogImage` (optional — falls back to `/api/og` dynamic generation)
2. **FAQ min 3 entries**: Generates FAQPage JSON-LD automatically
3. **authorBio filled**: E-E-A-T signal for Google

### Supabase Tables (4 tables, Python CLI managed)

These tables are separate from Payload CMS tables. They share the same PostgreSQL database but are managed by Python CLI, not Payload's Drizzle ORM.

#### `historical_owner_earnings`

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGINT (identity) | PK |
| `company_ticker` | TEXT | Not null |
| `year` | INTEGER | Not null |
| `net_income` | BIGINT | |
| `depreciation` | BIGINT | |
| `amortization` | BIGINT | |
| `capex` | BIGINT | |
| `maintenance_ratio` | NUMERIC(4,2) | |
| `owner_earnings` | BIGINT | |
| `reality_coefficient` | NUMERIC(4,2) | Default 1.00 |
| `oe_calibrated` | BIGINT | |
| `cagr_from_base` | NUMERIC(6,4) | |
| `adjustments_json` | JSONB | Per-year adjustments (v0.2+) |
| `currency` | TEXT | Default 'NTD' |
| `source` | TEXT | |
| Unique | `(company_ticker, year)` | |

#### `company_financials`

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGINT (identity) | PK |
| `ticker` | TEXT | |
| `period` | TEXT | e.g. '2024-Q4', '2024-FY' |
| `period_type` | TEXT | 'quarterly' or 'annual' |
| Revenue, net_income, total_assets, total_debt, fcf, shares, etc. | various | Financial snapshot |
| `analysis_output` | JSONB | AI analysis results (v0.2+) |
| `source_api` | TEXT | 'fmp', 'yahoo', 'manual' |
| Unique | `(ticker, period, source_api)` | |

#### `watchlist_signals`

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGINT (identity) | PK |
| `ticker` | TEXT | Nullable for macro signals |
| `signal_type` | TEXT | 'x_intel', 'news', 'earnings', etc. |
| `headline` | TEXT | |
| `content` | TEXT | |
| `analysis_output` | JSONB | AI analysis output (v0.2+) |
| `relevance_score` | NUMERIC(3,2) | |
| `processed` | BOOLEAN | Default false |

#### `iv_calculations`

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGINT (identity) | PK |
| `ticker` | TEXT | |
| 7 Allen Framework parameters | various | maintenance_ratio, reality_coefficient, cc_low/high, stage2/3_cagr, discount_rate |
| `iv_per_share_low/high` | NUMERIC(12,2) | Required output |
| `parameters_json` | JSONB | Full parameter snapshot |
| `source_research_id` | TEXT | Links to research provenance |

### EAV + JSONB Design Strategy

**When to use structured columns**: Data with known schema that needs SQL filtering (e.g., `ticker`, `year`, `iv_per_share_low`). These are your WHERE clause targets.

**When to use JSONB**: Data with evolving schema or agent-generated output (e.g., AI sentiment analysis, risk scores, entity extraction results). The `analysis_output` columns accept any JSON structure without migration.

**Schema evolution strategy**:
1. New AI analysis type → write to JSONB `analysis_output` immediately (no migration needed)
2. Once a JSONB field is queried frequently → promote to a dedicated column via migration
3. GIN indexes on JSONB columns enable efficient `@>` containment queries
4. Example: `SELECT * FROM watchlist_signals WHERE analysis_output @> '{"sentiment": "bearish"}'`

---

## Part 4: SEO & Maintenance

### Sitemap

File: `cms/src/app/(frontend)/sitemap.ts`

Generates `/sitemap.xml` dynamically from published posts. Includes homepage (priority 1.0, weekly) and all published articles (priority 0.8, monthly).

### Robots

File: `cms/src/app/(frontend)/robots.ts`

Allows all crawlers. Disallows `/admin/*` and `/api/*`. Points to `/sitemap.xml`.

### JSON-LD Injection

File: `cms/src/lib/structured-data.ts` (generators) + `posts/[slug]/page.tsx` (injection)

Each article page includes:
1. **Article schema**: headline, description, author, publisher, dates, image
2. **FAQPage schema**: auto-generated from post's FAQ array (min 3 Q&A)
3. **HowTo schema** (optional): enabled per-post via `schema.enableHowTo` checkbox

Validation: Use [Google Rich Results Test](https://search.google.com/test/rich-results) to verify structured data.

### OG Image Generation

Route: `cms/src/app/(frontend)/api/og/route.tsx`

Edge runtime. Accepts `title` and `category` query params. Returns 1200×630 PNG.

Category color mapping:
- `framework` → blue (#2563eb)
- `case-study` → green (#059669)
- `brand-story` → purple (#7c3aed)
- `opinion` → amber (#d97706)

### TSMC Smoke Test

Before any production deploy, verify the TSMC case study renders correctly:
1. IV Range displayed: NT$4,565 ~ NT$5,639
2. All code blocks render with syntax highlighting
3. FAQ section shows 3+ questions
4. JSON-LD validates in Rich Results Test
5. OG image generates with correct title and "case study" badge

### Cache Revalidation

Payload CMS 3.x with Next.js uses ISR (Incremental Static Regeneration) by default:
- Pages are statically generated at build time
- On-demand revalidation triggered by Payload webhook on publish/update
- For MVP: manual redeploy via Vercel dashboard or `git push` triggers full rebuild

### Monitoring Checklist (Post-Launch)

| Check | Frequency | Tool |
|-------|-----------|------|
| Sitemap accessible | Weekly | `curl https://ivco.io/sitemap.xml` |
| Rich Results valid | Per article | Google Rich Results Test |
| OG images render | Per article | Twitter Card Validator |
| Supabase DB awake | Daily | `psql` connection test |
| X Intel pipeline | Daily | `x-intel-collect.log` |
| Build errors | Per deploy | Vercel dashboard |

---

## Appendix: Migration Files

| File | Content |
|------|---------|
| `supabase/migrations/001_core_tables.sql` | 4 core tables (OE, financials, signals, IV calculations) |
| `supabase/migrations/002_add_jsonb_fields.sql` | JSONB columns + GIN indexes on 3 tables |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-02-14 | NotebookLM original (Obsidian `reference/ivco/cms-guides/`) |
| v2.0 | 2026-02-16 | Full rewrite reflecting actual deployed architecture: 7 collections, Supabase JSONB, Vercel deploy, OG images, seed script, JSON-LD injection |
