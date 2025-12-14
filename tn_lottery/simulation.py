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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from tn_lottery.lottery import Lottery
from tn_lottery.payouts import calculate_payout, get_tier_display_info

console = Console()

# Default values
DEFAULT_COST_PER_PLAY = 2.0
DEFAULT_PLAYS_PER_TICKET = 5
DEFAULT_PLAYS_PER_WEEK = 2
DEFAULT_DURATION_YEARS = 0  # 0 = forever (until jackpot)
DEFAULT_REPORT_INTERVAL = 10  # Report every N years


def create_simple_bar_chart(value, max_value, width=30):
    """Create a simple text-based bar chart.
    
    Args:
        value: Current value
        max_value: Maximum value for scaling
        width: Width of bar in characters
        
    Returns:
        String representation of bar
    """
    if max_value == 0:
        filled = 0
    else:
        filled = int((value / max_value) * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


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
    """Print enhanced progress report during simulation with visual elements.
    
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
    total_wins = sum(wins_by_tier.values())
    win_rate = (total_wins / draws * 100) if draws > 0 else 0
    
    # Create progress report table
    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    table.add_column("Progress Update", style="bold cyan")
    table.add_column("Value", justify="right", style="yellow")
    table.add_column("Visual", style="green")
    
    # Years
    table.add_row("Years:", f"{years:.1f}", "")
    
    # Draws with bar
    max_draws_display = draws
    draws_bar = create_simple_bar_chart(draws, max(draws, 1000), width=20)
    table.add_row("Draws:", f"{draws:,}", draws_bar)
    
    # Money spent
    table.add_row("Spent:", f"${spent:,.2f}", "")
    
    # Money won with bar showing vs spent
    won_bar = create_simple_bar_chart(won_total, spent, width=20)
    table.add_row("Won:", f"${won_total:,.2f}", won_bar)
    
    # Net (color coded)
    net_color = "green" if net >= 0 else "red"
    table.add_row("Net:", f"[{net_color}]${net:,.2f}[/]", "")
    
    # ROI with bar
    roi_bar = create_simple_bar_chart(max(0, roi), 100, width=20)
    table.add_row("ROI:", f"{roi:.1f}%", roi_bar)
    
    # Wins
    table.add_row("Total Wins:", f"{total_wins:,}", "")
    table.add_row("Win Rate:", f"{win_rate:.1f}%", "")
    
    console.print(table)
    console.print()


def print_final_summary(draws, spent, won_total, all_wins_by_tier, won_jackpot, plays_per_week):
    """Print comprehensive final summary with enhanced visualizations.
    
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
    
    # Overall Statistics with visual bars
    console.print("[bold]Overall Statistics:[/bold]")
    stats_table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", justify="right", style="yellow")
    stats_table.add_column("Visualization", style="green")
    
    stats_table.add_row("Total Draws:", f"{draws:,}", "")
    stats_table.add_row("Years Played:", f"{years_played:.2f}", "")
    stats_table.add_row("Total Spent:", f"${spent:,.2f}", "")
    
    # Won vs Spent visualization
    won_bar = create_simple_bar_chart(won_total, spent, width=25)
    stats_table.add_row("Total Won:", f"${won_total:,.2f}", won_bar)
    
    # Net profit/loss
    net_color = "green" if net >= 0 else "red"
    stats_table.add_row("Net Profit/Loss:", f"[{net_color}]${net:,.2f}[/]", "")
    
    # ROI with bar (capped at 100 for display)
    roi_bar = create_simple_bar_chart(max(0, min(roi, 100)), 100, width=25)
    stats_table.add_row("ROI:", f"{roi:.1f}%", roi_bar)
    
    stats_table.add_row("Won Jackpot:", "[green]Yes! 🎉[/green]" if won_jackpot else "[red]No[/red]", "")
    stats_table.add_row("Total Wins:", f"{total_wins:,}", "")
    console.print(stats_table)
    console.print()
    
    # Wins Breakdown by Tier with visual bars
    if all_wins_by_tier:
        console.print("[bold]Wins Breakdown by Prize Tier:[/bold]")
        wins_table = Table(show_header=True, header_style="bold magenta")
        wins_table.add_column("Prize Tier", style="cyan")
        wins_table.add_column("Count", justify="right", style="yellow")
        wins_table.add_column("Prize Amount", justify="right", style="green")
        wins_table.add_column("Total Won", justify="right", style="green")
        wins_table.add_column("Distribution", style="blue")
        
        # Get all prize tier info for display
        tier_info = {name: prize for name, prize in get_tier_display_info()}
        max_wins = max(all_wins_by_tier.values()) if all_wins_by_tier else 1
        
        # Display in order of prize tiers
        for tier_name, prize_str in get_tier_display_info():
            count = all_wins_by_tier.get(tier_name, 0)
            if count > 0 or tier_name == "Jackpot":  # Always show jackpot
                # Create distribution bar
                dist_bar = create_simple_bar_chart(count, max_wins, width=15)
                
                if tier_name == "Jackpot" and won_jackpot:
                    wins_table.add_row(
                        tier_name,
                        "1",
                        prize_str,
                        "🎰 JACKPOT! 🎰",
                        "🎊" * 15,
                        style="bold gold1"
                    )
                elif tier_name == "Jackpot":
                    wins_table.add_row(
                        tier_name,
                        "0",
                        prize_str,
                        "$0",
                        "░" * 15,
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
                        f"${total:,}",
                        dist_bar
                    )
        
        console.print(wins_table)
        console.print()
    
    # Win Rate Statistics with comparison
    win_rate = (total_wins / draws * 100) if draws > 0 else 0
    expected_win_rate = 4.0  # ~4% overall win probability for Powerball
    
    console.print("[bold]Win Statistics:[/bold]")
    win_stats_table = Table(show_header=False, box=None, padding=(0, 2))
    win_stats_table.add_column("Metric", style="cyan")
    win_stats_table.add_column("Your Result", style="yellow")
    win_stats_table.add_column("Expected", style="green")
    
    win_rate_bar = create_simple_bar_chart(win_rate, 30, width=15)
    win_stats_table.add_row(
        "Win Rate:",
        f"{win_rate:.2f}% ({total_wins:,}/{draws:,}) {win_rate_bar}",
        f"~{expected_win_rate:.1f}%"
    )
    
    roi_bar = create_simple_bar_chart(max(0, roi), 100, width=15)
    win_stats_table.add_row(
        "ROI:",
        f"{roi:.1f}% {roi_bar}",
        "~50%"
    )
    
    avg_win = won_total / total_wins if total_wins > 0 else 0
    win_stats_table.add_row(
        "Avg Win Amount:",
        f"${avg_win:.2f}",
        "~$4-5"
    )
    
    console.print(win_stats_table)
    console.print()
    
    # Spending Analysis
    if years_played > 0:
        console.print("[bold]Spending Analysis:[/bold]")
        spending_table = Table(show_header=False, box=None, padding=(0, 2))
        spending_table.add_column("Period", style="cyan")
        spending_table.add_column("Amount", justify="right", style="yellow")
        
        cost_per_week = spent / (years_played * 52)
        cost_per_month = spent / (years_played * 12)
        cost_per_year = spent / years_played
        
        spending_table.add_row("Per Week:", f"${cost_per_week:.2f}")
        spending_table.add_row("Per Month:", f"${cost_per_month:.2f}")
        spending_table.add_row("Per Year:", f"${cost_per_year:.2f}")
        
        console.print(spending_table)
        console.print()
    
    # Reality Check
    if not won_jackpot and draws > 100:
        expected_roi = 0.50  # ~50% return on investment for Powerball (excluding jackpot)
        
        # Calculate what percentage through to expected jackpot win
        jackpot_odds = 292_201_338
        progress_to_jackpot = (draws / jackpot_odds) * 100
        
        console.print(Panel(
            f"[yellow]Reality Check:[/yellow]\n\n"
            f"You played {draws:,} times and spent ${spent:,.2f}.\n"
            f"Your actual ROI was {roi:.1f}%, which is {'above' if roi > 50 else 'below' if roi < 50 else 'at'} typical.\n\n"
            f"Powerball's expected return (excluding jackpot) is about {expected_roi*100:.0f}%.\n"
            f"This means for every $2 spent, you typically get back ~${expected_roi*2:.2f}.\n\n"
            f"The odds of winning the jackpot are 1 in {jackpot_odds:,}.\n"
            f"You've played {progress_to_jackpot:.4f}% of the way to expected jackpot.\n\n"
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
            f"You got incredibly lucky!\n\n"
            f"In reality, this would take approximately:\n"
            f"• 2.8 million years playing 2x/week\n"
            f"• Or cost ~$584 million buying all combinations",
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
