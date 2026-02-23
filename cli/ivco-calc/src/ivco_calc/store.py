"""ivco-store — write analysis results to Supabase PostgreSQL.

Supports four data types:
  analysis: Full analyze output → historical_owner_earnings + iv_calculations + research_sessions
  oe:       Single OE calculation → historical_owner_earnings
  financial: Fetch output → company_financials
  signal:   Watchlist signal → watchlist_signals

Reads DATABASE_URL from environment. Uses psycopg2 for PostgreSQL.
"""
import json
import os
from datetime import datetime, timezone


def get_connection():
    """Get PostgreSQL connection from DATABASE_URL env var.

    Raises ImportError with install hint if psycopg2 is not available.
    """
    try:
        import psycopg2
    except ImportError:
        raise ImportError(
            "psycopg2 is not installed. Run: pip install ivco-calc[db]"
        )
    from ivco_calc.env_loader import ensure_var
    url = ensure_var("DATABASE_URL")
    return psycopg2.connect(url)


def store_oe(data: dict, ticker: str, year: int) -> dict:
    """Store a single Owner Earnings record."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        inputs = data.get("inputs", {})
        oe_val = data.get("owner_earnings", 0)
        cur.execute(
            """INSERT INTO historical_owner_earnings
               (company_ticker, year, net_income, depreciation, amortization,
                capex, maintenance_ratio, owner_earnings, currency, source)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (company_ticker, year) DO UPDATE SET
                 net_income = EXCLUDED.net_income,
                 depreciation = EXCLUDED.depreciation,
                 amortization = EXCLUDED.amortization,
                 capex = EXCLUDED.capex,
                 maintenance_ratio = EXCLUDED.maintenance_ratio,
                 owner_earnings = EXCLUDED.owner_earnings,
                 source = EXCLUDED.source
               RETURNING id""",
            (
                ticker, year,
                inputs.get("net_income", 0),
                inputs.get("depreciation", 0),
                inputs.get("amortization", 0),
                inputs.get("capex", 0),
                inputs.get("maintenance_capex_ratio", 0),
                oe_val,
                "USD",
                "ivco-calc",
            ),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "ok", "table": "historical_owner_earnings", "id": row_id}
    finally:
        conn.close()


def store_financial(data: dict) -> dict:
    """Store fetched financial data (income + balance sheet).

    Note: cash_flow data from `fetch` output is intentionally not persisted here.
    Cash flow fields (CapEx) are consumed during `analyze` for OE calculation.
    Full cash_flow persistence is planned for a future schema addition.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        ticker = data.get("ticker", "")
        stored = []

        for stmt in data.get("income_statements", []):
            period = f"{stmt.get('year', 0)}-FY"
            cur.execute(
                """INSERT INTO company_financials
                   (ticker, period, period_type, revenue, net_income,
                    currency, source_api)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (ticker, period, source_api) DO UPDATE SET
                     revenue = EXCLUDED.revenue,
                     net_income = EXCLUDED.net_income
                   RETURNING id""",
                (
                    ticker, period, "annual",
                    stmt.get("revenue", 0),
                    stmt.get("net_income", 0),
                    "USD",
                    data.get("source", "fmp"),
                ),
            )
            row_id = cur.fetchone()[0]
            stored.append({"table": "company_financials", "id": row_id, "period": period})

        for bs in data.get("balance_sheet", []):
            period = f"{bs.get('year', 0)}-FY"
            cur.execute(
                """UPDATE company_financials
                   SET total_debt = %s, total_assets = %s, shares_outstanding = %s
                   WHERE ticker = %s AND period = %s AND source_api = %s""",
                (
                    bs.get("total_debt", 0),
                    bs.get("total_assets", 0),
                    bs.get("shares_outstanding", 0),
                    ticker, period, data.get("source", "fmp"),
                ),
            )

        conn.commit()
        return {"status": "ok", "table": "company_financials", "rows": len(stored), "details": stored}
    finally:
        conn.close()


def store_signal(data: dict) -> dict:
    """Store a watchlist signal (X Intel, news, event)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO watchlist_signals
               (ticker, signal_type, headline, content, source, source_url, relevance_score)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                data.get("ticker"),
                data.get("signal_type", "news"),
                data.get("headline", ""),
                data.get("content"),
                data.get("source"),
                data.get("source_url"),
                data.get("relevance_score"),
            ),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "ok", "table": "watchlist_signals", "id": row_id}
    finally:
        conn.close()


def store_analysis(data: dict, *, initiated_by: str = "jane") -> dict:
    """Store full analyze pipeline output.

    Args:
        data: Full analyze JSON output (ticker, analysis, parameters).
        initiated_by: Who initiated this research session (for audit trail).

    Writes to three tables:
    1. historical_owner_earnings (one row per year)
    2. iv_calculations (one row with full DCF result)
    3. research_sessions (one row tracking the run)
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        ticker = data.get("ticker", "")
        analysis = data.get("analysis", {})
        params = data.get("parameters", {})

        # 1. Store OE series
        oe_ids = []
        for entry in analysis.get("oe_series", []):
            cur.execute(
                """INSERT INTO historical_owner_earnings
                   (company_ticker, year, net_income, depreciation, amortization,
                    capex, maintenance_ratio, owner_earnings, currency, source)
                   VALUES (%s, %s, 0, 0, 0, 0, %s, %s, %s, %s)
                   ON CONFLICT (company_ticker, year) DO UPDATE SET
                     maintenance_ratio = EXCLUDED.maintenance_ratio,
                     owner_earnings = EXCLUDED.owner_earnings,
                     source = EXCLUDED.source
                   RETURNING id""",
                (
                    ticker,
                    entry.get("year", 0),
                    params.get("maintenance_ratio", 0),
                    entry.get("oe", 0),
                    "USD",
                    "ivco-analyze",
                ),
            )
            oe_ids.append(cur.fetchone()[0])

        # 2. Store IV calculation
        iv = analysis.get("iv", {})
        cagr_data = analysis.get("cagr", {})
        iv_id = None
        if "iv_per_share_low" in iv:
            cur.execute(
                """INSERT INTO iv_calculations
                   (ticker, maintenance_ratio, reality_coefficient, historical_cagr,
                    cc_low, cc_high, stage1_cagr_low, stage1_cagr_high,
                    stage2_cagr, stage3_growth, discount_rate,
                    long_term_debt, shares_outstanding,
                    iv_per_share_low, iv_per_share_high,
                    current_price, currency, parameters_json)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                (
                    ticker,
                    params.get("maintenance_ratio", 0),
                    1.0,  # default reality coefficient
                    cagr_data.get("cagr", 0),
                    params.get("cc_low", 0),
                    params.get("cc_high", 0),
                    iv.get("stage1_cagr_low", 0),
                    iv.get("stage1_cagr_high", 0),
                    params.get("stage2_cagr", 0),
                    params.get("stage3_cagr", 0),
                    params.get("discount_rate", 0),
                    iv.get("long_term_debt", 0),
                    iv.get("shares_outstanding", 0),
                    iv.get("iv_per_share_low", 0),
                    iv.get("iv_per_share_high", 0),
                    analysis.get("current_price", 0),
                    "USD",
                    json.dumps(params),
                ),
            )
            iv_id = cur.fetchone()[0]

        # 3. Create research session
        now = datetime.now(timezone.utc)
        cur.execute(
            """INSERT INTO research_sessions
               (ticker, session_type, trigger_source, initiated_by,
                parameters, output_supabase_iv_id, status,
                started_at, completed_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                ticker,
                "full_analysis",
                "manual",
                initiated_by,
                json.dumps(params),
                iv_id,
                "completed",
                now,
                now,
            ),
        )
        session_id = cur.fetchone()[0]

        conn.commit()
        return {
            "status": "ok",
            "ticker": ticker,
            "stored": {
                "historical_owner_earnings": len(oe_ids),
                "iv_calculations": iv_id,
                "research_sessions": session_id,
            },
        }
    finally:
        conn.close()
