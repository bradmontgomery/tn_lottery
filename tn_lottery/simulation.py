#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Powerball Simulator

Simulates playing the lottery over time to understand the financial impact.
Supports configurable parameters and tracks all prize tiers for realistic modeling.
"""

import rich_click as click
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from tn_lottery.lottery import Lottery
from tn_lottery.payouts import calculate_payout, get_tier_display_info

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


def play_drawing(lotto, plays_per_ticket, cost_per_play):
    """Execute one lottery drawing with prize tier tracking.
    
    Args:
        lotto: Lottery instance
        plays_per_ticket: Number of plays per ticket
        cost_per_play: Cost per individual play
        
    Returns:
        Tuple of (winnings: float, wins_by_tier: dict, won_jackpot: bool, cost: float)
    """
    plays, cost = generate_ticket(lotto, plays_per_ticket, cost_per_play)
    winning_numbers = lotto.powerball()
    
    # Calculate winnings and track prize tiers
    winnings, wins_by_tier, won_jackpot = calculate_payout(plays, winning_numbers)
    
    return (winnings, wins_by_tier, won_jackpot, cost)

def print_progress(draws, spent, won_total, wins_by_tier, years_interval, won_jackpot=False):
    """Print progress report during simulation.
    
    Args:
        draws: Number of drawings played
        spent: Total amount spent
        won_total: Total amount won (excluding jackpot)
        wins_by_tier: Dictionary of wins by tier name
        years_interval: Years represented by the interval
        won_jackpot: Whether jackpot was won
    """
    if won_jackpot:
        console.print("[bold green]🎉 YOU WON THE JACKPOT! 🎉[/bold green]")
    
    years = draws / 52 / 2  # 2 draws per week, 52 weeks per year
    net = won_total - spent
    roi = (won_total / spent * 100) if spent > 0 else 0
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("Years:", f"{years:.1f}")
    table.add_row("Draws:", f"{draws:,}")
    table.add_row("Spent:", f"${spent:,.2f}")
    table.add_row("Won:", f"${won_total:,.2f}")
    table.add_row("Net:", f"[{'green' if net >= 0 else 'red'}]${net:,.2f}[/]")
    table.add_row("ROI:", f"{roi:.1f}%")
    console.print(table)
    console.print()


def print_final_summary(draws, spent, won_total, all_wins_by_tier, won_jackpot, plays_per_week):
    """Print comprehensive final summary of simulation.
    
    Args:
        draws: Total number of drawings played
        spent: Total amount spent
        won_total: Total amount won (excluding jackpot)
        all_wins_by_tier: Dictionary of all wins by tier name
        won_jackpot: Whether jackpot was won
        plays_per_week: Number of plays per week
    """
    years_played = draws / 52 / plays_per_week
    net = won_total - spent
    roi = (won_total / spent * 100) if spent > 0 else 0
    total_wins = sum(all_wins_by_tier.values())
    
    console.print("\n" + "=" * 70)
    console.print("[bold blue]SIMULATION COMPLETE[/bold blue]".center(70))
    console.print("=" * 70 + "\n")
    
    # Overall Statistics
    console.print("[bold]Overall Statistics:[/bold]")
    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="yellow")
    stats_table.add_row("Total Draws:", f"{draws:,}")
    stats_table.add_row("Years Played:", f"{years_played:.2f}")
    stats_table.add_row("Total Spent:", f"${spent:,.2f}")
    stats_table.add_row("Total Won:", f"${won_total:,.2f}")
    stats_table.add_row("Net Profit/Loss:", f"[{'green' if net >= 0 else 'red'}]${net:,.2f}[/]")
    stats_table.add_row("ROI:", f"{roi:.1f}%")
    stats_table.add_row("Won Jackpot:", "[green]Yes! 🎉[/green]" if won_jackpot else "[red]No[/red]")
    stats_table.add_row("Total Wins:", f"{total_wins:,}")
    console.print(stats_table)
    console.print()
    
    # Wins Breakdown by Tier
    if all_wins_by_tier:
        console.print("[bold]Wins Breakdown by Prize Tier:[/bold]")
        wins_table = Table(show_header=True, header_style="bold magenta")
        wins_table.add_column("Prize Tier", style="cyan")
        wins_table.add_column("Count", justify="right", style="yellow")
        wins_table.add_column("Prize Amount", justify="right", style="green")
        wins_table.add_column("Total Won", justify="right", style="green")
        
        # Get all prize tier info for display
        tier_info = {name: prize for name, prize in get_tier_display_info()}
        
        # Display in order of prize tiers
        for tier_name, prize_str in get_tier_display_info():
            count = all_wins_by_tier.get(tier_name, 0)
            if count > 0 or tier_name == "Jackpot":  # Always show jackpot
                if tier_name == "Jackpot" and won_jackpot:
                    wins_table.add_row(
                        tier_name,
                        "1",
                        prize_str,
                        "🎰 JACKPOT! 🎰",
                        style="bold gold1"
                    )
                elif tier_name == "Jackpot":
                    wins_table.add_row(
                        tier_name,
                        "0",
                        prize_str,
                        "$0",
                        style="dim"
                    )
                else:
                    # Extract numeric prize from display string
                    prize_amount = int(prize_str.replace("$", "").replace(",", ""))
                    total = count * prize_amount
                    wins_table.add_row(
                        tier_name,
                        f"{count:,}",
                        prize_str,
                        f"${total:,}"
                    )
        
        console.print(wins_table)
        console.print()
    
    # Win Rate Statistics
    win_rate = (total_wins / draws * 100) if draws > 0 else 0
    console.print(f"[bold]Win Rate:[/bold] {win_rate:.2f}% ({total_wins:,} wins in {draws:,} draws)")
    console.print()
    
    # Reality Check
    if not won_jackpot and draws > 1000:
        expected_roi = 0.50  # ~50% return on investment for Powerball (excluding jackpot)
        console.print(Panel(
            f"[yellow]Reality Check:[/yellow]\n\n"
            f"You played {draws:,} times and spent ${spent:,.2f}.\n"
            f"Your actual ROI was {roi:.1f}%, which is typical.\n\n"
            f"Powerball's expected return (excluding jackpot) is about {expected_roi*100:.0f}%.\n"
            f"This means for every $2 spent, you typically get back ~${expected_roi*2:.2f}.\n\n"
            f"The odds of winning the jackpot are 1 in 292,201,338.\n"
            f"[bold]Playing the lottery is entertainment, not investment.[/bold]",
            title="📊 Analysis",
            border_style="yellow"
        ))
    elif won_jackpot:
        console.print(Panel(
            f"[green]Congratulations![/green]\n\n"
            f"You won the jackpot after {years_played:.1f} years!\n"
            f"However, you spent ${spent:,.2f} to get there.\n\n"
            f"[bold]The odds were 1 in 292,201,338.[/bold]\n"
            f"You got incredibly lucky!",
            title="🎰 Jackpot Winner!",
            border_style="green"
        ))
    console.print()



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
    won_total = 0.0
    draws = 0
    won_jackpot = False
    all_wins_by_tier = defaultdict(int)
    
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
            # Play one drawing with prize tier tracking
            winnings, wins_by_tier, won_jackpot, cost = play_drawing(
                lotto, plays_per_ticket, cost_per_play
            )
            
            # Update totals
            spent += cost
            won_total += winnings
            draws += 1
            
            # Track wins by tier
            for tier_name, count in wins_by_tier.items():
                all_wins_by_tier[tier_name] += count
            
            # Check if we've hit the time limit
            if max_draws and draws >= max_draws:
                console.print(f"\n[yellow]Reached {duration_years} year limit without winning jackpot[/yellow]\n")
                break
            
            # Print progress reports
            if draws % report_frequency == 0:
                print_progress(draws, spent, won_total, all_wins_by_tier, report_interval, False)
        
        # Final comprehensive summary
        print_final_summary(draws, spent, won_total, all_wins_by_tier, won_jackpot, plays_per_week)
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Simulation interrupted by user[/yellow]\n")
        print_final_summary(draws, spent, won_total, all_wins_by_tier, won_jackpot, plays_per_week)


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
