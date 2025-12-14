# TN lotto

Tools to generate random numbers for the [Tennessee lottery](http://www.tnlottery.com), and a very simple powerball simulator.

## Supported Games

* Powerball
* Mega Millions
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

```bash
tn-lottery simulate
```

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
