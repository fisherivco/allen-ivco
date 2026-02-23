"""Financial Modeling Prep (FMP) API fetcher — free tier."""
import json
import ssl
from urllib.request import urlopen, Request
from urllib.error import URLError
from ivco_calc.fetchers.base import BaseFetcher


class FMPError(Exception):
    """FMP API error with ticker/endpoint context."""
    pass


def _safe_year(raw: dict) -> int:
    """Extract year from FMP record's date field, returning 0 on failure.

    Handles: None, empty string, malformed strings, missing key.
    """
    date = raw.get("date") or ""
    if len(date) < 4:
        return 0
    try:
        return int(date[:4])
    except (ValueError, TypeError):
        return 0

def _ssl_context() -> ssl.SSLContext:
    """Build SSL context using certifi CA bundle (macOS Python fix)."""
    import certifi
    return ssl.create_default_context(cafile=certifi.where())


class FMPFetcher(BaseFetcher):
    """FMP API v3 client. Free tier: 250 requests/day."""

    BASE_URL = "https://financialmodelingprep.com/stable"

    def __init__(self, api_key: str | None = None):
        if api_key:
            self.api_key = api_key
        else:
            from ivco_calc.env_loader import ensure_var
            self.api_key = ensure_var("FMP_API_KEY")

    def build_url(self, ticker: str, endpoint: str, limit: int = 10) -> str:
        """Build FMP API URL with symbol query param (new stable API format)."""
        return f"{self.BASE_URL}/{endpoint}?symbol={ticker}&limit={limit}&apikey={self.api_key}"

    def _get_json(self, url: str, *, ticker: str = "", endpoint: str = "") -> list | dict:
        """Fetch JSON from FMP API with contextual error wrapping."""
        req = Request(url, headers={"User-Agent": "IVCO-CLI/0.3.0"})
        ctx = f"ticker={ticker}, endpoint={endpoint}" if ticker else url
        try:
            with urlopen(req, timeout=30, context=_ssl_context()) as resp:
                return json.loads(resp.read().decode())
        except URLError as e:
            raise FMPError(f"Network error fetching {ctx}: {e}") from e
        except TimeoutError as e:
            raise FMPError(f"Timeout fetching {ctx}: {e}") from e
        except json.JSONDecodeError as e:
            raise FMPError(f"Invalid JSON response from {ctx}: {e}") from e

    def parse_income_statement(self, raw: dict) -> dict:
        """Parse FMP income statement into IVCO format."""
        year = _safe_year(raw)
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
            "shares_outstanding": raw.get("weightedAverageShsOut", 0) or 0,
        }

    def fetch_income_statements(self, ticker: str, limit: int = 10) -> list[dict]:
        url = self.build_url(ticker, "income-statement", limit)
        raw_list = self._get_json(url, ticker=ticker, endpoint="income-statement")
        if not isinstance(raw_list, list):
            return []
        return [self.parse_income_statement(r) for r in raw_list]

    def fetch_balance_sheet(self, ticker: str, limit: int = 10) -> list[dict]:
        url = self.build_url(ticker, "balance-sheet-statement", limit)
        raw_list = self._get_json(url, ticker=ticker, endpoint="balance-sheet-statement")
        if not isinstance(raw_list, list):
            return []
        return [
            {
                "ticker": r.get("symbol", ""),
                "year": _safe_year(r),
                "total_debt": r.get("totalDebt", 0) or 0,
                "long_term_debt": r.get("longTermDebt", 0) or 0,
                "total_assets": r.get("totalAssets", 0) or 0,
                "shares_outstanding": r.get("commonStockSharesOutstanding", 0) or 0,
                "common_stock": r.get("commonStock", 0) or 0,
            }
            for r in raw_list
        ]

    def fetch_cash_flow(self, ticker: str, limit: int = 10) -> list[dict]:
        """Fetch cash flow statements to get capital expenditure.

        Note: cash_flow data is returned by `fetch` but NOT persisted by
        `store_financial()` (which only writes income + balance sheet).
        Selected fields (CapEx) are used during `analyze` for OE calculation.
        """
        url = self.build_url(ticker, "cash-flow-statement", limit)
        raw_list = self._get_json(url, ticker=ticker, endpoint="cash-flow-statement")
        if not isinstance(raw_list, list):
            return []
        return [
            {
                "ticker": r.get("symbol", ""),
                "year": _safe_year(r),
                "capital_expenditure": abs(r.get("capitalExpenditure", 0) or 0),
                "operating_cash_flow": r.get("operatingCashFlow", 0) or 0,
                "free_cash_flow": r.get("freeCashFlow", 0) or 0,
            }
            for r in raw_list
        ]

    def fetch_quote(self, ticker: str) -> dict:
        """Fetch real-time quote using symbol query param."""
        url = f"{self.BASE_URL}/quote?symbol={ticker}&apikey={self.api_key}"
        data = self._get_json(url, ticker=ticker, endpoint="quote")
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
