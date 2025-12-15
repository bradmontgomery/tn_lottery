# Technical Debt Improvements

## Overview
This document describes the technical debt and deficiencies that were addressed after the CLI refactor.

## Changes Made

### 1. Database Location Management

**Problem:** Database file was hardcoded to `lottery.db` in the current directory, causing:
- Different database files created depending on where commands were run
- No control over database location
- Data scattered across multiple locations

**Solution:**
- Implemented intelligent database path resolution in `db.py`
- Priority order:
  1. `TN_LOTTERY_DB` environment variable (if set)
  2. `~/.local/share/tn-lottery/lottery.db` (XDG standard)
  3. `./lottery.db` (fallback if can't create data directory)
- Added `tn-lottery db-path` command to show current database location
- Database directory is created automatically if it doesn't exist

**Benefits:**
- Consistent database location across all command invocations
- User can customize location via environment variable
- Follows XDG Base Directory specification
- Graceful fallback for permission issues

**Usage:**
```bash
# Show current database location
tn-lottery db-path

# Use custom database location
export TN_LOTTERY_DB=/path/to/custom/lottery.db
tn-lottery scrape tn
```

### 2. Updated Lottery Game Rules

**Problem:** Lottery number ranges were outdated:
- Powerball: Used old ranges (1-59 for white balls, 1-35 for powerball)
- Mega Millions: Used old ranges (1-56 for white balls, 1-46 for mega ball)
- Game rules changed multiple times (Powerball in 2015 and 2021, Mega Millions in 2017)

**Solution:**
Updated `lottery.py` with current official rules:

**Powerball (as of October 2021):**
- 5 white balls from 1-69
- 1 red Powerball from 1-26
- Reference: https://www.powerball.com/how-to-play

**Mega Millions (as of October 2017):**
- 5 white balls from 1-70
- 1 Mega Ball from 1-25
- Reference: https://www.megamillions.com/how-to-play

**Benefits:**
- Numbers generated match actual lottery rules
- Simulation accuracy improved
- Documentation updated with official sources

### 3. Improved Scraper Error Handling

**Problem:** Scraper had minimal error handling:
- Network failures caused immediate script termination
- No retry logic for transient failures
- Rate limiting not handled
- No summary of successes/failures
- Could hammer servers with rapid requests

**Solution:**

**Retry Logic:**
- Added `fetch_with_retry()` function with configurable retries
- Default: 3 attempts with exponential backoff
- Handles rate limiting (HTTP 429) specially with increased delays
- Request timeout of 10 seconds to prevent hanging

**Better Error Handling:**
- Network errors caught and logged individually
- Parsing errors don't stop entire scrape
- Failed pages tracked and reported at end
- Total winners count displayed

**Rate Limiting:**
- Added 0.5 second delay between page requests
- Respects HTTP 429 responses with increased backoff
- Prevents server overload

**Improved parse_amount():**
- Better handling of edge cases
- Returns 0.0 for empty/invalid amounts instead of raising
- Handles "million" suffix parsing more robustly

**Benefits:**
- More resilient to network issues
- Better server citizenship
- Complete scrape summaries
- Fewer failed scrapes due to transient issues

### 4. Database Error Handling

**Problem:**
- Commands failed with cryptic SQLite errors if database not initialized
- No helpful messages for empty databases

**Solution:**
- `generate_report()` and `show_timeline()` now call `init_db()` automatically
- Check for empty tables and provide helpful messages
- Guide users to run scraper first if no data exists

**Benefits:**
- Better user experience for new users
- Clear guidance on required steps
- No confusing SQL error messages

### 5. Code Quality Improvements

**Additional improvements made:**

**Import Organization:**
- Added `time` module for sleep/delays
- Proper ordering of imports

**Error Messages:**
- More descriptive and actionable
- Colored output (yellow warnings, red errors, green success)
- Show total counts and failed pages

**Documentation:**
- Updated docstrings with current URLs
- Added parameter descriptions
- Better function documentation

## Testing Performed

✅ Database path resolution works correctly
✅ Database created in `~/.local/share/tn-lottery/` directory
✅ `tn-lottery db-path` command displays correct location
✅ Powerball numbers generated within correct ranges (1-69, 1-26)
✅ Mega Millions numbers generated within correct ranges (1-70, 1-25)
✅ Report command handles empty database gracefully
✅ Timeline command handles empty database gracefully
✅ Parse amount handles edge cases without crashing

## Environment Variable Configuration

Users can now customize the database location:

```bash
# Use a custom database path
export TN_LOTTERY_DB=/path/to/custom/lottery.db

# Or set it per-command
TN_LOTTERY_DB=./test.db tn-lottery scrape tn
```

## Summary

These improvements address the major technical debt identified:
- ✅ Database location no longer hardcoded
- ✅ Game rules updated to current specifications
- ✅ Robust error handling and retry logic
- ✅ Better user experience with helpful messages
- ✅ Rate limiting and server-friendly scraping

The application is now more robust, user-friendly, and maintainable.
