#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Powerball Simulator

Simulates playing the lottery over time to understand the financial impact.
Supports configurable parameters for realistic modeling.
"""

import rich_click as click
from rich.console import Console
from rich.table import Table
from tn_lottery.lottery import Lottery

console = Console()

# Default values
DEFAULT_COST_PER_PLAY = 2.0
DEFAULT_PLAYS_PER_TICKET = 5
DEFAULT_PLAYS_PER_WEEK = 2
DEFAULT_DURATION_YEARS = 0  # 0 = forever (until jackpot)
DEFAULT_REPORT_INTERVAL = 10  # Report every N years


def generate_ticket(lotto, plays, cost_per_play):
    """Generate a 'play ticket' consisting of numbers to play.

    Args:
        lotto: An instance of the Lottery class
        plays: The number of plays to generate (i.e. the set of numbers)
        cost_per_play: How much a single play costs

    Returns:
        Tuple of (list of powerball numbers, total cost)
    """
    numbers = []
    for i in range(plays):
        numbers.append(lotto.powerball())
    return (numbers, plays * cost_per_play)


def check_win(plays, winning_numbers):
    """Check if the given plays match any of the winning numbers.

    Args:
        plays: List of powerball play tuples
        winning_numbers: A powerball play tuple

    A powerball play tuple contains a list of 5 numbers followed by a
    powerball number. e.g. ([6, 20, 21, 52, 55], 27)

    Returns:
        Boolean indicating if any play matches the winning numbers
    """
    return winning_numbers in plays


def play_drawing(lotto, plays_per_ticket, cost_per_play):
    """Execute one lottery drawing.
    
    Args:
        lotto: Lottery instance
        plays_per_ticket: Number of plays per ticket
        cost_per_play: Cost per individual play
        
    Returns:
        Tuple of (won_jackpot: bool, cost: float)
    """
    plays, cost = generate_ticket(lotto, plays_per_ticket, cost_per_play)
    winning_numbers = lotto.powerball()
    return (check_win(plays, winning_numbers), cost)


def print_progress(draws, spent, years_interval, won=False):
    """Print progress report during simulation.
    
    Args:
        draws: Number of drawings played
        spent: Total amount spent
        years_interval: Years represented by the interval
        won: Whether jackpot was won
    """
    if won:
        console.print("[bold green]YOU WON THE JACKPOT![/bold green]")
    
    years = draws / 52 / 2  # 2 draws per week, 52 weeks per year
    cost = f"${spent:,.2f}"
    console.print(f"[cyan]{years:.1f} Years ({draws:,} draws):[/cyan] [yellow]{cost} spent[/yellow]")


def run_simulation(
    plays_per_week=DEFAULT_PLAYS_PER_WEEK,
    plays_per_ticket=DEFAULT_PLAYS_PER_TICKET,
    cost_per_play=DEFAULT_COST_PER_PLAY,
    duration_years=DEFAULT_DURATION_YEARS,
    report_interval=DEFAULT_REPORT_INTERVAL
):
    """Run a Powerball simulation with configurable parameters.
    
    Args:
        plays_per_week: How many times per week to play (default: 2)
        plays_per_ticket: Number of play sets per ticket (default: 5)
        cost_per_play: Cost per individual play in dollars (default: 2.00)
        duration_years: How many years to simulate, 0 = until jackpot (default: 0)
        report_interval: Years between progress reports (default: 10)
    """
    lotto = Lottery()
    spent = 0.0
    draws = 0
    won_jackpot = False
    
    # Calculate stopping point
    max_draws = int(duration_years * 52 * plays_per_week) if duration_years > 0 else None
    
    # Calculate report frequency (in draws)
    draws_per_year = 52 * plays_per_week
    report_frequency = int(report_interval * draws_per_year)
    
    # Display simulation parameters
    console.print("\n[bold blue]Powerball Simulation Parameters[/bold blue]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("Plays per week:", str(plays_per_week))
    table.add_row("Plays per ticket:", str(plays_per_ticket))
    table.add_row("Cost per play:", f"${cost_per_play:.2f}")
    table.add_row("Cost per week:", f"${plays_per_week * plays_per_ticket * cost_per_play:.2f}")
    table.add_row("Duration:", "Until jackpot" if duration_years == 0 else f"{duration_years} years")
    table.add_row("Report every:", f"{report_interval} years")
    console.print(table)
    console.print()
    
    try:
        while not won_jackpot:
            # Play one drawing
            won_jackpot, cost = play_drawing(lotto, plays_per_ticket, cost_per_play)
            spent += cost
            draws += 1
            
            # Check if we've hit the time limit
            if max_draws and draws >= max_draws:
                console.print(f"\n[yellow]Reached {duration_years} year limit without winning jackpot[/yellow]")
                break
            
            # Print progress reports
            if draws % report_frequency == 0:
                print_progress(draws, spent, report_interval, False)
        
        # Final report
        if won_jackpot:
            console.print()
            print_progress(draws, spent, report_interval, True)
        
        # Summary
        years_played = draws / 52 / plays_per_week
        console.print("\n[bold]Simulation Complete[/bold]")
        summary = Table(show_header=False, box=None, padding=(0, 2))
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="yellow")
        summary.add_row("Total draws:", f"{draws:,}")
        summary.add_row("Years played:", f"{years_played:.2f}")
        summary.add_row("Total spent:", f"${spent:,.2f}")
        summary.add_row("Won jackpot:", "Yes! 🎉" if won_jackpot else "No")
        console.print(summary)
        console.print()
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Simulation interrupted by user[/yellow]")
        years_played = draws / 52 / plays_per_week
        console.print(f"Played {draws:,} draws over {years_played:.2f} years")
        console.print(f"Total spent: ${spent:,.2f}")
        console.print()


@click.command()
@click.option(
    '--plays-per-week',
    type=int,
    default=DEFAULT_PLAYS_PER_WEEK,
    help=f"How many times per week to play (default: {DEFAULT_PLAYS_PER_WEEK})"
)
@click.option(
    '--plays-per-ticket',
    type=int,
    default=DEFAULT_PLAYS_PER_TICKET,
    help=f"Number of play sets per ticket (default: {DEFAULT_PLAYS_PER_TICKET})"
)
@click.option(
    '--cost-per-play',
    type=float,
    default=DEFAULT_COST_PER_PLAY,
    help=f"Cost per individual play in dollars (default: ${DEFAULT_COST_PER_PLAY})"
)
@click.option(
    '--duration',
    type=int,
    default=DEFAULT_DURATION_YEARS,
    help=f"Years to simulate (0 = until jackpot) (default: {DEFAULT_DURATION_YEARS})"
)
@click.option(
    '--report-interval',
    type=int,
    default=DEFAULT_REPORT_INTERVAL,
    help=f"Years between progress reports (default: {DEFAULT_REPORT_INTERVAL})"
)
def run(plays_per_week, plays_per_ticket, cost_per_play, duration, report_interval):
    """Run a Powerball simulation with configurable parameters."""
    run_simulation(
        plays_per_week=plays_per_week,
        plays_per_ticket=plays_per_ticket,
        cost_per_play=cost_per_play,
        duration_years=duration,
        report_interval=report_interval
    )


if __name__ == "__main__":
    run()
