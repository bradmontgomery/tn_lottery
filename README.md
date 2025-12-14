# TN lotto

Tools to generate random numbers for the [Tennessee lottery](http://www.tnlottery.com), and a very simple powerball simulator.

**Recent Updates:**
- ✅ Unified CLI with single `tn-lottery` command
- ✅ Updated game rules to current Powerball and Mega Millions specifications
- ✅ Improved database management with configurable location
- ✅ Enhanced error handling and retry logic in scrapers
- ✅ **Full prize tier tracking with all 9 Powerball levels**
- ✅ **Visual progress reports with bar charts and statistics**
- ✅ **Comprehensive analysis with spending breakdowns**
- ✅ **NEW: Multi-player simulation to demonstrate population statistics**

## Supported Games

* Powerball (current rules: 1-69 white balls, 1-26 powerball)
* Mega Millions (current rules: 1-70 white balls, 1-25 mega ball)
* Hot Lotto Sizzler
* Tennessee Cash
* Cash 4
* Cash 3

## Installation

1. Check out this repo.
2. Install the package: `uv pip install -e .` (or `pip install -e .`)

## Usage

The project provides a unified CLI via the `tn-lottery` command:

```bash
tn-lottery --help
```

### Available Commands

* `tn-lottery games` - List available lottery games
* `tn-lottery play` - Generate random numbers for games
* `tn-lottery simulate` - Run Powerball simulation
* `tn-lottery scrape` - Scrape lottery winner data
* `tn-lottery report` - Generate statistics from scraped data
* `tn-lottery timeline` - Show Powerball jackpot timeline

## Examples

### List available games

```bash
tn-lottery games
```

### Generate one set of numbers for all games

```bash
tn-lottery play
```

### Generate 5 sets of numbers for Powerball

```bash
tn-lottery play --game powerball --number 5
```

### Run the Powerball simulator

The simulator supports both individual and multi-player modes:

**Individual Simulation:**
```bash
# Run with default settings (until jackpot is won)
tn-lottery simulate

# Simulate playing for 20 years
tn-lottery simulate --duration 20

# Custom parameters
tn-lottery simulate \
  --plays-per-week 1 \
  --plays-per-ticket 3 \
  --cost-per-play 2.50 \
  --duration 10 \
  --report-interval 2
```

**Multi-Player Simulation:**
```bash
# Simulate 100 people each playing once
tn-lottery simulate-group --players 100

# Office pool: 50 people, 5 plays each
tn-lottery simulate-group --players 50 --plays-per-player 5

# Large population to see law of large numbers
tn-lottery simulate-group --players 2000 --plays-per-player 3

# Very large population (uses instant statistical mode)
tn-lottery simulate-group --players 1000000
```

**Features:**
- Populations < 10,000: Exact simulation with full statistics
- Populations ≥ 10,000: Statistical estimation (instant!)
- ROI distribution histogram (exact mode)
- Percentile analysis (25th, 75th, 90th, 95th, 99th)
- Enhanced jackpot winner details
- Educational insights about probability

**Available options:**
- `--plays-per-week` - How often to play (default: 2)
- `--plays-per-ticket` - Number of plays per ticket (default: 5)
- `--cost-per-play` - Cost per play in dollars (default: $2.00)
- `--duration` - Years to simulate, 0 = until jackpot (default: 0)
- `--report-interval` - Years between progress reports (default: 10)

**Prize Tracking:**
The simulator tracks all 9 Powerball prize tiers:
- Jackpot (5 + Powerball)
- $1,000,000 (5 numbers)
- $50,000 (4 + Powerball)
- $100 (4 numbers or 3 + Powerball)
- $7 (3 numbers or 2 + Powerball)
- $4 (1 + Powerball or Powerball only)

Results show realistic win rates (~25% of plays win something) and ROI calculations.

### Scrape lottery data

```bash
# Scrape TN Lottery winners
tn-lottery scrape tn

# Scrape Powerball winners
tn-lottery scrape powerball

# View statistics report
tn-lottery report

# View jackpot timeline
tn-lottery timeline
```

## Configuration

### Database Location

By default, the database is stored at `~/.local/share/tn-lottery/lottery.db`. You can customize this:

```bash
# View current database location
tn-lottery db-path

# Use a custom database location
export TN_LOTTERY_DB=/path/to/custom/lottery.db
tn-lottery scrape tn
```

*Disclaimer*: You'll likely just lose your money.

## Legacy Usage

The original scripts can still be run directly for backward compatibility:

```bash
python tn_lottery/play.py -h
python tn_lottery/simulation.py
python tn_lottery/scraper.py --help
```

## Simulation

The simulator runs a Powerball simulation with the following assumptions:

- You are an immortal playing the TN powerball every chance you get (2-times
  a week; powerball is Wed & Sat)
- You play 5 sets of numbers for $2 each ($10 / ticket)
- You only "win" if you hit the jackpot (5 numbers match + the powerball number)

The simulation runs until we hit the jackpot or kill it with Ctrl-C. It'll
periodically print the number of years you've played and the amount of money
spent playing.

## Scraper

The scraper collects winner data from the TN Lottery website and Powerball.com,
stores it in a SQLite database, and calculates statistics on the most commonly
won games, amounts, and the best-paying games on average.
