# Multi-Player Simulation Feature Plan

## Concept

Add ability to simulate multiple people playing the lottery simultaneously to answer questions like:
- "If 100 people each play once, will anyone win the jackpot?"
- "How many people need to play before someone wins?"
- "What's the distribution of winnings across a population?"
- "What percentage of players make money vs lose money?"

## Use Cases

### 1. Population-Scale Simulation
**Question:** "What happens when 1 million people each play one ticket?"

**Output:**
- Total spent by population: $10,000,000
- Total won by population: $5,123,456
- Jackpot winners: 0
- Players who profited: 234 (0.02%)
- Players who broke even: 1,456 (0.15%)
- Players who lost money: 998,310 (99.83%)
- Win distribution across prize tiers

### 2. Group Play Simulation
**Question:** "My office pool has 50 people, each buying 5 tickets. What are our chances?"

**Output:**
- Group statistics
- Likelihood of someone in group winning
- Expected group ROI
- Distribution of winnings within group

### 3. Until-Jackpot Simulation
**Question:** "How many people need to play before someone wins the jackpot?"

**Output:**
- Number of people who played
- Total money spent by all
- Which person won (person #45,234)
- Distribution of other wins

## Design Considerations

### Performance

**Challenge:** Simulating 1 million people × 5 plays = 5 million draws
- Current implementation: ~100 draws/second
- 1 million players would take ~14 hours!

**Solutions:**

#### Option A: Statistical Sampling (RECOMMENDED)
- For large populations, use probability distributions
- Sample representative subset, scale results
- Much faster for large N

#### Option B: Optimized Simulation
- Vectorize operations with numpy
- Batch process draws
- Multi-threading for independent players

#### Option C: Hybrid Approach
- Simulate exactly for small N (< 10,000)
- Use statistical estimation for large N (> 10,000)
- Show confidence intervals for estimates

### Implementation Approach

**Recommended: Hybrid with two modes**

#### Mode 1: Exact Simulation (players < 10,000)
```python
def simulate_exact(num_players, plays_per_player, cost_per_play):
    """Simulate each player individually."""
    results = []
    for player_id in range(num_players):
        player_result = simulate_single_player(plays_per_player, cost_per_play)
        results.append(player_result)
    return aggregate_results(results)
```

#### Mode 2: Statistical Estimation (players >= 10,000)
```python
def simulate_statistical(num_players, plays_per_player, cost_per_play):
    """Use probability distributions for large populations."""
    total_plays = num_players * plays_per_player
    
    # Calculate expected wins per tier based on odds
    expected_wins = {}
    for tier in POWERBALL_PRIZES:
        probability = 1.0 / odds[tier.name]
        expected_wins[tier.name] = int(total_plays * probability)
    
    # Add statistical variance
    actual_wins = add_variance(expected_wins, total_plays)
    
    return create_population_results(actual_wins, num_players)
```

## Proposed CLI Interface

```bash
# Single drawing with N players
tn-lottery simulate-group --players 100 --plays-per-player 5

# Multiple drawings until someone wins jackpot
tn-lottery simulate-group --players 1000 --until-jackpot

# Specific duration with population
tn-lottery simulate-group --players 500 --duration 1 --plays-per-week 2

# Large population (uses statistical mode)
tn-lottery simulate-group --players 1000000 --plays-per-player 1
```

## Data Structures

### PlayerResult
```python
@dataclass
class PlayerResult:
    player_id: int
    spent: float
    won: float
    net: float
    wins_by_tier: dict
    won_jackpot: bool
```

### PopulationResult
```python
@dataclass
class PopulationResult:
    num_players: int
    total_spent: float
    total_won: float
    jackpot_winners: list[int]  # player IDs who won jackpot
    
    # Distribution stats
    players_profited: int
    players_broke_even: int
    players_lost: int
    
    # Aggregate wins
    total_wins_by_tier: dict
    
    # Statistical measures
    mean_roi: float
    median_roi: float
    std_dev_roi: float
    
    # Best/worst performers
    best_player: PlayerResult
    worst_player: PlayerResult
```

## Output Display

### Summary Statistics
```
Multi-Player Simulation Results
Population: 1,000 players
Duration: 1 drawing
Plays per player: 5

══════════════════════════════════════════════════════════
POPULATION STATISTICS
══════════════════════════════════════════════════════════

Financial Summary:
  Total Spent:        $10,000.00
  Total Won:           $4,956.00
  Population Net:     -$5,044.00
  Population ROI:         49.6%

Outcome Distribution:
  Players who profited:      12 (1.2%)  ████░░░░░░░░░░░░░░░░
  Players broke even:        45 (4.5%)  ████░░░░░░░░░░░░░░░░
  Players who lost:         943 (94.3%) ████████████████████

Jackpot Winners:            0 (0.0%)

Win Statistics:
  Mean ROI:              49.6%
  Median ROI:            20.0%
  Std Deviation:         85.2%
  
  Best Player (#543):    Won $500, Spent $10 (5000% ROI!)
  Worst Player (#127):   Won $0, Spent $10 (-100% ROI)
```

### Prize Distribution Across Population
```
Prize Tier Distribution:
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Prize Tier   ┃ Total Wins  ┃ Prize Amount ┃ Total Paid  ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Jackpot      │           0 │      Jackpot │          $0 │
│ Match 5      │           0 │   $1,000,000 │          $0 │
│ Match 4 + PB │           1 │      $50,000 │     $50,000 │
│ Match 4      │          14 │         $100 │      $1,400 │
│ Match 3 + PB │          12 │         $100 │      $1,200 │
│ Match 3      │         105 │           $7 │        $735 │
│ Match 2 + PB │          98 │           $7 │        $686 │
│ Match 1 + PB │         623 │           $4 │      $2,492 │
│ Match PB     │       1,567 │           $4 │      $6,268 │
└──────────────┴─────────────┴──────────────┴─────────────┘

Total Prize Winners: 2,420 out of 5,000 plays (48.4%)
Multiple winners per player: 234 players (23.4%)
```

### Jackpot Winner Details (if applicable)
```
╭─────────────────────── 🎰 JACKPOT WINNER! ───────────────────────╮
│                                                                   │
│  Player #45,234 won the jackpot!                                 │
│                                                                   │
│  This occurred after:                                             │
│    • 45,234 people played                                         │
│    • $452,340 spent in total                                      │
│    • Expected probability: 0.015% (1 in 6,461)                    │
│                                                                   │
│  Lucky Player Stats:                                              │
│    • Spent: $10                                                   │
│    • Won: JACKPOT + $28 in small prizes                           │
│    • ROI: ∞ %                                                     │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
```

### ROI Distribution Histogram
```
ROI Distribution (% of players):

  100%+ │ ▌                      (1.2% of players)
   50%  │ ███▌                   (12.3%)
   20%  │ ████████░░             (28.5%)
    0%  │ ████████████░░         (42.1%)
  -50%  │ ██████████████████░░   (89.4%)
 -100%  │ ████████████████████   (94.3%)
        └─────────────────────────────────
```

## Performance Optimization Strategies

### 1. Numpy Vectorization
```python
import numpy as np

def generate_many_draws(n):
    """Generate n Powerball draws efficiently."""
    white_balls = np.random.randint(1, 70, size=(n, 5))
    powerballs = np.random.randint(1, 27, size=n)
    return white_balls, powerballs
```

### 2. Parallel Processing
```python
from multiprocessing import Pool

def simulate_batch(args):
    """Simulate a batch of players."""
    start_id, end_id, params = args
    return [simulate_player(i, params) for i in range(start_id, end_id)]

def simulate_parallel(num_players, params):
    """Simulate using multiple CPU cores."""
    batch_size = num_players // cpu_count()
    batches = create_batches(num_players, batch_size)
    
    with Pool() as pool:
        results = pool.map(simulate_batch, batches)
    
    return flatten(results)
```

### 3. Progressive Display
```python
with Progress() as progress:
    task = progress.add_task("[cyan]Simulating...", total=num_players)
    
    for i in range(num_players):
        simulate_player(i)
        progress.update(task, advance=1)
        
        # Update stats every 1000 players
        if i % 1000 == 0:
            show_interim_stats()
```

## Edge Cases to Handle

1. **Single player** - Should work same as regular simulate
2. **Very large N** (> 1M) - Use statistical mode, warn about estimation
3. **Jackpot in first few players** - Still show full population stats
4. **Multiple jackpot winners** - List all winners
5. **All players lose** - Common, show expected behavior
6. **Outlier wins** - Highlight in summary

## Educational Value

This feature teaches:
1. **Law of Large Numbers** - As N increases, population ROI approaches expected value
2. **Variance** - Individual results vary wildly, population is more predictable
3. **Survivor Bias** - Most people lose, but winners are visible
4. **Scale of Odds** - "1 in 292 million" becomes tangible
5. **Expected Value** - Population-level math vs individual luck

## Testing Strategy

1. **Small N (N=10)** - Verify exact simulation
2. **Medium N (N=1000)** - Check performance
3. **Large N (N=100000)** - Verify statistical mode
4. **Edge cases** - 1 player, jackpot on first player, etc.
5. **Statistics** - Verify ROI converges to expected value
6. **Performance** - Benchmark different N values

## Implementation Phases

### Phase A: Core Multi-Player Logic (3-4 hours)
- PlayerResult and PopulationResult data structures
- simulate_exact() for small populations
- Basic aggregation and statistics
- CLI option --players

### Phase B: Statistical Mode (2-3 hours)
- simulate_statistical() for large populations
- Automatic mode switching based on N
- Confidence intervals for estimates

### Phase C: Enhanced Display (2-3 hours)
- Population statistics table
- ROI distribution
- Jackpot winner highlights
- Best/worst player details

### Phase D: Performance Optimization (2-3 hours)
- Numpy vectorization
- Parallel processing
- Progress bars for long simulations

**Total Estimated Effort: 9-13 hours**

## Risks & Mitigations

**Risk:** Performance issues with large N
**Mitigation:** Hybrid approach with statistical mode

**Risk:** Statistical mode not accurate
**Mitigation:** Validate against exact mode for N=10,000

**Risk:** Memory issues with millions of PlayerResult objects
**Mitigation:** Only store aggregate stats, not individual results for large N

**Risk:** User confusion about exact vs statistical
**Mitigation:** Clear messaging, show "(estimated)" for statistical mode

## Success Criteria

After implementation, users can:
- ✅ Simulate 100 people playing
- ✅ Simulate 1 million people playing (fast!)
- ✅ See population-level statistics
- ✅ Understand distribution of outcomes
- ✅ Learn about probability at scale
- ✅ See who wins and who loses
- ✅ Understand expected value vs individual variance

## Future Enhancements

- Compare different strategies across population
- Track which numbers are most/least common
- Simulate lottery pools (shared winnings)
- Historical simulation (replay actual drawings)
- Geographic distribution (which states win most)

---

This feature would transform the simulator from individual to population-level analysis, making it even more educational and interesting!
