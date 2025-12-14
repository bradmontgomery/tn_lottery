# TODO

## Build a simulator

Inputs:
- How often the game is played (e.g. 2 times / week for powerball)
- How much a ticket costs (and how many you play at a time?)
- How long you want to play (e.g. play for 20 years). Assume you play every
  time the game runs. (forever mode: keep playing until we hit the jackpot)

Output:
- How much money you've spent
- How much you've won.
- How long it takes to win? (e.g. how many years to hit the jackpot)
- Print the output in a text table.

Would be cool to see a graph of money spent vs. winnings over time.
- assuming we count minor winnings (match PB, match 2/5 etc).
- For examples of ways to win: http://goo.gl/2UT2jq

## Refactor to Single Entry Point CLI

**Goal:** Consolidate `play.py`, `scraper.py`, and `simulation.py` into a single `tn-lottery` CLI application using `rich-click`.

**Proposed CLI Structure:**
- `tn-lottery` (Main Group)
    - `play`: Generate random numbers for games.
        - Options: `--game`, `--number`
    - `games`: List available games (extracted from `play.py`).
    - `simulate`: Run the Powerball simulation.
    - `scrape` (Group)
        - `tn`: Scrape TN Lottery data.
        - `powerball`: Scrape Powerball data.
    - `report`: Generate statistics report from database.
    - `timeline`: Show Powerball jackpot timeline.

**Implementation Steps:**
1.  [ ] **Create `tn_lottery/cli.py`**: Initialize the main `click` group.
2.  [ ] **Refactor `play.py`**:
    -   Expose `play` logic as a function.
    -   Expose `list_games` logic as a function.
    -   Integrate into `cli.py` as `play` and `games` commands.
3.  [ ] **Refactor `simulation.py`**:
    -   Expose the simulation logic as a function.
    -   Integrate into `cli.py` as `simulate` command.
4.  [ ] **Refactor `scraper.py`**:
    -   Move `scrape_tn`, `scrape_powerball`, `report`, and `timeline` logic into reusable functions (remove internal `click` group).
    -   Integrate into `cli.py` (create a `scrape` group for the scrapers).
5.  [ ] **Update `pyproject.toml`**:
    -   Add `[project.scripts]` section.
    -   Define `tn-lottery = "tn_lottery.cli:cli"`.
6.  [ ] **Cleanup**: Remove `if __name__ == "__main__":` blocks from old files and ensure they are treated as modules.
7.  [ ] **Verification**: Test all subcommands.
