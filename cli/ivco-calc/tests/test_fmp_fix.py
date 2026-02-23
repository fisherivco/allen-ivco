"""Test FMP API base URL fix for 403 error."""
import pytest
from ivco_calc.fetchers.fmp import FMPFetcher


def test_fmp_base_url_is_stable():
    """FMP base URL should use /stable not /api/v3."""
    assert FMPFetcher.BASE_URL == "https://financialmodelingprep.com/stable"


@pytest.mark.skip(reason="Requires valid FMP_API_KEY and network access")
def test_fmp_live_income_statement():
    """Live test: fetch TSM income statements (requires API key)."""
    fetcher = FMPFetcher()  # loads from FMP_API_KEY env
    income = fetcher.fetch_income_statements("TSM", limit=3)
    assert len(income) > 0
    assert income[0]["ticker"] == "TSM"
    assert income[0]["year"] > 2020
    assert income[0]["net_income"] > 0


@pytest.mark.skip(reason="Requires valid FMP_API_KEY and network access")
def test_fmp_live_balance_sheet():
    """Live test: fetch TSM balance sheet (requires API key)."""
    fetcher = FMPFetcher()
    balance = fetcher.fetch_balance_sheet("TSM", limit=3)
    assert len(balance) > 0
    assert balance[0]["ticker"] == "TSM"
    assert balance[0]["year"] > 2020
    assert balance[0]["total_debt"] > 0


@pytest.mark.skip(reason="Requires valid FMP_API_KEY and network access")
def test_fmp_live_quote():
    """Live test: fetch TSM quote (requires API key)."""
    fetcher = FMPFetcher()
    quote = fetcher.fetch_quote("TSM")
    assert quote["ticker"] == "TSM"
    assert quote["price"] > 0
    assert quote["market_cap"] > 0
