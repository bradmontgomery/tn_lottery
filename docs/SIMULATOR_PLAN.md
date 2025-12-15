# Implementation Plan: Enhanced Simulator

## Overview
The primary remaining TODO is to build an enhanced simulator with configurable inputs, tracking of minor winnings, and visualization capabilities.

## Current State Analysis

### What Exists
- Basic Powerball simulator that runs until jackpot is won
- Hardcoded parameters (5 plays @ $2 each, 2x/week)
- Only tracks jackpot wins (no minor prize tiers)
- Progress reporting every 10 years
- No time limit or configurability

### What's Missing
- Configurable game parameters (frequency, cost, duration)
- Prize tier tracking (not just jackpot)
- Payout calculations for partial matches
- Time-limited simulation mode
- Visualization/graphing of spending vs. winnings
- Summary statistics and ROI calculations
- Support for other games beyond Powerball

## Implementation Plan

### Phase 1: Configurable Parameters (Essential)
**Priority: HIGH**

Add CLI options to make the simulator configurable:

```bash
tn-lottery simulate [OPTIONS]
  --game TEXT              Game to simulate [powerball|megamillions]
  --plays-per-week INT     How often to play per week [default: 2]
  --plays-per-ticket INT   Number of plays per ticket [default: 5]
  --cost-per-play FLOAT    Cost per individual play [default: 2.00]
  --duration INT           Years to simulate (0 = until jackpot) [default: 0]
  --report-interval INT    Years between progress reports [default: 10]
```

**Files to modify:**
- `tn_lottery/simulation.py` - Add parameters to `run_simulation()`
- `tn_lottery/cli.py` - Add options to `simulate` command

**Estimated effort:** 2-3 hours

---

### Phase 2: Prize Tier Tracking (Core Feature)
**Priority: HIGH**

Implement proper payout structure for Powerball:

**Powerball Prize Tiers (current as of 2024):**
| Match | Prize | Odds |
|-------|-------|------|
| 5 + PB | Jackpot | 1 in 292,201,338 |
| 5 | $1,000,000 | 1 in 11,688,053 |
| 4 + PB | $50,000 | 1 in 913,129 |
| 4 | $100 | 1 in 36,525 |
| 3 + PB | $100 | 1 in 14,494 |
| 3 | $7 | 1 in 580 |
| 2 + PB | $7 | 1 in 701 |
| 1 + PB | $4 | 1 in 92 |
| 0 + PB | $4 | 1 in 38 |

**Implementation:**
1. Create `calculate_payout()` function to determine winnings
2. Track wins by tier in a dictionary
3. Update `check()` to return win tier instead of boolean
4. Accumulate total winnings over simulation
5. Display breakdown of wins by tier

**New data structure:**
```python
results = {
    'spent': 0,
    'won': 0,
    'net': 0,
    'wins_by_tier': defaultdict(int),
    'jackpot_won': False,
    'trials': 0,
}
```

**Files to modify:**
- `tn_lottery/simulation.py` - Add payout logic and tracking
- Create `tn_lottery/payouts.py` - Prize tier definitions

**Estimated effort:** 4-5 hours

---

### Phase 3: Enhanced Reporting (Quality of Life)
**Priority: MEDIUM**

Improve output with rich tables and statistics:

**End-of-simulation summary:**
```
╭─────────────────── Simulation Results ────────────────────╮
│ Game:           Powerball                                  │
│ Duration:       234 years (12,168 draws)                   │
│ Total Spent:    $121,680.00                                │
│ Total Won:      $47,234.00                                 │
│ Net Loss:       -$74,446.00                                │
│ ROI:            38.8%                                      │
╰────────────────────────────────────────────────────────────╯

Wins Breakdown:
┌─────────────┬───────┬────────────┬──────────────┐
│ Tier        │ Count │ Each Prize │ Total        │
├─────────────┼───────┼────────────┼──────────────┤
│ Jackpot     │     1 │ Jackpot    │ Jackpot      │
│ Match 5     │     0 │ $1,000,000 │ $0           │
│ Match 4+PB  │     0 │ $50,000    │ $0           │
│ Match 4     │     3 │ $100       │ $300         │
│ Match 3+PB  │     8 │ $100       │ $800         │
│ Match 3     │   197 │ $7         │ $1,379       │
│ Match 2+PB  │   168 │ $7         │ $1,176       │
│ Match 1+PB  │ 1,285 │ $4         │ $5,140       │
│ Match PB    │ 3,125 │ $4         │ $12,500      │
└─────────────┴───────┴────────────┴──────────────┘
```

**Files to modify:**
- `tn_lottery/simulation.py` - Enhanced reporting with rich tables

**Estimated effort:** 2-3 hours

---

### Phase 4: Time-Series Data & Visualization (Nice to Have)
**Priority: MEDIUM**

Track spending/winnings over time and visualize:

**Option A: Text-based visualization (using rich)**
```python
from rich.console import Console
# Use rich's progress bars or simple ASCII charts
```

**Option B: Terminal graphs (using plotext)**
```bash
pip install plotext
```
```python
import plotext as plt
# Creates terminal-friendly plots
```

**Option C: Save data for external visualization**
```python
# Export CSV or JSON for analysis in Excel/Python/etc.
tn-lottery simulate --export simulation_results.csv
```

**Implementation approach:**
1. Collect data points at regular intervals (e.g., yearly)
2. Store in list of dicts: `[{year: 1, spent: 520, won: 28}, ...]`
3. Display graph or export to file

**Files to modify:**
- `tn_lottery/simulation.py` - Add time-series tracking
- `pyproject.toml` - Add optional dependency for plotext

**Estimated effort:** 3-4 hours

---

### Phase 5: Multi-Game Support (Future Enhancement)
**Priority: LOW**

Extend simulator to work with other games:

- Mega Millions
- Tennessee Cash
- Generic game (user defines parameters)

**Implementation:**
- Abstract game logic into classes
- Each game defines its own payout structure
- Simulator works with any game class

**Files to create/modify:**
- `tn_lottery/games.py` - Game class definitions
- `tn_lottery/simulation.py` - Game-agnostic simulation

**Estimated effort:** 5-6 hours

---

## Recommended Implementation Order

### Sprint 1: Basic Enhancements (Most Value, Least Effort)
1. **Phase 1: Configurable Parameters** - Make it flexible
2. **Phase 2: Prize Tier Tracking** - Make it realistic
3. **Phase 3: Enhanced Reporting** - Make it informative

**Total estimated effort:** 8-11 hours
**Value:** High - Makes simulator actually useful

### Sprint 2: Advanced Features (Nice to Have)
4. **Phase 4: Visualization** - Make it visual
5. **Phase 5: Multi-Game** - Make it comprehensive

**Total estimated effort:** 8-10 hours
**Value:** Medium - Cool features but not essential

---

## Success Criteria

After implementation, users should be able to:

✅ Simulate different games with custom parameters
✅ See realistic win/loss tracking including minor prizes
✅ Get detailed statistics on their simulation
✅ Understand the actual expected value of playing
✅ Run bounded simulations (e.g., "What if I play for 20 years?")
✅ Export or visualize results

---

## Files to Create/Modify

**New Files:**
- `tn_lottery/payouts.py` - Prize structure definitions
- `tn_lottery/games.py` - Game abstractions (Phase 5)
- `tests/test_simulation.py` - Unit tests (recommended)

**Modified Files:**
- `tn_lottery/simulation.py` - Core enhancements
- `tn_lottery/cli.py` - Add command options
- `pyproject.toml` - Optional dependencies
- `README.md` - Update usage examples
- `TODO.md` - Mark items complete

---

## Testing Strategy

For each phase:
1. Unit tests for payout calculations
2. Integration tests for full simulation
3. Manual testing with various parameter combinations
4. Verify output formatting
5. Test edge cases (winning on first draw, never winning, etc.)

---

## Open Questions

1. Should jackpot amount be configurable or realistic (tracking actual jackpot growth)?
2. Should we implement Power Play / Megaplier multipliers?
3. Should we track statistics like "best winning streak" or "longest dry spell"?
4. CSV export format - what fields to include?
5. Should we add a "quick mode" that estimates results mathematically vs. simulation?

---

## Next Steps

1. Review and approve this plan
2. Start with Sprint 1, Phase 1 (configurable parameters)
3. Get feedback after each phase
4. Decide whether to proceed with Sprint 2 based on user needs

