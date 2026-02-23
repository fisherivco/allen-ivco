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
        "weightedAverageShsOut": 5186949600,
    }
    fetcher = FMPFetcher(api_key="test_key")
    parsed = fetcher.parse_income_statement(raw)
    assert parsed["ticker"] == "TSM"
    assert parsed["year"] == 2022
    assert parsed["net_income"] == 1016900515000
    assert parsed["capex"] == 1075620698000  # positive
    assert parsed["depreciation"] > 0
    assert parsed["shares_outstanding"] == 5186949600


def test_fmp_fetcher_build_url():
    """FMP API URL is correctly constructed (stable API format)."""
    fetcher = FMPFetcher(api_key="demo_key")
    url = fetcher.build_url("TSM", "income-statement", limit=10)
    assert "financialmodelingprep.com/stable" in url
    assert "symbol=TSM" in url
    assert "apikey=demo_key" in url
    assert "limit=10" in url


def test_fmp_fetcher_parse_cash_flow():
    """FMP cash flow statement parsing extracts CapEx correctly."""
    raw = {
        "symbol": "TSM",
        "date": "2025-12-31",
        "capitalExpenditure": -1285591558000,
        "operatingCashFlow": 1500000000000,
        "freeCashFlow": 214408442000,
    }
    fetcher = FMPFetcher(api_key="test_key")
    # fetch_cash_flow returns a list, so we need to mock _get_json
    with patch.object(fetcher, '_get_json', return_value=[raw]):
        result = fetcher.fetch_cash_flow("TSM", limit=1)
        assert len(result) == 1
        cf = result[0]
        assert cf["ticker"] == "TSM"
        assert cf["year"] == 2025
        assert cf["capital_expenditure"] == 1285591558000  # positive (abs)
        assert cf["operating_cash_flow"] == 1500000000000
        assert cf["free_cash_flow"] == 214408442000


def test_fmp_fetcher_balance_sheet_fields():
    """FMP balance sheet includes long_term_debt and common_stock."""
    raw = {
        "symbol": "TSM",
        "date": "2025-12-31",
        "totalDebt": 950000000000,
        "longTermDebt": 853816320000,
        "totalAssets": 5000000000000,
        "commonStockSharesOutstanding": 5186949600,
        "commonStock": 258594577000,
    }
    fetcher = FMPFetcher(api_key="test_key")
    with patch.object(fetcher, '_get_json', return_value=[raw]):
        result = fetcher.fetch_balance_sheet("TSM", limit=1)
        assert len(result) == 1
        bs = result[0]
        assert bs["ticker"] == "TSM"
        assert bs["year"] == 2025
        assert bs["total_debt"] == 950000000000
        assert bs["long_term_debt"] == 853816320000
        assert bs["common_stock"] == 258594577000


def test_fetch_cli_requires_ticker():
    """CLI fetch command requires --ticker."""
    runner = CliRunner()
    result = runner.invoke(cli, ["fetch", "--years", "5"])
    assert result.exit_code != 0
    assert "Missing" in result.output or "required" in result.output.lower()
