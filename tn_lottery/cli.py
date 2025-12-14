#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TN Lottery CLI - Unified command-line interface for TN Lottery tools.
"""
import sys
import rich_click as click
from rich.console import Console
from rich.table import Table

from tn_lottery.lottery import Lottery
from tn_lottery import simulation
from tn_lottery.db import init_db, get_db, DB_PATH

console = Console()


@click.group()
def cli():
    """TN Lottery tools for generating numbers, simulating games, and analyzing data."""
    pass


@cli.command(name='db-path')
def show_db_path():
    """Show the database file location."""
    console.print(f"[bold]Database location:[/bold] {DB_PATH}")
    console.print(f"\nYou can change this by setting the TN_LOTTERY_DB environment variable.")
    console.print(f"Example: export TN_LOTTERY_DB=/path/to/custom/lottery.db")


@cli.command()
@click.option('-g', '--game', type=str, help="Play a single game (see 'tn-lottery games' for list)")
@click.option('-n', '--number', type=int, default=1, help="Number of plays to generate")
def play(game, number):
    """Generate random numbers for TN Lottery games."""
    from tn_lottery.play import generate_numbers
    generate_numbers(game, number)


@cli.command()
def games():
    """List available lottery games."""
    from tn_lottery.play import list_games
    list_games()


@cli.command()
@click.option(
    '--plays-per-week',
    type=int,
    default=2,
    help="How many times per week to play (default: 2)"
)
@click.option(
    '--plays-per-ticket',
    type=int,
    default=5,
    help="Number of play sets per ticket (default: 5)"
)
@click.option(
    '--cost-per-play',
    type=float,
    default=2.0,
    help="Cost per individual play in dollars (default: $2.00)"
)
@click.option(
    '--duration',
    type=int,
    default=0,
    help="Years to simulate (0 = until jackpot) (default: 0)"
)
@click.option(
    '--report-interval',
    type=int,
    default=10,
    help="Years between progress reports (default: 10)"
)
def simulate(plays_per_week, plays_per_ticket, cost_per_play, duration, report_interval):
    """Run a Powerball simulation with configurable parameters."""
    from tn_lottery.simulation import run_simulation
    run_simulation(
        plays_per_week=plays_per_week,
        plays_per_ticket=plays_per_ticket,
        cost_per_play=cost_per_play,
        duration_years=duration,
        report_interval=report_interval
    )


@cli.command(name='simulate-group')
@click.option(
    '--players',
    type=int,
    default=100,
    help="Number of players to simulate (default: 100)"
)
@click.option(
    '--plays-per-player',
    type=int,
    default=5,
    help="Number of plays each player makes (default: 5)"
)
@click.option(
    '--cost-per-play',
    type=float,
    default=2.0,
    help="Cost per individual play in dollars (default: $2.00)"
)
@click.option(
    '--mode',
    type=click.Choice(['auto', 'exact', 'parallel', 'statistical'], case_sensitive=False),
    default='auto',
    help="Simulation mode: auto (default), exact, parallel, or statistical"
)
def simulate_group_command(players, plays_per_player, cost_per_play, mode):
    """Simulate multiple people playing the lottery simultaneously.
    
    This shows population-level statistics and helps understand:
    - What percentage of players profit vs lose
    - How winnings are distributed across a population
    - Law of large numbers in action
    - Variance between individual luck and population trends
    
    Simulation modes:
    - Auto: Automatically selects best mode based on population size
    - Exact: Simulates each player individually (best for < 1,000)
    - Parallel: Uses multiple CPU cores (best for 1,000-10,000)
    - Statistical: Fast probability-based estimation (best for 10,000+)
    
    Examples:
      tn-lottery simulate-group --players 100
      tn-lottery simulate-group --players 1000 --plays-per-player 3
      tn-lottery simulate-group --players 50 --cost-per-play 5.0
      tn-lottery simulate-group --players 100000 --mode statistical
      tn-lottery simulate-group --players 5000 --mode parallel
    """
    from tn_lottery.multiplayer import (
        simulate_population_auto, 
        simulate_population,
        simulate_population_parallel,
        simulate_population_statistical,
        print_population_results
    )
    
    # Select simulation mode
    if mode == 'auto':
        result, mode_name = simulate_population_auto(
            num_players=players,
            plays_per_player=plays_per_player,
            cost_per_play=cost_per_play,
            show_progress=True
        )
    elif mode == 'exact':
        result = simulate_population(
            num_players=players,
            plays_per_player=plays_per_player,
            cost_per_play=cost_per_play,
            show_progress=True
        )
        mode_name = "Exact Simulation"
    elif mode == 'parallel':
        result = simulate_population_parallel(
            num_players=players,
            plays_per_player=plays_per_player,
            cost_per_play=cost_per_play,
            show_progress=True
        )
        mode_name = "Parallel Simulation"
    else:  # statistical
        result = simulate_population_statistical(
            num_players=players,
            plays_per_player=plays_per_player,
            cost_per_play=cost_per_play
        )
        mode_name = "Statistical Estimation"
    
    # Display results
    print_population_results(result, plays_per_player, cost_per_play, mode_name)


@cli.group()
def scrape():
    """Scrape lottery winner data from various sources."""
    init_db()


@scrape.command(name='tn')
def scrape_tn():
    """Scrape TN Lottery winners to database."""
    from tn_lottery.scraper import scrape_tn_lottery
    scrape_tn_lottery()


@scrape.command(name='powerball')
def scrape_powerball():
    """Scrape Powerball winners to database."""
    from tn_lottery.scraper import scrape_powerball_data
    scrape_powerball_data()


@cli.command()
def report():
    """Generate statistics report from scraped data."""
    from tn_lottery.scraper import generate_report
    generate_report()


@cli.command()
def timeline():
    """Show Powerball jackpot timeline."""
    from tn_lottery.scraper import show_timeline
    show_timeline()


if __name__ == "__main__":
    cli()
