# FMP API 403 Forbidden Fix — Summary Report

**Date**: 2026-02-16
**Issue**: FMP API returning HTTP 403 Forbidden for all endpoints
**Status**: ✅ RESOLVED

---

## Root Cause

Financial Modeling Prep changed their API structure:

| Old (Broken) | New (Fixed) |
|--------------|-------------|
| `https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}` | `https://financialmodelingprep.com/stable/{endpoint}?symbol={ticker}` |

**Two key changes:**
1. Base URL: `/api/v3` → `/stable`
2. Ticker routing: Path-based (`/TSM`) → Query param (`?symbol=TSM`)

The old `/api/v3` endpoints are now considered "legacy" and return 403 errors.

---

## Changes Made

### 1. Base URL Update
**File**: `cli/ivco-calc/src/ivco_calc/fetchers/fmp.py`

```python
# Before
BASE_URL = "https://financialmodelingprep.com/api/v3"

# After
BASE_URL = "https://financialmodelingprep.com/stable"
```

### 2. URL Building Method
**File**: `cli/ivco-calc/src/ivco_calc/fetchers/fmp.py`

```python
# Before
def build_url(self, ticker: str, endpoint: str, limit: int = 10) -> str:
    return f"{self.BASE_URL}/{endpoint}/{ticker}?limit={limit}&apikey={self.api_key}"

# After
def build_url(self, ticker: str, endpoint: str, limit: int = 10) -> str:
    """Build FMP API URL with symbol query param (new stable API format)."""
    return f"{self.BASE_URL}/{endpoint}?symbol={ticker}&limit={limit}&apikey={self.api_key}"
```

### 3. Quote Endpoint
**File**: `cli/ivco-calc/src/ivco_calc/fetchers/fmp.py`

```python
# Before
url = f"{self.BASE_URL}/quote/{ticker}?apikey={self.api_key}"

# After
url = f"{self.BASE_URL}/quote?symbol={ticker}&apikey={self.api_key}"
```

### 4. Test Update
**File**: `cli/ivco-calc/tests/test_fetch.py`

Updated URL assertions to check for `symbol=TSM` instead of path-based ticker.

### 5. New Test File
**File**: `cli/ivco-calc/tests/test_fmp_fix.py`

Created comprehensive test suite for FMP API fix validation (includes live API tests marked as skipped by default).

---

## Test Results

### Full Test Suite: ✅ 34 passed, 3 skipped

```
pytest tests/ -v
========================= 34 passed, 3 skipped =========================
```

### Live API Test Results

**TSM Income Statement** (3 years):
- ✓ Fetched 3 records
- Latest: 2025 - Net Income: $1,735,678,080,000
- Revenue: $3,848,510,949,000

**TSM Balance Sheet** (3 years):
- ✓ Fetched 3 records
- Latest: 2025 - Total Debt: $990,356,650,000
- Total Assets: $7,910,679,587,000

**TSM Quote**:
- ✓ Price: $366.36
- ✓ Market Cap: $1,900,127,936,629
- P/E: N/A (0.00 in response)

---

## API Endpoint Reference

All FMP API endpoints now use this format:

```
https://financialmodelingprep.com/stable/{endpoint}?symbol={TICKER}&apikey={KEY}
```

**Tested Endpoints:**
- `/stable/income-statement`
- `/stable/balance-sheet-statement`
- `/stable/quote`

**Authentication**: API key appended as query parameter (`&apikey=YOUR_KEY`)

---

## Sources

- [FMP Income Statement API Documentation](https://site.financialmodelingprep.com/developer/docs/stable/income-statement)
- [FMP Quote API Documentation](https://site.financialmodelingprep.com/developer/docs/stable/quote)
- [FMP Quickstart Guide](https://site.financialmodelingprep.com/developer/docs/quickstart)
- [GitHub Issue: 403 Error with Legacy Endpoints](https://github.com/AI4Finance-Foundation/FinRobot/issues/73)

---

## Impact

- ✅ All existing tests pass
- ✅ No breaking changes to IVCO CLI interface
- ✅ FMP fetcher now works with current API structure
- ✅ Compatible with free tier (250 requests/day)

---

## Next Steps

1. ✅ Update base URL and endpoint structure
2. ✅ Fix URL building logic
3. ✅ Update tests
4. ✅ Verify live API calls work
5. ⏭️ Consider removing `manual_fmp_test.py` (was used for manual verification)

---

**Verified by**: Chi (AI-Native Full-Stack Engineer)
**Review status**: Ready for Allen's approval
