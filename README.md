# TN Lottery Tools

A comprehensive command-line toolkit for the [Tennessee lottery](http://www.tnlottery.com) featuring random number generation, Powerball simulation, winner data scraping, and statistical analysis.

**Recent Updates:**
- ✅ Unified CLI with single `tn-lottery` command
- ✅ Updated game rules to current Powerball and Mega Millions specifications
- ✅ Improved database management with configurable location
- ✅ Enhanced error handling and retry logic in scrapers
- ✅ **Full prize tier tracking with all 9 Powerball levels**
- ✅ **Visual progress reports with bar charts and statistics**
- ✅ **Comprehensive analysis with spending breakdowns**
- ✅ **Multi-player simulation to demonstrate population statistics**

## Supported Games

* Powerball (current rules: 1-69 white balls, 1-26 powerball)
* Mega Millions (current rules: 1-70 white balls, 1-25 mega ball)
* Hot Lotto Sizzler
* Tennessee Cash
* Cash 4
* Cash 3

## Installation & Usage

### Option 1: Run Directly with uvx (Recommended)

No installation needed! Use `uvx` to run the tool directly:

```bash
# Run from PyPI (once published)
uvx tn-lottery --help

# Run from local directory
uvx --from . tn-lottery --help
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/tn_lottery.git
cd tn_lottery

# Install with uv (recommended)
uv pip install -e .

# Or install with pip
pip install -e .

# Run the CLI
tn-lottery --help
```

### Option 3: Install from PyPI (once published)

```bash
uv pip install tn-lottery
# or
pip install tn-lottery
```

## Quick Start

```bash
# Generate lottery numbers
tn-lottery play

# Run a single-player Powerball simulation
tn-lottery simulate

# Simulate 100 people playing together
tn-lottery simulate-group --players 100

# List all commands
tn-lottery --help
```

## Available Commands

| Command | Description |
|---------|-------------|
| `tn-lottery games` | List available lottery games |
| `tn-lottery play` | Generate random numbers for games |
| `tn-lottery simulate` | Run individual Powerball simulation |
| `tn-lottery simulate-group` | Simulate multiple players simultaneously |
| `tn-lottery scrape` | Scrape lottery winner data |
| `tn-lottery report` | Generate statistics from scraped data |
| `tn-lottery timeline` | Show Powerball jackpot timeline |
| `tn-lottery db-path` | Show database file location |

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

### Run the Powerball Simulator

The simulator demonstrates the mathematics of lottery odds through both individual and multi-player simulations.

#### Individual Simulation

Simulate a single person playing Powerball over time:

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

**Individual Simulation Options:**
- `--plays-per-week` - How often to play (default: 2)
- `--plays-per-ticket` - Number of plays per ticket (default: 5)
- `--cost-per-play` - Cost per play in dollars (default: $2.00)
- `--duration` - Years to simulate, 0 = until jackpot (default: 0)
- `--report-interval` - Years between progress reports (default: 10)

**Prize Tracking:**

The simulator tracks all 9 Powerball prize tiers:
- **Jackpot** (5 + Powerball)
- **$1,000,000** (5 numbers)
- **$50,000** (4 + Powerball)
- **$100** (4 numbers or 3 + Powerball)
- **$7** (3 numbers or 2 + Powerball)
- **$4** (1 + Powerball or Powerball only)

Results show realistic win rates (~25% of plays win something) and ROI calculations.

#### Multi-Player Simulation

Simulate multiple people playing simultaneously to demonstrate population-level statistics:

```bash
# Simulate 100 people each playing once
tn-lottery simulate-group --players 100

# Office pool: 50 people, 5 plays each
tn-lottery simulate-group --players 50 --plays-per-player 5

# Large population to see law of large numbers
tn-lottery simulate-group --players 5000 --plays-per-player 3

# Very large population (uses instant statistical mode)
tn-lottery simulate-group --players 100000

# Force a specific simulation mode
tn-lottery simulate-group --players 5000 --mode parallel
tn-lottery simulate-group --players 1000 --mode exact
tn-lottery simulate-group --players 100000 --mode statistical
```

**Multi-Player Options:**
- `--players` - Number of people to simulate (required)
- `--plays-per-player` - Plays per person (default: 1)
- `--cost-per-play` - Cost per play in dollars (default: $2.00)
- `--mode` - Simulation mode: auto, exact, parallel, or statistical (default: auto)

**Simulation Modes:**

The simulator intelligently selects the best mode based on population size:

- **Exact** (< 1,000 players): Full individual simulation with complete statistics
- **Parallel** (1,000-10,000 players): Multi-core processing for 8x speedup
- **Statistical** (10,000+ players): Instant probabilistic estimation (1000x+ speedup)
- **Auto** (default): Automatically selects the best mode for your population size

**Features:**
- Comprehensive population-level statistics
- ROI distribution histogram with 7 buckets
- Percentile analysis (25th, 50th, 75th, 90th, 95th, 99th)
- Best/worst player tracking
- Enhanced jackpot winner celebration
- Educational insights about probability concepts
- **Performance:** Can simulate 1,000,000 players in ~0.3 seconds!

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

## Technical Details

### Simulation Methodology

The simulator uses scientifically accurate probability models:

**Individual Mode:**
- Plays according to actual Powerball draw schedule (2x per week: Wed & Sat)
- Tracks all 9 prize tiers with correct odds
- Accounts for realistic win rates (~25% of plays win something)
- Provides detailed spending analysis and ROI calculations

**Multi-Player Mode:**
- **Exact mode:** Full Monte Carlo simulation with complete tracking
- **Parallel mode:** Leverages multi-core CPUs for faster processing
- **Statistical mode:** Uses probability distributions for instant results on large populations
- All modes produce statistically equivalent results

### Database & Scraping

The scraper collects winner data from:
- TN Lottery website
- Powerball.com

Data is stored in a SQLite database and used to calculate:
- Most commonly won games
- Average payouts by game
- Jackpot timelines and trends

## Development

### Running Tests

```bash
# Run with pytest (if tests are added)
pytest

# Run specific test file
pytest tests/test_simulation.py
```

### Project Structure

```
tn_lottery/
├── cli.py              # Main CLI entry point
├── play.py             # Number generation
├── simulation.py       # Individual simulation
├── group_simulation.py # Multi-player simulation
├── scraper.py          # Data scraping
├── db.py               # Database management
└── games.py            # Game definitions
```

## License

See [LICENSE](LICENSE) file for details.

## Disclaimer

*This tool is for educational and entertainment purposes only. You'll likely just lose your money. Please gamble responsibly.*
