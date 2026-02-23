#!/usr/bin/env python3
"""Manual FMP API test — run this to verify 403 is fixed."""
from ivco_calc.fetchers.fmp import FMPFetcher
import json

def main():
    print("=== FMP API Fix Verification ===\n")

    fetcher = FMPFetcher()  # loads FMP_API_KEY from env

    # Test 1: Income statements
    print("1. Testing income-statement endpoint...")
    try:
        income = fetcher.fetch_income_statements("TSM", limit=3)
        if income:
            print(f"   ✓ SUCCESS: Fetched {len(income)} records")
            latest = income[0]
            print(f"   Latest: {latest['year']} - Net Income: ${latest['net_income']:,.0f}")
            print(f"   JSON sample: {json.dumps(latest, indent=2)}\n")
        else:
            print("   ✗ FAILED: Empty response\n")
    except Exception as e:
        print(f"   ✗ FAILED: {type(e).__name__}: {e}\n")

    # Test 2: Balance sheet
    print("2. Testing balance-sheet-statement endpoint...")
    try:
        balance = fetcher.fetch_balance_sheet("TSM", limit=3)
        if balance:
            print(f"   ✓ SUCCESS: Fetched {len(balance)} records")
            latest = balance[0]
            print(f"   Latest: {latest['year']} - Total Debt: ${latest['total_debt']:,.0f}")
            print(f"   JSON sample: {json.dumps(latest, indent=2)}\n")
        else:
            print("   ✗ FAILED: Empty response\n")
    except Exception as e:
        print(f"   ✗ FAILED: {type(e).__name__}: {e}\n")

    # Test 3: Quote
    print("3. Testing quote endpoint...")
    try:
        quote = fetcher.fetch_quote("TSM")
        if quote and quote['price'] > 0:
            print(f"   ✓ SUCCESS")
            print(f"   Price: ${quote['price']:.2f}")
            print(f"   Market Cap: ${quote['market_cap']:,.0f}")
            print(f"   P/E: {quote['pe']:.2f}")
            print(f"   JSON: {json.dumps(quote, indent=2)}\n")
        else:
            print("   ✗ FAILED: Invalid or zero price\n")
    except Exception as e:
        print(f"   ✗ FAILED: {type(e).__name__}: {e}\n")

    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
