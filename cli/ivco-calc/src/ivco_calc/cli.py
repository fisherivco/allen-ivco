"""IVCO CLI — composable valuation tools."""
import click
import json
from ivco_calc.owner_earnings import calc_owner_earnings
from ivco_calc.cagr import calc_cagr
from ivco_calc.dcf import calc_three_stage_dcf
from ivco_calc.verify import verify_iv_range
from ivco_calc.tools_registry import list_tools, get_tool_info

@click.group()
@click.version_option(version="0.3.0")
def cli():
    """IVCO — Intrinsic Value Confidence Observatory CLI tools."""
    pass

def output_json(data: dict) -> None:
    """Print JSON to stdout for piping."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))

@cli.command("calc-oe")
@click.option("--net-income", type=int, required=True)
@click.option("--depreciation", type=int, required=True)
@click.option("--amortization", type=int, required=True)
@click.option("--capex", type=int, required=True)
@click.option("--maintenance-ratio", type=float, required=True)
def calc_oe_cmd(net_income, depreciation, amortization, capex, maintenance_ratio):
    """Calculate Owner Earnings for a single year."""
    oe = calc_owner_earnings(
        net_income=net_income,
        depreciation=depreciation,
        amortization=amortization,
        capex=capex,
        maintenance_capex_ratio=maintenance_ratio
    )
    output_json({
        "owner_earnings": oe,
        "inputs": {
            "net_income": net_income,
            "depreciation": depreciation,
            "amortization": amortization,
            "capex": capex,
            "maintenance_capex_ratio": maintenance_ratio
        }
    })

@cli.command("calc-cagr")
@click.option("--start-oe", type=int, required=True)
@click.option("--end-oe", type=int, required=True)
@click.option("--start-year", type=int, required=True)
@click.option("--end-year", type=int, required=True)
@click.option("--rc-start", type=float, default=1.0)
@click.option("--rc-end", type=float, default=1.0)
def calc_cagr_cmd(start_oe, end_oe, start_year, end_year, rc_start, rc_end):
    """Calculate CAGR from Owner Earnings with Reality Coefficient."""
    oe_series = [{"year": start_year, "oe": start_oe}, {"year": end_year, "oe": end_oe}]
    rc = {start_year: rc_start, end_year: rc_end}
    result = calc_cagr(oe_series=oe_series, reality_coefficients=rc)
    output_json(result)

@cli.command("calc-iv")
@click.option("--latest-oe", type=int, required=True)
@click.option("--cagr", type=float, required=True)
@click.option("--cc-low", type=float, required=True)
@click.option("--cc-high", type=float, required=True)
@click.option("--stage2-cagr", type=float, required=True)
@click.option("--stage3-cagr", type=float, required=True)
@click.option("--discount-rate", type=float, required=True)
@click.option("--long-term-debt", type=int, required=True)
@click.option("--shares-outstanding", type=int, required=True)
@click.option("--share-par-value", type=int, default=10)
def calc_iv_cmd(latest_oe, cagr, cc_low, cc_high, stage2_cagr, stage3_cagr,
                discount_rate, long_term_debt, shares_outstanding, share_par_value):
    """Calculate Intrinsic Value using Three-Stage DCF."""
    result = calc_three_stage_dcf(
        latest_oe=latest_oe,
        cagr=cagr,
        cc_low=cc_low,
        cc_high=cc_high,
        stage2_cagr=stage2_cagr,
        stage3_cagr=stage3_cagr,
        discount_rate=discount_rate,
        long_term_debt=long_term_debt,
        shares_outstanding_raw=shares_outstanding,
        share_par_value=share_par_value,
    )
    output_json(result)

@cli.command("verify")
@click.option("--computed-low", type=int, required=True)
@click.option("--computed-high", type=int, required=True)
@click.option("--expected-low", type=int, required=True)
@click.option("--expected-high", type=int, required=True)
@click.option("--tolerance", type=int, default=0)
def verify_cmd(computed_low, computed_high, expected_low, expected_high, tolerance):
    """Verify computed IV Range against expected values."""
    result = verify_iv_range(
        computed_low=computed_low, computed_high=computed_high,
        expected_low=expected_low, expected_high=expected_high,
        tolerance=tolerance,
    )
    output_json(result)
    if result["status"] == "FAIL":
        raise SystemExit(1)

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
    cash_flow = fetcher.fetch_cash_flow(ticker, limit=years)
    quote = fetcher.fetch_quote(ticker)
    # Note: cash_flow is included in output but store_financial() only persists
    # income_statements and balance_sheet. Cash flow fields (CapEx) are used
    # during analyze for OE calculation. Full cash_flow persistence is planned
    # for a future schema addition.
    output_json({
        "ticker": ticker,
        "source": source,
        "income_statements": income,
        "balance_sheet": balance,
        "cash_flow": cash_flow,
        "quote": quote,
    })

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
    cash_flow = fetcher.fetch_cash_flow(ticker, limit=years)
    quote = fetcher.fetch_quote(ticker)

    if not income:
        click.echo(json.dumps({"error": f"No income data found for {ticker}"}))
        raise SystemExit(1)

    # Build capex lookup from cash flow
    capex_by_year = {cf["year"]: cf["capital_expenditure"] for cf in cash_flow}

    # Step 2: Calculate OE for each year
    oe_series = []
    for stmt in sorted(income, key=lambda x: x["year"]):
        # Use CapEx from cash flow if available, fallback to income statement
        capex = capex_by_year.get(stmt["year"], stmt.get("capex", 0))
        oe = calc_owner_earnings(
            net_income=stmt["net_income"],
            depreciation=stmt["depreciation"],
            amortization=stmt["amortization"],
            capex=capex,
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
    latest_oe_year = oe_series[-1]["year"] if oe_series else 0
    # Get shares from the same year as latest OE for consistency
    income_sorted = sorted(income, key=lambda x: x["year"], reverse=True)
    shares = 0
    # First: try income statement matching latest OE year
    for stmt in income_sorted:
        if stmt["year"] == latest_oe_year and stmt.get("shares_outstanding"):
            shares = stmt["shares_outstanding"]
            break
    # Fallback: most recent income statement with shares
    if not shares:
        for stmt in income_sorted:
            if stmt.get("shares_outstanding"):
                shares = stmt["shares_outstanding"]
                break
    # Fallback: balance sheet
    if not shares:
        for bs in sorted(balance, key=lambda x: x["year"], reverse=True):
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

@cli.command("store")
@click.option("--type", "store_type", type=click.Choice(["analysis", "oe", "financial", "signal"]),
              required=True, help="Data type to store")
@click.option("--ticker", type=str, default=None, help="Ticker (required for oe type)")
@click.option("--year", type=int, default=None, help="Year (required for oe type)")
@click.option("--initiated-by", type=str, default="jane", help="Who initiated this (for research_sessions)")
def store_cmd(store_type, ticker, year, initiated_by):
    """Store analysis results to Supabase PostgreSQL.

    Reads JSON from stdin. Pipe from other ivco commands:

      ivco analyze --ticker KLAC ... | ivco store --type analysis
      ivco calc-oe ... | ivco store --type oe --ticker KLAC --year 2024
      ivco fetch --ticker KLAC | ivco store --type financial
    """
    import sys
    from ivco_calc.store import store_analysis, store_oe, store_financial, store_signal

    raw = sys.stdin.read()
    if not raw.strip():
        click.echo(json.dumps({"error": "No JSON input on stdin"}))
        raise SystemExit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        click.echo(json.dumps({"error": f"Invalid JSON input: {e}"}))
        raise SystemExit(1)

    try:
        if store_type == "analysis":
            result = store_analysis(data, initiated_by=initiated_by)
        elif store_type == "oe":
            if not ticker or not year:
                click.echo(json.dumps({"error": "--ticker and --year required for oe type"}))
                raise SystemExit(1)
            result = store_oe(data, ticker=ticker, year=year)
        elif store_type == "financial":
            result = store_financial(data)
        elif store_type == "signal":
            result = store_signal(data)
        else:
            click.echo(json.dumps({"error": f"Unknown type: {store_type}"}))
            raise SystemExit(1)
    except ImportError as e:
        click.echo(json.dumps({"error": str(e)}))
        raise SystemExit(1)

    output_json(result)


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

if __name__ == "__main__":
    cli()
