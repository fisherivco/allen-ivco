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
    {
        "name": "store",
        "layer": 1,
        "layer_name": "primitive",
        "description": "Store analysis results to Supabase PostgreSQL",
        "usage": "ivco analyze ... | ivco store --type analysis",
        "input": "JSON from stdin (pipe from other ivco commands)",
        "output": "JSON confirmation with stored row IDs",
        "requires": "DATABASE_URL env var + psycopg2 (pip install ivco-calc[db])",
        "types": ["analysis", "oe", "financial", "signal"],
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
    # Layer 2: Planned (not yet implemented)
    {
        "name": "ivco-search",
        "layer": 1,
        "layer_name": "primitive",
        "description": "Search news, supply chain, and competitor intel via Tavily API",
        "usage": "ivco-search --ticker KLAC --scope news,supply-chain,competitors",
        "input": "Ticker + search scope",
        "output": "JSON with search results scored by relevance",
        "status": "planned",
        "requires": "TAVILY_API_KEY env var",
    },
    {
        "name": "ivco-report",
        "layer": 2,
        "layer_name": "composed",
        "description": "Generate Obsidian report + Blog draft from research session",
        "usage": "ivco-report --session-id N --output obsidian,blog",
        "input": "Research session ID from Supabase",
        "output": "Markdown files written to Obsidian + docs/blog/",
        "status": "planned",
        "composes": ["store"],
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
