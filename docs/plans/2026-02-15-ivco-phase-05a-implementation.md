# IVCO Phase 0.5a Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the foundation for IVCO's blog launch + data infrastructure — Payload CMS with SEO schema baked in, Supabase tables for financial data, Python CLI data fetcher, Agent DNA files, and tool ecosystem skeleton.

**Architecture:** Payload CMS (Next.js App Router embedded) with Posts/Authors/Companies/Categories/CompanyEvents collections. SEO structured data (Article + FAQPage JSON-LD) enforced at collection level. Supabase for financial data persistence. Python CLI extended with fetch/analyze commands. Agent DNA files for future Deep Value Council.

**Tech Stack:** Payload CMS 3.75.0, Next.js 15, TypeScript, Supabase (PostgreSQL), Python 3.10+, Click CLI, Vitest (CMS tests), Pytest (CLI tests)

**Design Document:** `docs/plans/2026-02-15-ivco-phase-05-1-design.md`

---

## Existing State (What's Already Built)

**Payload CMS (`cms/`):**
- `Users.ts` — auth, email only
- `Media.ts` — file uploads
- `Companies.ts` — 4-tab layout (basic info, integrity, historical, forward, navigation) ✅ Rich
- `CompanyEvents.ts` — signals/events per company ✅ Rich
- `Categories.ts` — simple name + slug ✅
- `Posts.ts` — basic blog (title, slug, content, excerpt, category, coverImage, status) ⚠️ Missing SEO/FAQ/Author/Tags

**Python CLI (`cli/ivco-calc/`):**
- `owner_earnings.py`, `cagr.py`, `dcf.py`, `verify.py` — core calculations ✅
- `cli.py` — 4 commands: calc-oe, calc-cagr, calc-iv, verify ✅
- 11 tests passing ✅

**Missing:**
- Authors collection (no file)
- SEO fields on Posts (seo.title, seo.description, seo.ogImage, FAQ array, schema.authorBio)
- Supabase tables (none created)
- Python fetchers (no ivco-fetch, no ivco-analyze)
- Agent DNA files (none)
- Tool ecosystem meta-commands (no --list-tools)

---

## Task 1: Create Authors Collection

**Files:**
- Create: `cms/src/collections/Authors.ts`
- Modify: `cms/src/payload.config.ts`

**Step 1: Create Authors collection file**

Create `cms/src/collections/Authors.ts`:

```typescript
import type { CollectionConfig } from 'payload'

export const Authors: CollectionConfig = {
  slug: 'authors',
  admin: {
    useAsTitle: 'name',
    group: 'Blog',
  },
  access: {
    read: () => true,
  },
  fields: [
    {
      name: 'name',
      type: 'text',
      required: true,
      label: 'Name',
    },
    {
      name: 'bio',
      type: 'textarea',
      required: true,
      label: 'Bio',
      admin: {
        description: 'Author bio for E-E-A-T signal (appears at bottom of articles)',
      },
    },
    {
      name: 'avatar',
      type: 'upload',
      relationTo: 'media',
      label: 'Avatar',
    },
  ],
}
```

**Step 2: Register Authors in payload.config.ts**

In `cms/src/payload.config.ts`, add import and include in collections array:

```typescript
import { Authors } from './collections/Authors'
// ...
collections: [Users, Media, Authors, Companies, CompanyEvents, Categories, Posts],
```

**Step 3: Verify TypeScript compiles**

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cms && pnpm exec tsc --noEmit`
Expected: No errors

**Step 4: Commit**

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cms/src/collections/Authors.ts cms/src/payload.config.ts
git commit -m "feat(cms): add Authors collection for blog E-E-A-T

Authors have name, bio (required), and avatar. Required by Posts
collection for author attribution and structured data.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Upgrade Posts Collection with SEO Schema

> Allen's directive: "每篇文章必須有完整 Structured Data Schema (Article + FAQ)，在 Payload CMS Collection 層級強制要求"
> Reference: `shared-state/inbox/claude-code/2026-02-14-24-schema-enforcement-consensus.json`

**Files:**
- Modify: `cms/src/collections/Posts.ts`

**Step 1: Rewrite Posts.ts with full SEO schema**

Replace `cms/src/collections/Posts.ts` with the upgraded version. Key changes from existing:
- Add `author` relationship to Authors
- Add `tags` array field
- Add `seo` group (title ≤60 chars, description ≤160 chars, ogImage required, canonicalUrl optional)
- Add `faq` array (min 3 items, required)
- Add `schema.enableHowTo` checkbox
- Add `schema.authorBio` textarea (required)
- Expand `status` options: draft / ai_reviewing / ready / published
- Keep existing fields: title, slug, content, excerpt, category, coverImage, publishedAt

```typescript
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'author', 'category', 'status', 'publishedAt'],
    group: 'Blog',
  },
  access: {
    read: () => true,
  },
  fields: [
    // === Core Content ===
    {
      name: 'title',
      type: 'text',
      required: true,
      label: 'Title',
    },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
      label: 'Slug',
      validate: (value: string | null | undefined) => {
        if (!value) return 'Slug is required'
        if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)) {
          return 'Slug must be lowercase alphanumeric with hyphens only'
        }
        return true
      },
      admin: {
        description: 'URL path (e.g. tsmc-intrinsic-value-case-study)',
      },
    },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'authors',
      required: true,
      label: 'Author',
    },
    {
      name: 'content',
      type: 'richText',
      required: true,
      label: 'Content',
    },
    {
      name: 'excerpt',
      type: 'textarea',
      label: 'Excerpt',
      admin: {
        description: 'Preview text for cards and RSS (optional, falls back to seo.description)',
      },
    },
    {
      name: 'category',
      type: 'relationship',
      relationTo: 'categories',
      required: true,
      label: 'Category',
    },
    {
      name: 'tags',
      type: 'array',
      label: 'Tags',
      fields: [
        {
          name: 'tag',
          type: 'text',
          required: true,
        },
      ],
    },
    {
      name: 'relatedCompany',
      type: 'relationship',
      relationTo: 'companies',
      label: 'Related Company',
      admin: {
        description: 'Link to company if this is a case study or analysis',
      },
    },
    {
      name: 'coverImage',
      type: 'upload',
      relationTo: 'media',
      label: 'Cover Image',
    },
    {
      name: 'status',
      type: 'select',
      required: true,
      defaultValue: 'draft',
      label: 'Status',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'AI Reviewing', value: 'ai_reviewing' },
        { label: 'Ready', value: 'ready' },
        { label: 'Published', value: 'published' },
      ],
    },
    {
      name: 'publishedAt',
      type: 'date',
      label: 'Published At',
      admin: {
        date: { pickerAppearance: 'dayAndTime' },
        condition: (data) => data?.status === 'published',
      },
    },

    // === SEO (Required — Allen directive: baked into CMS, not afterthought) ===
    {
      name: 'seo',
      type: 'group',
      label: 'SEO',
      fields: [
        {
          name: 'title',
          type: 'text',
          required: true,
          maxLength: 60,
          label: 'SEO Title',
          admin: {
            description: 'SERP title (max 60 characters)',
          },
        },
        {
          name: 'description',
          type: 'textarea',
          required: true,
          maxLength: 160,
          label: 'Meta Description',
          admin: {
            description: 'SERP description (max 160 characters)',
          },
        },
        {
          name: 'ogImage',
          type: 'upload',
          relationTo: 'media',
          required: true,
          label: 'OG Image',
          admin: {
            description: 'Social sharing preview image (1200x630px recommended)',
          },
        },
        {
          name: 'canonicalUrl',
          type: 'text',
          label: 'Canonical URL',
          admin: {
            description: 'Only if cross-posted elsewhere',
          },
        },
      ],
    },

    // === FAQ (Required — auto-generates FAQPage JSON-LD) ===
    {
      name: 'faq',
      type: 'array',
      required: true,
      minRows: 3,
      label: 'FAQ (min 3 questions)',
      admin: {
        description: 'Required for FAQPage structured data. Minimum 3 Q&A pairs.',
      },
      fields: [
        {
          name: 'question',
          type: 'text',
          required: true,
          label: 'Question',
        },
        {
          name: 'answer',
          type: 'textarea',
          required: true,
          label: 'Answer',
        },
      ],
    },

    // === Schema Options ===
    {
      name: 'schema',
      type: 'group',
      label: 'Structured Data',
      fields: [
        {
          name: 'enableHowTo',
          type: 'checkbox',
          label: 'Enable HowTo Schema',
          defaultValue: false,
          admin: {
            description: 'Turn on for step-by-step articles (e.g. TSMC Case Study)',
          },
        },
        {
          name: 'authorBio',
          type: 'textarea',
          required: true,
          label: 'Author Bio (for this article)',
          admin: {
            description: 'E-E-A-T signal — author bio specific to this article\'s topic',
          },
        },
      ],
    },
  ],
}
```

**Step 2: Verify TypeScript compiles**

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cms && pnpm exec tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cms/src/collections/Posts.ts
git commit -m "feat(cms): upgrade Posts with SEO schema, FAQ, author

Allen directive: structured data baked into CMS at collection level.
- SEO group: title (<=60), description (<=160), ogImage (required)
- FAQ array: min 3 Q&A pairs, auto-generates FAQPage JSON-LD
- Author relationship to Authors collection
- Tags array, relatedCompany, schema.enableHowTo, schema.authorBio
- Status: draft/ai_reviewing/ready/published
- Slug validation: lowercase alphanumeric with hyphens

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Add Maintenance Ratio + Exchange to Companies

The existing Companies.ts is already rich (4 tabs). Add the Allen Framework parameters specified in design that are missing.

**Files:**
- Modify: `cms/src/collections/Companies.ts`

**Step 1: Add missing Allen Framework fields**

Add these fields to the existing `階段二：歷史事實` tab, after `total_shares`:

```typescript
{
  name: 'maintenance_capex_ratio',
  type: 'number',
  label: 'Maintenance CapEx Ratio',
  min: 0,
  max: 1,
  admin: {
    description: 'Allen Framework parameter: fraction of capex that is maintenance (e.g. 0.20 for TSMC)',
    step: 0.01,
  },
},
```

Add `exchange` field to the `基本資訊` tab, after `ticker`:

```typescript
{
  name: 'exchange',
  type: 'select',
  label: 'Exchange',
  options: [
    { label: 'NYSE', value: 'NYSE' },
    { label: 'NASDAQ', value: 'NASDAQ' },
    { label: 'TPE (Taiwan)', value: 'TPE' },
    { label: 'HKEX (Hong Kong)', value: 'HKEX' },
    { label: 'Other', value: 'other' },
  ],
  admin: {
    description: 'Primary stock exchange listing',
  },
},
```

**Step 2: Verify TypeScript compiles**

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cms && pnpm exec tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cms/src/collections/Companies.ts
git commit -m "feat(cms): add maintenance_capex_ratio + exchange to Companies

Allen Framework parameter for OE calculation. Exchange field for
multi-market watchlist support.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Create Supabase Migration — 4 Core Tables

**Files:**
- Create: `supabase/migrations/001_core_tables.sql`

**Step 1: Create migration directory**

```bash
mkdir -p /Users/allenchenmac/fisher/projects/allen-ivco/supabase/migrations
```

**Step 2: Write migration SQL**

Create `supabase/migrations/001_core_tables.sql`:

```sql
-- IVCO Core Tables — Phase 0.5a Foundation
-- These tables are written by Python CLI tools, not Payload CMS.
-- Payload CMS uses its own PostgreSQL tables via Drizzle ORM.

-- 1. Historical Owner Earnings (Python CLI: ivco calc-oe → ivco-store)
CREATE TABLE IF NOT EXISTS historical_owner_earnings (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  company_ticker TEXT NOT NULL,
  year INTEGER NOT NULL,
  net_income BIGINT NOT NULL,
  depreciation BIGINT NOT NULL,
  amortization BIGINT NOT NULL,
  capex BIGINT NOT NULL,
  maintenance_ratio NUMERIC(4,2) NOT NULL,
  owner_earnings BIGINT NOT NULL,
  reality_coefficient NUMERIC(4,2) DEFAULT 1.00,
  oe_calibrated BIGINT,
  cagr_from_base NUMERIC(6,4),
  currency TEXT DEFAULT 'NTD',
  source TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (company_ticker, year)
);

-- 2. Company Financial Snapshots (Finance API periodic fetch)
CREATE TABLE IF NOT EXISTS company_financials (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticker TEXT NOT NULL,
  period TEXT NOT NULL,         -- e.g. '2024-Q4', '2024-FY'
  period_type TEXT NOT NULL,    -- 'quarterly' or 'annual'
  revenue BIGINT,
  net_income BIGINT,
  total_assets BIGINT,
  total_debt BIGINT,
  fcf BIGINT,
  shares_outstanding BIGINT,
  pe_ratio NUMERIC(8,2),
  market_cap BIGINT,
  gross_margin NUMERIC(6,4),
  operating_margin NUMERIC(6,4),
  dso NUMERIC(6,2),
  dio NUMERIC(6,2),
  currency TEXT DEFAULT 'USD',
  fetched_at TIMESTAMPTZ DEFAULT NOW(),
  source_api TEXT NOT NULL,     -- 'fmp', 'yahoo', 'manual'
  UNIQUE (ticker, period, source_api)
);

-- 3. Watchlist Signals (X Intel + News + Events)
CREATE TABLE IF NOT EXISTS watchlist_signals (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticker TEXT,                  -- nullable for macro signals
  signal_type TEXT NOT NULL,    -- 'x_intel', 'news', 'earnings', 'filing', 'capex', 'management'
  headline TEXT NOT NULL,
  content TEXT,
  source TEXT,
  source_url TEXT,
  relevance_score NUMERIC(3,2),
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. IV Calculations (Research engine output)
CREATE TABLE IF NOT EXISTS iv_calculations (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticker TEXT NOT NULL,
  calculated_at TIMESTAMPTZ DEFAULT NOW(),
  -- Allen Framework 7 parameters
  maintenance_ratio NUMERIC(4,2) NOT NULL,
  reality_coefficient NUMERIC(4,2) DEFAULT 1.00,
  historical_cagr NUMERIC(6,4) NOT NULL,
  cc_low NUMERIC(4,2) NOT NULL,
  cc_high NUMERIC(4,2) NOT NULL,
  stage1_cagr_low NUMERIC(6,4),
  stage1_cagr_high NUMERIC(6,4),
  stage2_cagr NUMERIC(6,4) NOT NULL,
  stage3_growth NUMERIC(6,4) NOT NULL,
  discount_rate NUMERIC(6,4) NOT NULL,
  long_term_debt BIGINT DEFAULT 0,
  shares_outstanding BIGINT NOT NULL,
  -- Output
  iv_per_share_low NUMERIC(12,2) NOT NULL,
  iv_per_share_high NUMERIC(12,2) NOT NULL,
  current_price NUMERIC(12,2),
  margin_of_safety_low NUMERIC(6,4),
  margin_of_safety_high NUMERIC(6,4),
  -- Metadata
  currency TEXT DEFAULT 'NTD',
  parameters_json JSONB,
  source_research_id TEXT,
  notes TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_hoe_ticker_year ON historical_owner_earnings (company_ticker, year);
CREATE INDEX IF NOT EXISTS idx_cf_ticker_period ON company_financials (ticker, period);
CREATE INDEX IF NOT EXISTS idx_ws_ticker_created ON watchlist_signals (ticker, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_iv_ticker_date ON iv_calculations (ticker, calculated_at DESC);
```

**Step 3: Verify SQL syntax**

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco && python3 -c "open('supabase/migrations/001_core_tables.sql').read(); print('SQL file readable')"`
Expected: `SQL file readable`

**Step 4: Commit**

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add supabase/migrations/001_core_tables.sql
git commit -m "feat(supabase): add 4 core tables for IVCO data layer

Tables: historical_owner_earnings, company_financials,
watchlist_signals, iv_calculations. These store Python CLI output
separately from Payload CMS's own tables.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

> **Note for executor:** This migration will be applied to Supabase when database connection is configured. For now it serves as the schema definition.

---

## Task 5: Python CLI — ivco-fetch (Financial Data Fetcher)

**Files:**
- Create: `cli/ivco-calc/src/ivco_calc/fetchers/__init__.py`
- Create: `cli/ivco-calc/src/ivco_calc/fetchers/base.py`
- Create: `cli/ivco-calc/src/ivco_calc/fetchers/fmp.py`
- Create: `cli/ivco-calc/tests/test_fetch.py`
- Modify: `cli/ivco-calc/src/ivco_calc/cli.py`
- Modify: `cli/ivco-calc/pyproject.toml`

### Step 1: Write the failing test

Create `cli/ivco-calc/tests/test_fetch.py`:

```python
"""Test ivco-fetch financial data fetcher."""
import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from ivco_calc.cli import cli
from ivco_calc.fetchers.fmp import FMPFetcher


def test_fmp_fetcher_parse_income_statement():
    """FMP API response parsing produces correct OE inputs."""
    raw = {
        "symbol": "TSM",
        "date": "2022-12-31",
        "period": "FY",
        "netIncome": 1016900515000,
        "depreciationAndAmortization": 437254273000,
        "capitalExpenditure": -1075620698000,
        "revenue": 2263891000000,
        "grossProfit": 1370280000000,
        "totalDebt": 710000000000,
        "sharesOutstanding": 25930380000,
    }
    fetcher = FMPFetcher(api_key="test_key")
    parsed = fetcher.parse_income_statement(raw)
    assert parsed["ticker"] == "TSM"
    assert parsed["year"] == 2022
    assert parsed["net_income"] == 1016900515000
    assert parsed["capex"] == 1075620698000  # positive
    assert parsed["depreciation"] > 0


def test_fmp_fetcher_build_url():
    """FMP API URL is correctly constructed."""
    fetcher = FMPFetcher(api_key="demo_key")
    url = fetcher.build_url("TSM", "income-statement", limit=10)
    assert "financialmodelingprep.com" in url
    assert "TSM" in url
    assert "apikey=demo_key" in url
    assert "limit=10" in url


def test_fetch_cli_requires_ticker():
    """CLI fetch command requires --ticker."""
    runner = CliRunner()
    result = runner.invoke(cli, ["fetch", "--years", "5"])
    assert result.exit_code != 0
    assert "Missing" in result.output or "required" in result.output.lower()
```

### Step 2: Run tests to verify they fail

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/test_fetch.py -v`
Expected: FAIL (modules not yet created)

### Step 3: Create fetcher base interface

Create `cli/ivco-calc/src/ivco_calc/fetchers/__init__.py`:

```python
"""Financial data fetchers for IVCO."""
```

Create `cli/ivco-calc/src/ivco_calc/fetchers/base.py`:

```python
"""Abstract base for financial data fetchers."""
from abc import ABC, abstractmethod


class BaseFetcher(ABC):
    """Interface for financial data sources."""

    @abstractmethod
    def fetch_income_statements(self, ticker: str, limit: int = 10) -> list[dict]:
        """Fetch income statement data. Returns list of parsed dicts."""
        ...

    @abstractmethod
    def fetch_balance_sheet(self, ticker: str, limit: int = 10) -> list[dict]:
        """Fetch balance sheet data. Returns list of parsed dicts."""
        ...

    @abstractmethod
    def fetch_quote(self, ticker: str) -> dict:
        """Fetch current price quote. Returns dict with price, pe, market_cap."""
        ...
```

### Step 4: Implement FMP fetcher

Create `cli/ivco-calc/src/ivco_calc/fetchers/fmp.py`:

```python
"""Financial Modeling Prep (FMP) API fetcher — free tier."""
import os
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
from ivco_calc.fetchers.base import BaseFetcher


class FMPFetcher(BaseFetcher):
    """FMP API v3 client. Free tier: 250 requests/day."""

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("FMP_API_KEY", "")
        if not self.api_key:
            raise ValueError("FMP_API_KEY not set. Get free key at financialmodelingprep.com")

    def build_url(self, ticker: str, endpoint: str, limit: int = 10) -> str:
        return f"{self.BASE_URL}/{endpoint}/{ticker}?limit={limit}&apikey={self.api_key}"

    def _get_json(self, url: str) -> list | dict:
        req = Request(url, headers={"User-Agent": "IVCO-CLI/0.2.0"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def parse_income_statement(self, raw: dict) -> dict:
        """Parse FMP income statement into IVCO format."""
        date_str = raw.get("date", "")
        year = int(date_str[:4]) if date_str else 0
        capex_raw = raw.get("capitalExpenditure", 0)
        capex = abs(capex_raw) if capex_raw else 0
        da = raw.get("depreciationAndAmortization", 0) or 0
        return {
            "ticker": raw.get("symbol", ""),
            "year": year,
            "period": raw.get("period", "FY"),
            "net_income": raw.get("netIncome", 0) or 0,
            "depreciation": da,
            "amortization": 0,  # FMP combines D&A; split if needed
            "capex": capex,
            "revenue": raw.get("revenue", 0) or 0,
            "gross_profit": raw.get("grossProfit", 0) or 0,
        }

    def fetch_income_statements(self, ticker: str, limit: int = 10) -> list[dict]:
        url = self.build_url(ticker, "income-statement", limit)
        raw_list = self._get_json(url)
        if not isinstance(raw_list, list):
            return []
        return [self.parse_income_statement(r) for r in raw_list]

    def fetch_balance_sheet(self, ticker: str, limit: int = 10) -> list[dict]:
        url = self.build_url(ticker, "balance-sheet-statement", limit)
        raw_list = self._get_json(url)
        if not isinstance(raw_list, list):
            return []
        return [
            {
                "ticker": r.get("symbol", ""),
                "year": int(r.get("date", "0000")[:4]),
                "total_debt": r.get("totalDebt", 0) or 0,
                "total_assets": r.get("totalAssets", 0) or 0,
                "shares_outstanding": r.get("commonStockSharesOutstanding", 0) or 0,
            }
            for r in raw_list
        ]

    def fetch_quote(self, ticker: str) -> dict:
        url = f"{self.BASE_URL}/quote/{ticker}?apikey={self.api_key}"
        data = self._get_json(url)
        if isinstance(data, list) and data:
            q = data[0]
            return {
                "ticker": q.get("symbol", ticker),
                "price": q.get("price", 0),
                "pe": q.get("pe", 0),
                "market_cap": q.get("marketCap", 0),
                "change_pct": q.get("changesPercentage", 0),
            }
        return {"ticker": ticker, "price": 0, "pe": 0, "market_cap": 0, "change_pct": 0}
```

### Step 5: Add fetch command to CLI

Add to `cli/ivco-calc/src/ivco_calc/cli.py`, after existing commands:

```python
@cli.command("fetch")
@click.option("--ticker", type=str, required=True, help="Stock ticker (e.g. TSM, AAPL)")
@click.option("--years", type=int, default=10, help="Number of years to fetch")
@click.option("--source", type=click.Choice(["fmp"]), default="fmp", help="Data source")
def fetch_cmd(ticker, years, source):
    """Fetch financial data from external API."""
    from ivco_calc.fetchers.fmp import FMPFetcher
    fetcher = FMPFetcher()
    income = fetcher.fetch_income_statements(ticker, limit=years)
    balance = fetcher.fetch_balance_sheet(ticker, limit=years)
    quote = fetcher.fetch_quote(ticker)
    output_json({
        "ticker": ticker,
        "source": source,
        "income_statements": income,
        "balance_sheet": balance,
        "quote": quote,
    })
```

### Step 6: Add `requests` is NOT needed — we use urllib (stdlib). Update pyproject.toml only if needed

No dependency changes needed — FMP fetcher uses stdlib `urllib`. Keep dependencies minimal.

### Step 7: Run tests to verify they pass

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/test_fetch.py -v`
Expected: 3 PASS

### Step 8: Run all existing tests to confirm no regressions

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/ -v`
Expected: All 11 existing + 3 new = 14 PASS

### Step 9: Commit

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cli/ivco-calc/src/ivco_calc/fetchers/ cli/ivco-calc/src/ivco_calc/cli.py cli/ivco-calc/tests/test_fetch.py
git commit -m "feat(cli): add ivco fetch — FMP API financial data fetcher

Layer 1 primitive: fetch income statements, balance sheets, and
current quotes from Financial Modeling Prep free tier API.
Stdlib urllib only, no new dependencies.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: Python CLI — ivco-analyze (One-Stop Analysis)

**Files:**
- Create: `cli/ivco-calc/tests/test_analyze.py`
- Modify: `cli/ivco-calc/src/ivco_calc/cli.py`

### Step 1: Write the failing test

Create `cli/ivco-calc/tests/test_analyze.py`:

```python
"""Test ivco-analyze one-stop analysis pipeline."""
import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from ivco_calc.cli import cli


def test_analyze_cli_requires_ticker():
    """CLI analyze command requires --ticker."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze"])
    assert result.exit_code != 0


def test_analyze_cli_help():
    """CLI analyze command has help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "ticker" in result.output.lower()
    assert "maintenance" in result.output.lower()
```

### Step 2: Run test to verify it fails

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/test_analyze.py -v`
Expected: FAIL

### Step 3: Implement analyze command

Add to `cli/ivco-calc/src/ivco_calc/cli.py`:

```python
@cli.command("analyze")
@click.option("--ticker", type=str, required=True, help="Stock ticker (e.g. TSM)")
@click.option("--years", type=int, default=10, help="Years of history to fetch")
@click.option("--maintenance-ratio", type=float, required=True, help="Maintenance CapEx ratio (e.g. 0.20)")
@click.option("--cc-low", type=float, required=True, help="Confidence Coefficient lower bound")
@click.option("--cc-high", type=float, required=True, help="Confidence Coefficient upper bound")
@click.option("--stage2-cagr", type=float, default=0.15, help="Stage 2 CAGR (default 15%%)")
@click.option("--stage3-cagr", type=float, default=0.05, help="Stage 3 perpetual growth (default 5%%)")
@click.option("--discount-rate", type=float, default=0.08, help="Discount rate (default 8%%)")
@click.option("--long-term-debt", type=int, default=0, help="Long-term debt")
@click.option("--share-par-value", type=int, default=10, help="Share par value")
@click.option("--source", type=click.Choice(["fmp"]), default="fmp")
def analyze_cmd(ticker, years, maintenance_ratio, cc_low, cc_high,
                stage2_cagr, stage3_cagr, discount_rate, long_term_debt,
                share_par_value, source):
    """One-stop analysis: fetch → calc-oe → calc-cagr → calc-iv."""
    from ivco_calc.fetchers.fmp import FMPFetcher

    # Step 1: Fetch
    fetcher = FMPFetcher()
    income = fetcher.fetch_income_statements(ticker, limit=years)
    balance = fetcher.fetch_balance_sheet(ticker, limit=years)
    quote = fetcher.fetch_quote(ticker)

    if not income:
        click.echo(json.dumps({"error": f"No income data found for {ticker}"}))
        raise SystemExit(1)

    # Step 2: Calculate OE for each year
    oe_series = []
    for stmt in sorted(income, key=lambda x: x["year"]):
        oe = calc_owner_earnings(
            net_income=stmt["net_income"],
            depreciation=stmt["depreciation"],
            amortization=stmt["amortization"],
            capex=stmt["capex"],
            maintenance_capex_ratio=maintenance_ratio,
        )
        oe_series.append({"year": stmt["year"], "oe": oe})

    # Step 3: Calculate CAGR
    if len(oe_series) >= 2:
        cagr_result = calc_cagr(oe_series=oe_series, reality_coefficients={})
    else:
        cagr_result = {"cagr": 0, "years": 0}

    # Step 4: Calculate IV
    latest_oe = oe_series[-1]["oe"] if oe_series else 0
    shares = 0
    for bs in balance:
        if bs.get("shares_outstanding"):
            shares = bs["shares_outstanding"]
            break

    if latest_oe > 0 and shares > 0 and cagr_result.get("cagr", 0) > 0:
        iv_result = calc_three_stage_dcf(
            latest_oe=latest_oe,
            cagr=cagr_result["cagr"],
            cc_low=cc_low,
            cc_high=cc_high,
            stage2_cagr=stage2_cagr,
            stage3_cagr=stage3_cagr,
            discount_rate=discount_rate,
            long_term_debt=long_term_debt,
            shares_outstanding_raw=shares,
            share_par_value=share_par_value,
        )
    else:
        iv_result = {"error": "Insufficient data for IV calculation"}

    output_json({
        "ticker": ticker,
        "analysis": {
            "oe_series": oe_series,
            "cagr": cagr_result,
            "iv": iv_result,
            "current_price": quote.get("price", 0),
            "pe_ratio": quote.get("pe", 0),
        },
        "parameters": {
            "maintenance_ratio": maintenance_ratio,
            "cc_low": cc_low,
            "cc_high": cc_high,
            "stage2_cagr": stage2_cagr,
            "stage3_cagr": stage3_cagr,
            "discount_rate": discount_rate,
        },
    })
```

### Step 4: Run tests to verify they pass

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/test_analyze.py -v`
Expected: 2 PASS

### Step 5: Run all tests

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/ -v`
Expected: All PASS (14 + 2 = 16)

### Step 6: Commit

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cli/ivco-calc/src/ivco_calc/cli.py cli/ivco-calc/tests/test_analyze.py
git commit -m "feat(cli): add ivco analyze — one-stop fetch+calc pipeline

Layer 2 composed tool: fetches financial data, calculates OE series,
derives CAGR, runs Three-Stage DCF, outputs IV range with current
price for margin of safety assessment.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: Agent DNA Files (Deep Value Council Foundation)

**Files:**
- Create: `config/agents/shared/allen-framework.md`
- Create: `config/agents/shared/evaluation-criteria.md`
- Create: `config/agents/shared/good-price-logic.md`
- Create: `config/agents/macro-strategist.md`
- Create: `config/agents/supply-chain-detective.md`
- Create: `config/agents/the-skeptic.md`
- Create: `config/agents/consensus-chairman.md`

### Step 1: Create directory structure

```bash
mkdir -p /Users/allenchenmac/fisher/projects/allen-ivco/config/agents/shared
```

### Step 2: Create shared Allen Framework DNA

Create `config/agents/shared/allen-framework.md`:

```markdown
# Allen Framework — Shared Agent DNA

> Every IVCO agent must internalize this framework. It is the mathematical and philosophical core.

## The Four Masters

| Master | Contribution | IVCO Application |
|--------|-------------|------------------|
| **Graham** | Facts and scientific evaluation as foundation | Historical financials are the gate — no speculation without data |
| **Buffett** | Owner Earnings as the true measure of value | OE = Net Income + D&A - Maintenance CapEx (not net income, not FCF) |
| **Fisher** | Management integrity and growth capacity | Commitment tracking, say-do ratio, new product pipeline |
| **Munger** | Inversion and multidisciplinary thinking | "Why will this fail?" comes before "Why will this succeed?" |

## Three-Tier Calibration Pipeline

```
Layer 1: OE_calibrated = OE × Reality_Coefficient
Layer 2: CAGR = f(OE_calibrated series, 7-10 years)
Layer 3: CAGR_adjusted = CAGR × Confidence_Coefficient
```

## Three-Stage DCF

- **Stage 1 (Years 1-5):** CAGR_adjusted growth, year-by-year discounting
- **Stage 2 (Years 6-10):** Moderate growth (company-specific conservative assumption)
- **Stage 3 (Terminal):** Perpetual growth rate, discounted to present

```
IV = (Stage_1_PV + Stage_2_PV + Stage_3_PV - Long_Term_Debt) / Shares_Outstanding
```

**Discount Rate** = US 10-Year Treasury Yield + ~3% long-term inflation (dynamic, NOT fixed 8%)

## Seven Company-Specific Parameters

1. Maintenance CapEx Ratio (e.g. TSMC = 0.20)
2. Reality Coefficient (historical OE correction)
3. Confidence Coefficient Lower Bound
4. Confidence Coefficient Upper Bound
5. Stage 2 CAGR
6. Stage 3 Perpetual Growth Rate
7. Long-Term Debt

## Confidence Coefficient Grading

| Grade | CC Range | Condition | Evidence Required |
|-------|----------|-----------|-------------------|
| Conservative | 0.8x-1.0x | Integrity issues or competitive threats | Basic financials |
| Steady | 1.0x-1.5x | 100% integrity + stable-to-strong expansion | Commitment tracking + capacity verification |
| Aggressive | 1.5x-2.5x | Major expansion + tech leadership | CapEx timeline + supply chain verification |
| Extreme | 2.5x+ | 3x capacity expansion + hidden champion | Annual report + 100% execution + written thesis |
| Terminate | N/A | Integrity breach | One-strike rule, analysis stops |

## CLI Tools Available

- `ivco calc-oe` — Calculate Owner Earnings
- `ivco calc-cagr` — Calculate CAGR with Reality Coefficients
- `ivco calc-iv` — Three-Stage DCF → IV Range
- `ivco fetch` — Fetch financial data from FMP API
- `ivco analyze` — One-stop: fetch → calc-oe → calc-cagr → calc-iv
- `ivco verify` — Cross-validate against expected values
```

### Step 3: Create evaluation criteria DNA

Create `config/agents/shared/evaluation-criteria.md`:

```markdown
# Evaluation Criteria — What Makes a Good Company

> Shared criteria for all IVCO agents when assessing companies.

## Moat Assessment (Munger's Durable Competitive Advantage)

- **Switching costs**: How painful is it for customers to switch?
- **Network effects**: Does the product get better with more users?
- **Cost advantages**: Structural cost edge (scale, location, process)?
- **Intangible assets**: Patents, brands, regulatory licenses?
- **Efficient scale**: Market too small for a second player?

## Management Quality (Fisher's Scuttlebutt)

- **Say-Do Ratio**: Compare 3-5 years of guidance vs actual results
- **Capital allocation**: How does management deploy retained earnings?
- **Insider ownership**: Do executives own meaningful stock?
- **Succession planning**: Is the business dependent on one person?
- **Integrity gate**: Any accounting irregularities, related-party transactions, or governance red flags → Terminate

## Financial Health (Graham's Margin of Safety)

- **Gross margin > 35%**: Pricing power indicator
- **DSO < industry median**: Cash collection efficiency
- **DIO reasonable**: Inventory management
- **Debt/Equity manageable**: Not over-leveraged
- **FCF positive (or justified negative)**: Growing companies may have negative FCF if growth capex is justified

## Growth Verification (Buffett's Owner Earnings Growth)

- **Revenue CAGR**: Top-line momentum
- **OE CAGR > 15%**: Strong compounder threshold
- **CapEx as expansion signal**: 2-3x historical capex = major expansion
- **New market entry**: Geographic or product line expansion
- **R&D intensity**: Innovation pipeline health
```

### Step 4: Create good-price-logic DNA (self-correction protocol)

Create `config/agents/shared/good-price-logic.md`:

```markdown
# Good Price Logic — Self-Correction Protocol

> "Good companies are easy to find. Good PRICES are not." — Allen

## The Core Insight

Famous companies with strong moats (NVDA, TSMC, AAPL) often trade at premium valuations.
The market has already priced in their excellence. Finding them is step 1. Getting a good
price is the real challenge.

## Self-Correction Loop

### Trigger Conditions

After evaluating a batch of candidates, check:
1. Query P/E ratio and 52-week performance for each candidate
2. Calculate: what percentage have P/E > 30 OR 52-week gain > 50%?

### Decision Logic

```
IF >60% of candidates are "too expensive":
    TRIGGER: "Market has fully priced in. Go upstream."
    ACTION:  Identify Tier 1 suppliers of these companies
    FILTER:  Gross margin > 35%, DSO < industry median,
             not easily squeezed by second-source strategies
    RECURSE: Apply same evaluation to suppliers

IF Margin of Safety > 20% found:
    PROCEED to full Allen Framework analysis

IF still >60% too expensive after Tier 1:
    GO DEEPER: Tier 2 suppliers (suppliers of suppliers)
    APPLY same filters
    RECURSE until Margin of Safety > 20% found OR depth limit reached
```

### Depth Limit

- **Tier 0**: The famous companies themselves
- **Tier 1**: Direct suppliers (most hidden champions found here)
- **Tier 2**: Suppliers' suppliers (maximum depth for Phase 1)

### What Makes a Good Supplier Investment

1. **Not easily replaceable**: Technical moat, not just price competition
2. **Multiple large customers**: Not dependent on one buyer
3. **Gross margin > 35%**: Indicates pricing power and value-add
4. **Growing with the wave**: Benefits from same secular trend as famous companies
5. **Market hasn't noticed yet**: Lower P/E, less analyst coverage
```

### Step 5: Create role-specific DNA files

Create `config/agents/macro-strategist.md`:

```markdown
# Macro Strategist — Round 1 Agent

> DNA: Allen's macro thinking + Graham's fact-based foundation

## Role

You are the first analyst in the Deep Value Council. Your job is to identify structural
investment opportunities from macro events, news, and market shifts.

## Shared DNA

Read and internalize:
- `shared/allen-framework.md` — Core valuation methodology
- `shared/evaluation-criteria.md` — What makes a good company
- `shared/good-price-logic.md` — Self-correction protocol

## Your Specific Mission

Given a news article, macro event, or market development:

1. **Identify the structural change**: What is fundamentally shifting? (Not noise — structure)
2. **Map to sectors**: Which 2-3 sectors benefit most from this structural change?
3. **Name initial candidates**: For each sector, list 3-5 companies with the strongest competitive position
4. **Flag what to watch**: What data points would confirm or deny this thesis?

## Output Format

```json
{
  "structural_change": "description",
  "golden_sectors": ["sector_1", "sector_2", "sector_3"],
  "candidates": [
    {"name": "...", "ticker": "...", "sector": "...", "why": "..."}
  ],
  "watch_signals": ["signal_1", "signal_2"],
  "confidence": "low/medium/high",
  "reasoning": "..."
}
```

## Constraints

- Facts first. No speculation without data.
- Cite specific numbers when available (revenue growth, market share, etc.)
- If the macro event is noise (short-term, no structural impact), say so clearly.
- Do NOT evaluate price yet — that's for later rounds.
```

Create `config/agents/supply-chain-detective.md`:

```markdown
# Supply Chain Detective — Round 2 Agent

> DNA: Chi's engineering rigor + Fisher's scuttlebutt + recursive upstream search

## Role

You are the second analyst in the Deep Value Council. You receive a list of candidate
companies and dig into their supply chains to find hidden champions.

## Shared DNA

Read and internalize:
- `shared/allen-framework.md` — Core valuation methodology
- `shared/evaluation-criteria.md` — What makes a good company
- `shared/good-price-logic.md` — Self-correction protocol (you execute the upstream search)

## Your Specific Mission

Given a list of candidate companies:

1. **Map the supply chain**: For each candidate, identify key suppliers (Tier 1)
2. **Assess supplier quality**: Moat, margins, customer concentration, growth trajectory
3. **Find hidden champions**: Companies that benefit from the same wave but haven't been discovered
4. **Deduplicate**: Multiple candidates may share suppliers — consolidate the list
5. **Recursive search**: If triggered by good-price-logic, go to Tier 2 suppliers

## Tools Available

- `ivco search --query "ASML suppliers" --depth 2` — Supply chain research via Tavily
- `ivco fetch --ticker KLAC --years 10` — Financial data for any ticker

## Output Format

```json
{
  "tier_1_suppliers": [
    {"name": "...", "ticker": "...", "supplies_to": ["..."], "moat": "...", "gross_margin": "..."}
  ],
  "tier_2_suppliers": [],
  "hidden_champions": [
    {"name": "...", "ticker": "...", "why_hidden": "...", "catalyst": "..."}
  ],
  "deduplicated_total": 0
}
```

## Constraints

- Engineering rigor: verify claims with financial data, not just narratives
- Fisher's scuttlebutt: look for management quality signals (insider buying, consistent guidance)
- Flag any company with customer concentration > 40% as a risk
```

Create `config/agents/the-skeptic.md`:

```markdown
# The Skeptic — Round 3 Agent

> DNA: Munger's inversion + Jane's Devil's Advocate DNA + one-strike integrity rule

## Role

You are the third analyst in the Deep Value Council. Your sole job is to find reasons
why each investment will FAIL. You are the quality gate.

## Shared DNA

Read and internalize:
- `shared/allen-framework.md` — Core valuation methodology
- `shared/evaluation-criteria.md` — What makes a good company
- `shared/good-price-logic.md` — Self-correction protocol (you trigger it when too expensive)

## Your Specific Mission

Given the combined candidate list from Rounds 1-2:

1. **Inversion test**: For each company, list 3 ways this investment could lose money
2. **Integrity gate**: Any management integrity issue → TERMINATE analysis for that company
3. **Price check**: Is the current price justified? Calculate rough Margin of Safety
4. **Too-expensive trigger**: If >60% of candidates have P/E > 30, trigger self-correction loop
5. **Survivor list**: Companies that pass all filters, ranked by conviction

## Tools Available

- `ivco fetch --ticker TSM --years 10` — Get financial data
- `ivco calc-oe` — Calculate Owner Earnings
- `ivco calc-iv` — Three-Stage DCF for IV Range

## Output Format

```json
{
  "survivors": [
    {"ticker": "...", "conviction": "high/medium/low", "iv_range": "...", "current_price": "...", "margin_of_safety": "..."}
  ],
  "eliminated": [
    {"ticker": "...", "reason": "..."}
  ],
  "too_expensive_pct": 0.0,
  "trigger_upstream": false,
  "risk_warnings": ["..."]
}
```

## Constraints

- Always lead with risks. "Why will this fail?" before "Why will this succeed?"
- One-strike integrity rule: any accounting fraud, related-party abuse, or governance violation → Terminate
- Be honest about uncertainty. "I don't know" is better than fabricated confidence.
- Jane's voice: direct, no sugar-coating, data-driven skepticism
```

Create `config/agents/consensus-chairman.md`:

```markdown
# Consensus Chairman — Round 4 Agent

> DNA: Allen Framework Complete — Three-Tier Calibration + Three-Stage DCF + Final Verdict

## Role

You are the final analyst in the Deep Value Council. You synthesize all previous rounds
into a definitive research output with Allen Framework math.

## Shared DNA

Read and internalize:
- `shared/allen-framework.md` — Core valuation methodology (YOU execute the full math)
- `shared/evaluation-criteria.md` — What makes a good company
- `shared/good-price-logic.md` — Self-correction protocol

## Your Specific Mission

Given the survivor list from Round 3:

1. **Full Allen Framework analysis** for each survivor:
   - Calculate OE series (7-10 years)
   - Apply Reality Coefficients
   - Derive CAGR
   - Assign Confidence Coefficient range with justification
   - Run Three-Stage DCF → IV Range per share
2. **Rank by conviction**: Margin of Safety + Quality Score
3. **Generate triple output**: Research report + data record + blog draft outline
4. **Action items**: What to monitor, when to re-evaluate, entry price targets

## Tools Available

- `ivco analyze --ticker TSM --maintenance-ratio 0.20 --cc-low 1.2 --cc-high 1.5`
- `ivco verify --computed-low 4565 --computed-high 5639 --expected-low 4565 --expected-high 5639`

## Output Format

```json
{
  "final_list": [
    {
      "ticker": "...",
      "name": "...",
      "iv_per_share_low": 0,
      "iv_per_share_high": 0,
      "current_price": 0,
      "margin_of_safety": "...",
      "conviction": "high/medium/low",
      "cc_range": "...",
      "cc_justification": "...",
      "key_risks": ["..."],
      "action": "buy/watch/pass"
    }
  ],
  "research_summary": "...",
  "blog_outline": {
    "title": "...",
    "key_findings": ["..."],
    "faq": [{"q": "...", "a": "..."}]
  }
}
```

## Constraints

- Every IV number must come from the Three-Stage DCF, not rough multiples
- CC assignment must cite specific evidence (capex plans, say-do ratio, market position)
- Output must include per-share values — Allen doesn't buy by market cap
- The research summary should be writeable as a Fisher-voice blog article
```

### Step 6: Commit

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add config/agents/
git commit -m "feat(agents): add Deep Value Council DNA — 4 roles + 3 shared

Foundation for IVCO's research engine. Each agent has Allen Framework
math, evaluation criteria, and good-price self-correction logic
embedded in their DNA. Roles: Macro Strategist, Supply Chain Detective,
The Skeptic, Consensus Chairman.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: Tool Ecosystem Skeleton (--list-tools, --help)

**Files:**
- Create: `cli/ivco-calc/src/ivco_calc/tools_registry.py`
- Create: `cli/ivco-calc/tests/test_tools_registry.py`
- Modify: `cli/ivco-calc/src/ivco_calc/cli.py`

### Step 1: Write the failing test

Create `cli/ivco-calc/tests/test_tools_registry.py`:

```python
"""Test tool ecosystem discovery."""
from click.testing import CliRunner
from ivco_calc.cli import cli
from ivco_calc.tools_registry import list_tools, get_tool_info


def test_list_tools_returns_all():
    """list_tools returns all registered tools."""
    tools = list_tools()
    assert len(tools) >= 6  # calc-oe, calc-cagr, calc-iv, verify, fetch, analyze
    names = [t["name"] for t in tools]
    assert "calc-oe" in names
    assert "fetch" in names
    assert "analyze" in names


def test_get_tool_info():
    """get_tool_info returns details for a specific tool."""
    info = get_tool_info("calc-oe")
    assert info is not None
    assert info["name"] == "calc-oe"
    assert "layer" in info
    assert "description" in info


def test_get_tool_info_not_found():
    """get_tool_info returns None for unknown tool."""
    info = get_tool_info("nonexistent")
    assert info is None


def test_list_tools_cli():
    """CLI list-tools command outputs JSON."""
    runner = CliRunner()
    result = runner.invoke(cli, ["list-tools"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) >= 6
```

### Step 2: Run test to verify it fails

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/test_tools_registry.py -v`
Expected: FAIL

### Step 3: Create tools registry

Create `cli/ivco-calc/src/ivco_calc/tools_registry.py`:

```python
"""IVCO Tool Ecosystem Registry — agent-discoverable tool catalog."""

TOOLS = [
    # Layer 1: Core Primitives
    {
        "name": "calc-oe",
        "layer": 1,
        "layer_name": "primitive",
        "description": "Calculate Owner Earnings for a single year",
        "usage": "ivco calc-oe --net-income N --depreciation N --amortization N --capex N --maintenance-ratio F",
        "input": "Financial statement values + maintenance ratio",
        "output": "JSON with owner_earnings value",
    },
    {
        "name": "calc-cagr",
        "layer": 1,
        "layer_name": "primitive",
        "description": "Calculate CAGR from OE series with Reality Coefficients",
        "usage": "ivco calc-cagr --start-oe N --end-oe N --start-year Y --end-year Y",
        "input": "OE start/end values + years + optional reality coefficients",
        "output": "JSON with cagr, years, calibrated values",
    },
    {
        "name": "calc-iv",
        "layer": 1,
        "layer_name": "primitive",
        "description": "Calculate Intrinsic Value using Three-Stage DCF",
        "usage": "ivco calc-iv --latest-oe N --cagr F --cc-low F --cc-high F --stage2-cagr F --stage3-cagr F --discount-rate F --long-term-debt N --shares-outstanding N",
        "input": "OE + CAGR + 7 Allen Framework parameters",
        "output": "JSON with iv_per_share_low, iv_per_share_high",
    },
    {
        "name": "verify",
        "layer": 1,
        "layer_name": "primitive",
        "description": "Cross-validate computed IV against expected values",
        "usage": "ivco verify --computed-low N --computed-high N --expected-low N --expected-high N",
        "input": "Computed and expected IV ranges",
        "output": "JSON with status PASS/FAIL + deviations",
    },
    {
        "name": "fetch",
        "layer": 1,
        "layer_name": "primitive",
        "description": "Fetch financial data from external API (FMP free tier)",
        "usage": "ivco fetch --ticker TSM --years 10 --source fmp",
        "input": "Ticker symbol + years",
        "output": "JSON with income_statements, balance_sheet, quote",
    },
    # Layer 2: Composed Tools
    {
        "name": "analyze",
        "layer": 2,
        "layer_name": "composed",
        "description": "One-stop analysis: fetch → calc-oe → calc-cagr → calc-iv",
        "usage": "ivco analyze --ticker TSM --maintenance-ratio 0.20 --cc-low 1.2 --cc-high 1.5",
        "input": "Ticker + Allen Framework parameters",
        "output": "JSON with full OE series, CAGR, IV range, current price",
        "composes": ["fetch", "calc-oe", "calc-cagr", "calc-iv"],
    },
]


def list_tools() -> list[dict]:
    """Return all registered tools."""
    return TOOLS


def get_tool_info(name: str) -> dict | None:
    """Return info for a specific tool, or None if not found."""
    for tool in TOOLS:
        if tool["name"] == name:
            return tool
    return None
```

### Step 4: Add list-tools command to CLI

Add to `cli/ivco-calc/src/ivco_calc/cli.py`:

```python
from ivco_calc.tools_registry import list_tools, get_tool_info

@cli.command("list-tools")
@click.option("--layer", type=int, help="Filter by layer (1=primitive, 2=composed, 3=agent)")
def list_tools_cmd(layer):
    """Discover all available IVCO tools (agent-discoverable)."""
    tools = list_tools()
    if layer is not None:
        tools = [t for t in tools if t["layer"] == layer]
    output_json(tools)

@cli.command("tool-info")
@click.argument("name")
def tool_info_cmd(name):
    """Get detailed info about a specific tool."""
    info = get_tool_info(name)
    if info is None:
        click.echo(json.dumps({"error": f"Tool '{name}' not found. Use 'ivco list-tools' to see available tools."}))
        raise SystemExit(1)
    output_json(info)
```

### Step 5: Run tests

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/test_tools_registry.py -v`
Expected: 4 PASS

### Step 6: Run all tests

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/ -v`
Expected: All PASS (16 + 4 = 20)

### Step 7: Commit

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cli/ivco-calc/src/ivco_calc/tools_registry.py cli/ivco-calc/src/ivco_calc/cli.py cli/ivco-calc/tests/test_tools_registry.py
git commit -m "feat(cli): add tool ecosystem skeleton — list-tools + tool-info

OpenClaw-inspired agent-discoverable tool catalog. Agents can query
available tools, filter by layer, and get usage instructions.
Foundation for self-evolving tool ecosystem.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 9: JSON-LD Structured Data Generator

> Allen directive: "Payload CMS afterRead hook 或 Next.js head component 自動從這些欄位生成 JSON-LD"

**Files:**
- Create: `cms/src/lib/structured-data.ts`
- Create: `cms/src/lib/__tests__/structured-data.test.ts`

### Step 1: Write the failing test

Create `cms/src/lib/__tests__/structured-data.test.ts`:

```typescript
import { describe, it, expect } from 'vitest'
import { generateArticleSchema, generateFAQSchema } from '../structured-data'

describe('generateArticleSchema', () => {
  it('generates valid Article JSON-LD', () => {
    const schema = generateArticleSchema({
      title: 'Allen Framework vs Buffett Owner Earnings',
      description: 'How the Allen Framework extends Buffett\'s 1986 Owner Earnings formula',
      slug: 'allen-framework-vs-buffett-owner-earnings-1986',
      author: 'IVCO Fisher',
      authorBio: 'Studies businesses, not markets.',
      publishedAt: '2026-02-14T00:00:00Z',
      ogImageUrl: 'https://ivco.io/media/og-allen-framework.jpg',
    })
    expect(schema['@type']).toBe('Article')
    expect(schema.headline).toBe('Allen Framework vs Buffett Owner Earnings')
    expect(schema.author.name).toBe('IVCO Fisher')
    expect(schema.publisher.name).toBe('IVCO')
  })
})

describe('generateFAQSchema', () => {
  it('generates valid FAQPage JSON-LD', () => {
    const schema = generateFAQSchema([
      { question: 'What is Owner Earnings?', answer: 'Buffett\'s formula for true cash flow.' },
      { question: 'Why not FCF?', answer: 'FCF penalizes growth capex.' },
      { question: 'How is maintenance capex estimated?', answer: 'Company-specific ratio.' },
    ])
    expect(schema['@type']).toBe('FAQPage')
    expect(schema.mainEntity).toHaveLength(3)
    expect(schema.mainEntity[0]['@type']).toBe('Question')
    expect(schema.mainEntity[0].acceptedAnswer['@type']).toBe('Answer')
  })
})
```

### Step 2: Run test to verify it fails

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cms && pnpm exec vitest run src/lib/__tests__/structured-data.test.ts`
Expected: FAIL (module not found)

### Step 3: Implement structured data generators

Create `cms/src/lib/structured-data.ts`:

```typescript
interface ArticleInput {
  title: string
  description: string
  slug: string
  author: string
  authorBio: string
  publishedAt: string
  modifiedAt?: string
  ogImageUrl: string
}

interface FAQItem {
  question: string
  answer: string
}

export function generateArticleSchema(input: ArticleInput) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: input.title,
    description: input.description,
    url: `https://ivco.io/${input.slug}`,
    image: input.ogImageUrl,
    datePublished: input.publishedAt,
    dateModified: input.modifiedAt || input.publishedAt,
    author: {
      '@type': 'Person',
      name: input.author,
      description: input.authorBio,
    },
    publisher: {
      '@type': 'Organization',
      name: 'IVCO',
      url: 'https://ivco.io',
    },
  }
}

export function generateFAQSchema(faqs: FAQItem[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  }
}

export function generateHowToSchema(title: string, steps: { name: string; text: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'HowTo',
    name: title,
    step: steps.map((s, i) => ({
      '@type': 'HowToStep',
      position: i + 1,
      name: s.name,
      text: s.text,
    })),
  }
}
```

### Step 4: Run test to verify it passes

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cms && pnpm exec vitest run src/lib/__tests__/structured-data.test.ts`
Expected: PASS

### Step 5: Commit

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cms/src/lib/structured-data.ts cms/src/lib/__tests__/structured-data.test.ts
git commit -m "feat(cms): add JSON-LD structured data generators

Article, FAQPage, and HowTo schema generators. Auto-generates from
Posts collection fields. Allen directive: structured data from CMS
fields, not hand-written JSON-LD.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 10: Update CLI Version + pyproject.toml

**Files:**
- Modify: `cli/ivco-calc/pyproject.toml`
- Modify: `cli/ivco-calc/src/ivco_calc/cli.py`

### Step 1: Bump version and ensure all imports work

Update `pyproject.toml` version to `0.2.0`.

Update `cli.py` version option to `0.2.0`.

### Step 2: Verify editable install works

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && pip install -e ".[dev]" && ivco --version`
Expected: `ivco, version 0.2.0`

### Step 3: Verify all commands accessible

Run: `ivco --help`
Expected: Shows calc-oe, calc-cagr, calc-iv, verify, fetch, analyze, list-tools, tool-info

### Step 4: Run full test suite

Run: `cd /Users/allenchenmac/fisher/projects/allen-ivco/cli/ivco-calc && python -m pytest tests/ -v --tb=short`
Expected: 20 tests PASS

### Step 5: Commit

```bash
cd /Users/allenchenmac/fisher/projects/allen-ivco
git add cli/ivco-calc/pyproject.toml cli/ivco-calc/src/ivco_calc/cli.py
git commit -m "chore(cli): bump version to 0.2.0 — fetch + analyze + tools ecosystem

New Layer 1 (fetch) + Layer 2 (analyze) + Meta (list-tools, tool-info).
20 tests passing.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Summary: Task Dependency Graph

```
Task 1: Authors Collection ──────┐
                                 ├──→ Task 2: Posts SEO Schema
Task 3: Companies upgrade ───────┤
                                 │
Task 4: Supabase migration ──────┤
                                 ├──→ Task 5: ivco-fetch ──→ Task 6: ivco-analyze
Task 7: Agent DNA files ─────────┤
                                 │
Task 8: Tool ecosystem ──────────┤
                                 │
Task 9: JSON-LD generators ──────┤
                                 │
Task 10: Version bump ───────────┘ (after all CLI tasks)
```

**Independent tasks (can run in parallel):** 1, 3, 4, 7
**Sequential chains:** 1→2, 5→6→10, 9 (after 2)

---

## Phase 0.5b Preview (Next Plan)

After this plan is complete, Phase 0.5b will cover:
- Deploy ivco.io to Vercel/Cloudflare
- Import 6 blog articles into Payload CMS
- Fix X Skill (restore intel pipeline)
- n8n 2-Agent MVP (Detective + Skeptic)
- ivco-search via Tavily API
- First real research pipeline test (Ray Dalio case study)
