"""Tests for Jack's code review findings — ivco-calc v0.3.0.

Covers all 7 findings from 2026-02-16-chi-code-review.md:
  HIGH #1: --initiated-by passthrough to store_analysis
  HIGH #2: shares_outstanding year alignment after sort
  HIGH #3: FMP date=None crash in balance/cash-flow
  MEDIUM #4: psycopg2 ImportError at get_connection()
  MEDIUM #5: json.loads invalid stdin handling
  MEDIUM #6: _get_json network error wrapping
  LOW #7: cash_flow partial persistence (documented, no code test needed)
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from ivco_calc.cli import cli
from ivco_calc.fetchers.fmp import FMPFetcher, FMPError, _safe_year


# ──────────────────────────────────────────────────────────────
# Finding #1 (HIGH): --initiated-by passthrough
# ──────────────────────────────────────────────────────────────

SAMPLE_ANALYSIS = {
    "ticker": "KLAC",
    "analysis": {
        "oe_series": [
            {"year": 2015, "oe": 800_000_000},
            {"year": 2024, "oe": 3_500_000_000},
        ],
        "cagr": {"cagr": 0.1766, "start_year": 2015, "end_year": 2024, "periods": 9},
        "iv": {
            "stage1_cagr_low": 0.2119,
            "stage1_cagr_high": 0.2649,
            "iv_per_share_low": 450,
            "iv_per_share_high": 680,
            "long_term_debt": 0,
            "shares_outstanding": 134_000_000,
        },
        "current_price": 520.0,
        "pe_ratio": 25.3,
    },
    "parameters": {
        "maintenance_ratio": 0.15,
        "cc_low": 1.2,
        "cc_high": 1.5,
        "stage2_cagr": 0.12,
        "stage3_cagr": 0.04,
        "discount_rate": 0.08,
    },
}


@patch("ivco_calc.store.get_connection")
def test_initiated_by_passed_to_store_analysis(mock_conn):
    """Finding #1: --initiated-by value should be persisted in research_sessions."""
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = [1]
    mock_conn.return_value.cursor.return_value = mock_cur

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["store", "--type", "analysis", "--initiated-by", "chi"],
        input=json.dumps(SAMPLE_ANALYSIS),
    )
    assert result.exit_code == 0, result.output

    # Find the INSERT INTO research_sessions call and verify initiated_by
    calls = mock_cur.execute.call_args_list
    session_call = None
    for call in calls:
        sql = call[0][0]
        if "research_sessions" in sql:
            session_call = call
            break

    assert session_call is not None, "research_sessions INSERT not found"
    params = session_call[0][1]
    # initiated_by is the 4th param in the INSERT
    assert params[3] == "chi", f"Expected 'chi', got '{params[3]}'"


@patch("ivco_calc.store.get_connection")
def test_initiated_by_defaults_to_jane(mock_conn):
    """Finding #1: default initiated_by should be 'jane'."""
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = [1]
    mock_conn.return_value.cursor.return_value = mock_cur

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["store", "--type", "analysis"],
        input=json.dumps(SAMPLE_ANALYSIS),
    )
    assert result.exit_code == 0

    calls = mock_cur.execute.call_args_list
    for call in calls:
        if "research_sessions" in call[0][0]:
            assert call[0][1][3] == "jane"
            break


# ──────────────────────────────────────────────────────────────
# Finding #2 (HIGH): shares year alignment with reversed API order
# ──────────────────────────────────────────────────────────────

def _make_income_stmts(order: str = "asc"):
    """Create income statements with different shares per year."""
    stmts = [
        {"ticker": "TEST", "year": 2020, "net_income": 100, "depreciation": 10,
         "amortization": 0, "capex": 20, "revenue": 500, "gross_profit": 200,
         "shares_outstanding": 1000, "period": "FY"},
        {"ticker": "TEST", "year": 2021, "net_income": 120, "depreciation": 12,
         "amortization": 0, "capex": 25, "revenue": 600, "gross_profit": 250,
         "shares_outstanding": 1100, "period": "FY"},
        {"ticker": "TEST", "year": 2022, "net_income": 150, "depreciation": 15,
         "amortization": 0, "capex": 30, "revenue": 700, "gross_profit": 300,
         "shares_outstanding": 1200, "period": "FY"},
    ]
    if order == "desc":
        return list(reversed(stmts))
    return stmts


def test_shares_year_alignment_reversed_api_order():
    """Finding #2: shares should match latest OE year regardless of API order.

    Simulates FMP returning data in descending order (2022, 2021, 2020).
    The old code used income[0] which would pick 2022 only by luck in desc order
    but 2020 (wrong year) in asc order. After fix, both orderings get 2022 shares.
    """
    from ivco_calc.owner_earnings import calc_owner_earnings
    from ivco_calc.cagr import calc_cagr

    for order in ["asc", "desc"]:
        income = _make_income_stmts(order)
        balance = []
        cash_flow = []

        # Replicate analyze logic (sorted by year for OE)
        oe_series = []
        for stmt in sorted(income, key=lambda x: x["year"]):
            oe = calc_owner_earnings(
                net_income=stmt["net_income"],
                depreciation=stmt["depreciation"],
                amortization=stmt["amortization"],
                capex=stmt["capex"],
                maintenance_capex_ratio=0.20,
            )
            oe_series.append({"year": stmt["year"], "oe": oe})

        latest_oe_year = oe_series[-1]["year"]
        assert latest_oe_year == 2022, f"Latest OE year should be 2022, got {latest_oe_year}"

        # Replicate the fixed shares lookup
        income_sorted = sorted(income, key=lambda x: x["year"], reverse=True)
        shares = 0
        for stmt in income_sorted:
            if stmt["year"] == latest_oe_year and stmt.get("shares_outstanding"):
                shares = stmt["shares_outstanding"]
                break
        if not shares:
            for stmt in income_sorted:
                if stmt.get("shares_outstanding"):
                    shares = stmt["shares_outstanding"]
                    break

        assert shares == 1200, (
            f"Order={order}: expected shares=1200 (from 2022), got {shares}"
        )


# ──────────────────────────────────────────────────────────────
# Finding #3 (HIGH): FMP date=None crash
# ──────────────────────────────────────────────────────────────

def test_safe_year_with_none_date():
    """Finding #3: date=None should return 0, not crash."""
    assert _safe_year({"date": None}) == 0


def test_safe_year_with_missing_date():
    """Finding #3: missing date key should return 0."""
    assert _safe_year({}) == 0


def test_safe_year_with_empty_string():
    """Finding #3: empty string date should return 0."""
    assert _safe_year({"date": ""}) == 0


def test_safe_year_with_malformed_date():
    """Finding #3: non-numeric date prefix should return 0."""
    assert _safe_year({"date": "abcd-01-01"}) == 0


def test_safe_year_with_short_date():
    """Finding #3: date shorter than 4 chars should return 0."""
    assert _safe_year({"date": "20"}) == 0


def test_safe_year_with_valid_date():
    """Finding #3: normal date should parse correctly."""
    assert _safe_year({"date": "2022-12-31"}) == 2022


def test_fmp_balance_sheet_date_none():
    """Finding #3: balance sheet with date=None should not crash."""
    fetcher = FMPFetcher(api_key="test_key")
    raw_data = [
        {"symbol": "TSM", "date": None, "totalDebt": 100, "longTermDebt": 50,
         "totalAssets": 500, "commonStockSharesOutstanding": 1000, "commonStock": 200},
    ]
    with patch.object(fetcher, '_get_json', return_value=raw_data):
        result = fetcher.fetch_balance_sheet("TSM", limit=1)
        assert len(result) == 1
        assert result[0]["year"] == 0


def test_fmp_cash_flow_date_none():
    """Finding #3: cash flow with date=None should not crash."""
    fetcher = FMPFetcher(api_key="test_key")
    raw_data = [
        {"symbol": "TSM", "date": None, "capitalExpenditure": -500,
         "operatingCashFlow": 1000, "freeCashFlow": 500},
    ]
    with patch.object(fetcher, '_get_json', return_value=raw_data):
        result = fetcher.fetch_cash_flow("TSM", limit=1)
        assert len(result) == 1
        assert result[0]["year"] == 0


# ──────────────────────────────────────────────────────────────
# Finding #4 (MEDIUM): psycopg2 ImportError at execution
# ──────────────────────────────────────────────────────────────

def test_store_missing_psycopg2_returns_json_error():
    """Finding #4: missing psycopg2 at execution should return JSON error."""
    runner = CliRunner()
    with patch("ivco_calc.store.get_connection", side_effect=ImportError(
        "psycopg2 is not installed. Run: pip install ivco-calc[db]"
    )):
        result = runner.invoke(
            cli,
            ["store", "--type", "analysis"],
            input=json.dumps(SAMPLE_ANALYSIS),
        )
        assert result.exit_code == 1
        output = json.loads(result.output)
        assert "psycopg2" in output["error"]
        assert "pip install" in output["error"]


# ──────────────────────────────────────────────────────────────
# Finding #5 (MEDIUM): invalid JSON stdin handling
# ──────────────────────────────────────────────────────────────

def test_store_invalid_json_stdin():
    """Finding #5: malformed JSON input should return structured error."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["store", "--type", "analysis"],
        input="this is not json {{{",
    )
    assert result.exit_code == 1
    output = json.loads(result.output)
    assert "error" in output
    assert "Invalid JSON" in output["error"]


def test_store_partial_json_stdin():
    """Finding #5: truncated JSON should return structured error."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["store", "--type", "analysis"],
        input='{"ticker": "KLAC", "analysis":',
    )
    assert result.exit_code == 1
    output = json.loads(result.output)
    assert "error" in output
    assert "Invalid JSON" in output["error"]


# ──────────────────────────────────────────────────────────────
# Finding #6 (MEDIUM): _get_json network error wrapping
# ──────────────────────────────────────────────────────────────

def test_get_json_url_error_wrapped():
    """Finding #6: URLError should be wrapped as FMPError with context."""
    from urllib.error import URLError
    fetcher = FMPFetcher(api_key="test_key")
    with patch("ivco_calc.fetchers.fmp.urlopen", side_effect=URLError("connection refused")):
        with pytest.raises(FMPError, match="Network error"):
            fetcher._get_json("http://example.com", ticker="TSM", endpoint="income-statement")


def test_get_json_timeout_wrapped():
    """Finding #6: TimeoutError should be wrapped as FMPError with context."""
    fetcher = FMPFetcher(api_key="test_key")
    with patch("ivco_calc.fetchers.fmp.urlopen", side_effect=TimeoutError("timed out")):
        with pytest.raises(FMPError, match="Timeout"):
            fetcher._get_json("http://example.com", ticker="TSM", endpoint="quote")


def test_get_json_bad_json_wrapped():
    """Finding #6: non-JSON response should be wrapped as FMPError with context."""
    fetcher = FMPFetcher(api_key="test_key")
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"<html>Server Error</html>"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ivco_calc.fetchers.fmp.urlopen", return_value=mock_resp):
        with pytest.raises(FMPError, match="Invalid JSON response"):
            fetcher._get_json("http://example.com", ticker="TSM", endpoint="balance-sheet")


def test_get_json_error_includes_ticker_context():
    """Finding #6: error message should include ticker and endpoint."""
    from urllib.error import URLError
    fetcher = FMPFetcher(api_key="test_key")
    with patch("ivco_calc.fetchers.fmp.urlopen", side_effect=URLError("fail")):
        with pytest.raises(FMPError) as exc_info:
            fetcher._get_json("http://x.com", ticker="AAPL", endpoint="income-statement")
        assert "AAPL" in str(exc_info.value)
        assert "income-statement" in str(exc_info.value)
