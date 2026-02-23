"""Tests for ivco-store module — unit tests (no DB required)."""
import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from ivco_calc.cli import cli


# Sample analyze output (matches real ivco analyze output structure)
SAMPLE_ANALYSIS = {
    "ticker": "KLAC",
    "analysis": {
        "oe_series": [
            {"year": 2015, "oe": 800000000},
            {"year": 2016, "oe": 900000000},
            {"year": 2024, "oe": 3500000000},
        ],
        "cagr": {"cagr": 0.1766, "start_year": 2015, "end_year": 2024, "periods": 9},
        "iv": {
            "stage1_cagr_low": 0.2119,
            "stage1_cagr_high": 0.2649,
            "iv_per_share_low": 450,
            "iv_per_share_high": 680,
            "long_term_debt": 0,
            "shares_outstanding": 134000000,
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

SAMPLE_OE = {
    "owner_earnings": 3500000000,
    "inputs": {
        "net_income": 4000000000,
        "depreciation": 500000000,
        "amortization": 0,
        "capex": 1200000000,
        "maintenance_capex_ratio": 0.15,
    },
}

SAMPLE_SIGNAL = {
    "ticker": "KLAC",
    "signal_type": "news",
    "headline": "KLA announces record Q4 revenue",
    "content": "KLA Corp reported record revenue...",
    "source": "tavily",
    "source_url": "https://example.com/klac-q4",
    "relevance_score": 0.85,
}


def test_store_command_exists():
    """Verify store command is registered in CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["store", "--help"])
    assert result.exit_code == 0
    assert "--type" in result.output
    assert "analysis" in result.output


def test_store_no_stdin():
    """Store with empty stdin should fail gracefully."""
    runner = CliRunner()
    result = runner.invoke(cli, ["store", "--type", "analysis"], input="")
    assert result.exit_code == 1
    output = json.loads(result.output)
    assert "error" in output


def test_store_oe_requires_ticker_and_year():
    """Store OE type requires --ticker and --year."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["store", "--type", "oe"],
        input=json.dumps(SAMPLE_OE),
    )
    assert result.exit_code == 1
    output = json.loads(result.output)
    assert "ticker" in output["error"].lower() or "year" in output["error"].lower()


@patch("ivco_calc.store.get_connection")
def test_store_analysis_calls_db(mock_conn):
    """Store analysis type should attempt DB write."""
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = [1]
    mock_conn.return_value.__enter__ = lambda s: s
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    mock_conn.return_value.cursor.return_value = mock_cur

    runner = CliRunner()
    result = runner.invoke(
        cli, ["store", "--type", "analysis"],
        input=json.dumps(SAMPLE_ANALYSIS),
    )
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert output["status"] == "ok"
    assert output["ticker"] == "KLAC"


@patch("ivco_calc.store.get_connection")
def test_store_signal_calls_db(mock_conn):
    """Store signal type should write to watchlist_signals."""
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = [42]
    mock_conn.return_value.__enter__ = lambda s: s
    mock_conn.return_value.__exit__ = MagicMock(return_value=False)
    mock_conn.return_value.cursor.return_value = mock_cur

    runner = CliRunner()
    result = runner.invoke(
        cli, ["store", "--type", "signal"],
        input=json.dumps(SAMPLE_SIGNAL),
    )
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert output["status"] == "ok"
    assert output["table"] == "watchlist_signals"


def test_tool_registry_includes_store():
    """Verify store is listed in tool registry."""
    from ivco_calc.tools_registry import list_tools, get_tool_info
    tools = list_tools()
    names = [t["name"] for t in tools]
    assert "store" in names

    info = get_tool_info("store")
    assert info is not None
    assert info["layer"] == 1
    assert "analysis" in info["types"]
