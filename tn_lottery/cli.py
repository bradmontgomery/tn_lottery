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
from tn_lottery.db import init_db, get_db

console = Console()


@click.group()
def cli():
    """TN Lottery tools for generating numbers, simulating games, and analyzing data."""
    pass


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
def simulate():
    """Run a Powerball simulation until jackpot is won."""
    from tn_lottery.simulation import run_simulation
    run_simulation()


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
