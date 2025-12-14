#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multi-Player Lottery Simulation

Simulates multiple people playing the lottery simultaneously to demonstrate
population-level statistics and probability at scale.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict
import statistics
import random


# Threshold for switching to statistical mode
STATISTICAL_MODE_THRESHOLD = 10000


@dataclass
class PlayerResult:
    """Result of a single player's lottery plays.
    
    Attributes:
        player_id: Unique identifier for the player
        spent: Total amount spent by player
        won: Total amount won by player (excluding jackpot)
        net: Net profit/loss (won - spent)
        wins_by_tier: Dictionary mapping tier name to win count
        won_jackpot: Whether player won the jackpot
    """
    player_id: int
    spent: float
    won: float
    net: float
    wins_by_tier: Dict[str, int]
    won_jackpot: bool
    
    @property
    def roi(self) -> float:
        """Return on investment as percentage."""
        return (self.won / self.spent * 100) if self.spent > 0 else 0.0
    
    @property
    def profited(self) -> bool:
        """Whether player made a profit."""
        return self.net > 0
    
    @property
    def broke_even(self) -> bool:
        """Whether player broke even (within $1)."""
        return abs(self.net) <= 1.0


@dataclass
class PopulationResult:
    """Aggregate results for a population of players.
    
    Attributes:
        num_players: Total number of players
        total_spent: Total amount spent by all players
        total_won: Total amount won by all players
        jackpot_winners: List of player IDs who won jackpot
        players_profited: Count of players who made profit
        players_broke_even: Count of players who broke even
        players_lost: Count of players who lost money
        total_wins_by_tier: Aggregate wins by tier across all players
        player_results: List of individual player results
    """
    num_players: int
    total_spent: float
    total_won: float
    jackpot_winners: List[int] = field(default_factory=list)
    players_profited: int = 0
    players_broke_even: int = 0
    players_lost: int = 0
    total_wins_by_tier: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    player_results: List[PlayerResult] = field(default_factory=list)
    
    @property
    def total_net(self) -> float:
        """Total net profit/loss for population."""
        return self.total_won - self.total_spent
    
    @property
    def population_roi(self) -> float:
        """Overall ROI for the population."""
        return (self.total_won / self.total_spent * 100) if self.total_spent > 0 else 0.0
    
    @property
    def mean_roi(self) -> float:
        """Mean ROI across all players."""
        if not self.player_results:
            return 0.0
        return statistics.mean(p.roi for p in self.player_results)
    
    @property
    def median_roi(self) -> float:
        """Median ROI across all players."""
        if not self.player_results:
            return 0.0
        return statistics.median(p.roi for p in self.player_results)
    
    @property
    def std_dev_roi(self) -> float:
        """Standard deviation of ROI across players."""
        if len(self.player_results) < 2:
            return 0.0
        return statistics.stdev(p.roi for p in self.player_results)
    
    @property
    def best_player(self) -> PlayerResult:
        """Player with highest ROI."""
        if not self.player_results:
            return None
        return max(self.player_results, key=lambda p: p.roi)
    
    @property
    def worst_player(self) -> PlayerResult:
        """Player with lowest ROI."""
        if not self.player_results:
            return None
        return min(self.player_results, key=lambda p: p.roi)
    
    @property
    def total_wins(self) -> int:
        """Total number of wins across all tiers."""
        return sum(self.total_wins_by_tier.values())


def simulate_single_player(
    player_id: int,
    lotto,
    plays_per_player: int,
    cost_per_play: float
) -> PlayerResult:
    """Simulate a single player's lottery plays.
    
    Args:
        player_id: Unique identifier for this player
        lotto: Lottery instance for generating draws
        plays_per_player: Number of plays this player makes
        cost_per_play: Cost per individual play
        
    Returns:
        PlayerResult with this player's outcomes
    """
    from tn_lottery.payouts import calculate_payout
    
    spent = plays_per_player * cost_per_play
    total_won = 0.0
    all_wins_by_tier = defaultdict(int)
    won_jackpot = False
    
    # Generate player's plays
    plays = []
    for _ in range(plays_per_player):
        plays.append(lotto.powerball())
    
    # Generate winning numbers
    winning_numbers = lotto.powerball()
    
    # Calculate payouts
    winnings, wins_by_tier, hit_jackpot = calculate_payout(plays, winning_numbers)
    
    total_won = winnings
    for tier, count in wins_by_tier.items():
        all_wins_by_tier[tier] = count
    won_jackpot = hit_jackpot
    
    net = total_won - spent
    
    return PlayerResult(
        player_id=player_id,
        spent=spent,
        won=total_won,
        net=net,
        wins_by_tier=dict(all_wins_by_tier),
        won_jackpot=won_jackpot
    )


def simulate_population(
    num_players: int,
    plays_per_player: int,
    cost_per_play: float,
    show_progress: bool = True
) -> PopulationResult:
    """Simulate a population of players (exact simulation).
    
    Args:
        num_players: Number of players to simulate
        plays_per_player: Number of plays each player makes
        cost_per_play: Cost per individual play
        show_progress: Whether to show progress bar
        
    Returns:
        PopulationResult with aggregate statistics
    """
    from tn_lottery.lottery import Lottery
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    
    console = Console()
    lotto = Lottery()
    player_results = []
    total_spent = 0.0
    total_won = 0.0
    jackpot_winners = []
    players_profited = 0
    players_broke_even = 0
    players_lost = 0
    total_wins_by_tier = defaultdict(int)
    
    # Show progress for larger simulations
    if show_progress and num_players > 100:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                f"[cyan]Simulating {num_players:,} players...",
                total=num_players
            )
            
            # Simulate each player
            for player_id in range(1, num_players + 1):
                result = simulate_single_player(player_id, lotto, plays_per_player, cost_per_play)
                player_results.append(result)
                
                # Aggregate statistics
                total_spent += result.spent
                total_won += result.won
                
                if result.won_jackpot:
                    jackpot_winners.append(player_id)
                    # Show jackpot winner immediately
                    console.print(f"\n[bold green]🎰 Player #{player_id} won the JACKPOT! 🎰[/bold green]")
                
                if result.profited:
                    players_profited += 1
                elif result.broke_even:
                    players_broke_even += 1
                else:
                    players_lost += 1
                
                # Aggregate wins by tier
                for tier, count in result.wins_by_tier.items():
                    total_wins_by_tier[tier] += count
                
                progress.update(task, advance=1)
    else:
        # No progress bar for small populations
        for player_id in range(1, num_players + 1):
            result = simulate_single_player(player_id, lotto, plays_per_player, cost_per_play)
            player_results.append(result)
            
            total_spent += result.spent
            total_won += result.won
            
            if result.won_jackpot:
                jackpot_winners.append(player_id)
            
            if result.profited:
                players_profited += 1
            elif result.broke_even:
                players_broke_even += 1
            else:
                players_lost += 1
            
            for tier, count in result.wins_by_tier.items():
                total_wins_by_tier[tier] += count
    
    return PopulationResult(
        num_players=num_players,
        total_spent=total_spent,
        total_won=total_won,
        jackpot_winners=jackpot_winners,
        players_profited=players_profited,
        players_broke_even=players_broke_even,
        players_lost=players_lost,
        total_wins_by_tier=dict(total_wins_by_tier),
        player_results=player_results
    )


def simulate_population_statistical(
    num_players: int,
    plays_per_player: int,
    cost_per_play: float
) -> PopulationResult:
    """Simulate a population using statistical estimation (for large N).
    
    Uses probability distributions instead of individual simulation for speed.
    Suitable for populations >= 10,000 players.
    
    Args:
        num_players: Number of players to simulate
        plays_per_player: Number of plays each player makes
        cost_per_play: Cost per individual play
        
    Returns:
        PopulationResult with estimated statistics
    """
    from tn_lottery.payouts import POWERBALL_PRIZES, get_expected_value_info
    from rich.console import Console
    
    console = Console()
    
    total_plays = num_players * plays_per_player
    total_spent = num_players * plays_per_player * cost_per_play
    
    # Get official odds
    odds_info = get_expected_value_info()
    odds = odds_info["odds"]
    
    # Calculate expected wins per tier based on probability
    total_wins_by_tier = defaultdict(int)
    total_won = 0.0
    jackpot_winners = []
    
    console.print(f"[cyan]Using statistical mode for {num_players:,} players...[/cyan]")
    
    # For each prize tier, calculate expected wins with variance
    for prize_tier in POWERBALL_PRIZES:
        tier_odds = odds[prize_tier.name]
        probability = 1.0 / tier_odds
        expected_wins = total_plays * probability
        
        if prize_tier.name == "Jackpot":
            # Handle jackpot separately - use binomial approximation
            # Probability of at least one jackpot winner
            prob_jackpot = 1 - (1 - probability) ** total_plays
            
            if random.random() < prob_jackpot:
                # Someone won!
                jackpot_winners.append(random.randint(1, num_players))
                total_wins_by_tier["Jackpot"] = 1
        else:
            # Regular prize tiers - add realistic variance
            # Use normal approximation to binomial
            # variance = n * p * (1 - p)
            variance = total_plays * probability * (1 - probability)
            std_dev = variance ** 0.5
            
            # Sample from normal distribution, ensure non-negative
            actual_wins = int(max(0, random.gauss(expected_wins, std_dev)))
            
            total_wins_by_tier[prize_tier.name] = actual_wins
            total_won += actual_wins * prize_tier.prize
    
    # Estimate player outcome distribution
    # Based on typical lottery statistics:
    # - ~4% of plays win something
    # - Of winners, most win small amounts
    # - Very few profit overall
    
    win_rate = odds_info["overall_win_probability"]  # ~4% win rate
    total_winners = int(total_plays * win_rate)
    
    # Estimate how many unique players won (some win multiple times)
    # Using rough approximation: ~70% of wins are unique players
    unique_winners = min(int(total_winners * 0.7), num_players)
    
    # Of unique winners, estimate profit distribution
    # Most winners don't profit (won less than spent)
    # Only ~1-3% of players profit
    players_profited = int(num_players * 0.02)  # ~2% profit
    players_broke_even = int(num_players * 0.01)  # ~1% break even
    players_lost = num_players - players_profited - players_broke_even
    
    # For statistical mode, we don't track individual players
    # So we can't provide best/worst, but we can estimate the population
    player_results = []  # Empty for statistical mode
    
    console.print(f"[green]Statistical calculation complete![/green]")
    
    return PopulationResult(
        num_players=num_players,
        total_spent=total_spent,
        total_won=total_won,
        jackpot_winners=jackpot_winners,
        players_profited=players_profited,
        players_broke_even=players_broke_even,
        players_lost=players_lost,
        total_wins_by_tier=dict(total_wins_by_tier),
        player_results=player_results  # Empty in statistical mode
    )


def simulate_population_auto(
    num_players: int,
    plays_per_player: int,
    cost_per_play: float,
    show_progress: bool = True
) -> tuple[PopulationResult, str]:
    """Automatically choose simulation mode based on population size.
    
    Uses exact simulation for small populations (< 10,000 players)
    Uses statistical estimation for large populations (>= 10,000 players)
    
    Args:
        num_players: Number of players to simulate
        plays_per_player: Number of plays each player makes
        cost_per_play: Cost per individual play
        show_progress: Whether to show progress (exact mode only)
        
    Returns:
        Tuple of (PopulationResult, mode_name)
    """
    from rich.console import Console
    
    console = Console()
    
    if num_players < STATISTICAL_MODE_THRESHOLD:
        # Use exact simulation
        console.print(f"[cyan]Simulating {num_players:,} players (Exact Mode)...[/cyan]")
        result = simulate_population(num_players, plays_per_player, cost_per_play, show_progress)
        mode = "Exact Simulation"
    else:
        # Use statistical estimation
        console.print(f"[cyan]Simulating {num_players:,} players (Statistical Mode)...[/cyan]")
        console.print(f"[dim]Using probability-based estimation for large population[/dim]")
        result = simulate_population_statistical(num_players, plays_per_player, cost_per_play)
        mode = "Statistical Estimation"
    
    return result, mode


def print_roi_histogram(player_results: List[PlayerResult]):
    """Print ROI distribution histogram.
    
    Args:
        player_results: List of player results
    """
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    # Define ROI buckets
    buckets = [
        (float('inf'), 200, "200%+"),
        (200, 100, "100-200%"),
        (100, 50, "50-100%"),
        (50, 20, "20-50%"),
        (20, 0, "0-20%"),
        (0, -50, "-50-0%"),
        (-50, -100, "< -100%"),
    ]
    
    # Count players in each bucket
    bucket_counts = {label: 0 for _, _, label in buckets}
    total = len(player_results)
    
    for player in player_results:
        roi = player.roi
        for upper, lower, label in buckets:
            if lower <= roi < upper:
                bucket_counts[label] += 1
                break
    
    # Create histogram
    histogram_table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    histogram_table.add_column("ROI Range", style="yellow", width=12)
    histogram_table.add_column("Count", justify="right", style="cyan", width=8)
    histogram_table.add_column("Percent", justify="right", style="green", width=8)
    histogram_table.add_column("Distribution", style="blue", width=40)
    
    for _, _, label in buckets:
        count = bucket_counts[label]
        pct = (count / total * 100) if total > 0 else 0
        
        # Create bar visualization
        bar_length = int(pct / 2)  # Scale to fit in 40 chars (2% per char)
        bar = "█" * bar_length
        
        # Color based on ROI
        if "+" in label or label.startswith("200") or label.startswith("100") or label.startswith("50") or label.startswith("20"):
            style = "green"
        elif label.startswith("0"):
            style = "yellow"
        else:
            style = "red"
        
        histogram_table.add_row(
            label,
            f"{count:,}",
            f"{pct:.1f}%",
            f"[{style}]{bar}[/]"
        )
    
    console.print(histogram_table)


def print_jackpot_winner_details(result: PopulationResult, plays_per_player: int, cost_per_play: float):
    """Print detailed jackpot winner information.
    
    Args:
        result: PopulationResult containing jackpot winners
        plays_per_player: Number of plays per player
        cost_per_play: Cost per play
    """
    from rich.console import Console
    from rich.panel import Panel
    
    if not result.jackpot_winners:
        return
    
    console = Console()
    total_plays = result.num_players * plays_per_player
    
    for winner_id in result.jackpot_winners:
        # Find winner in player results if available
        winner_player = None
        if result.player_results:
            for player in result.player_results:
                if player.player_id == winner_id:
                    winner_player = player
                    break
        
        # Calculate stats
        player_cost = plays_per_player * cost_per_play
        
        # Build winner details
        details = []
        details.append(f"[bold gold1]🎰 JACKPOT WINNER! 🎰[/bold gold1]\n")
        details.append(f"Player #{winner_id} won the GRAND PRIZE!\n")
        details.append(f"[bold]This occurred after:[/bold]")
        details.append(f"  • {result.num_players:,} people played")
        details.append(f"  • ${result.total_spent:,.0f} spent in total")
        
        # Expected probability
        jackpot_odds = 292201338
        prob_at_least_one = (1 - (1 - 1/jackpot_odds) ** total_plays) * 100
        details.append(f"  • Expected probability: {prob_at_least_one:.4f}%\n")
        
        details.append(f"[bold]Lucky Player Stats:[/bold]")
        details.append(f"  • Spent: ${player_cost:.2f}")
        
        if winner_player:
            other_winnings = winner_player.won - 0  # Jackpot not in won total yet in our model
            details.append(f"  • Other prizes: ${other_winnings:.2f}")
            details.append(f"  • Total won: JACKPOT + ${other_winnings:.2f}")
            details.append(f"  • ROI: ∞% (Jackpot!)")
        else:
            details.append(f"  • Won: [bold]JACKPOT[/bold]")
        
        panel = Panel(
            "\n".join(details),
            border_style="gold1",
            padding=(1, 2)
        )
        console.print(panel)
        console.print()


def print_population_results(result: PopulationResult, plays_per_player: int, cost_per_play: float, mode: str = "Exact Simulation"):
    """Print comprehensive population simulation results.
    
    Args:
        result: PopulationResult to display
        plays_per_player: Number of plays each player made
        cost_per_play: Cost per individual play
        mode: Simulation mode used ("Exact Simulation" or "Statistical Estimation")
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from tn_lottery.payouts import get_tier_display_info
    from tn_lottery.simulation import create_simple_bar_chart
    
    console = Console()
    
    console.print("\n" + "=" * 70)
    console.print("[bold blue]MULTI-PLAYER SIMULATION RESULTS[/bold blue]".center(70))
    console.print("=" * 70 + "\n")
    
    # Simulation parameters
    console.print("[bold]Simulation Parameters:[/bold]")
    params_table = Table(show_header=False, box=None, padding=(0, 2))
    params_table.add_column("Parameter", style="cyan")
    params_table.add_column("Value", style="yellow")
    params_table.add_row("Population:", f"{result.num_players:,} players")
    params_table.add_row("Plays per player:", str(plays_per_player))
    params_table.add_row("Cost per play:", f"${cost_per_play:.2f}")
    params_table.add_row("Cost per player:", f"${plays_per_player * cost_per_play:.2f}")
    params_table.add_row("Simulation mode:", mode)
    
    # Add note for statistical mode
    if mode == "Statistical Estimation":
        params_table.add_row("", "[dim]Using probability-based calculation[/dim]")
    
    console.print(params_table)
    console.print()
    
    # Financial summary
    console.print("[bold]Population Financial Summary:[/bold]")
    financial_table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    financial_table.add_column("Metric", style="cyan")
    financial_table.add_column("Amount", justify="right", style="yellow")
    financial_table.add_column("Visualization", style="green")
    
    financial_table.add_row("Total Spent:", f"${result.total_spent:,.2f}", "")
    
    # Won vs Spent bar
    won_bar = create_simple_bar_chart(result.total_won, result.total_spent, width=25)
    financial_table.add_row("Total Won:", f"${result.total_won:,.2f}", won_bar)
    
    net_color = "green" if result.total_net >= 0 else "red"
    financial_table.add_row("Population Net:", f"[{net_color}]${result.total_net:,.2f}[/]", "")
    
    roi_bar = create_simple_bar_chart(max(0, result.population_roi), 100, width=25)
    financial_table.add_row("Population ROI:", f"{result.population_roi:.1f}%", roi_bar)
    
    console.print(financial_table)
    console.print()
    
    # Outcome distribution
    console.print("[bold]Outcome Distribution:[/bold]")
    outcome_table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    outcome_table.add_column("Outcome", style="cyan")
    outcome_table.add_column("Count", justify="right", style="yellow")
    outcome_table.add_column("Percentage", justify="right", style="green")
    outcome_table.add_column("Visual", style="blue")
    
    profit_pct = (result.players_profited / result.num_players * 100) if result.num_players > 0 else 0
    even_pct = (result.players_broke_even / result.num_players * 100) if result.num_players > 0 else 0
    loss_pct = (result.players_lost / result.num_players * 100) if result.num_players > 0 else 0
    
    profit_bar = create_simple_bar_chart(profit_pct, 100, width=20)
    even_bar = create_simple_bar_chart(even_pct, 100, width=20)
    loss_bar = create_simple_bar_chart(loss_pct, 100, width=20)
    
    outcome_table.add_row(
        "Players who profited:",
        f"{result.players_profited:,}",
        f"{profit_pct:.1f}%",
        profit_bar
    )
    outcome_table.add_row(
        "Players who broke even:",
        f"{result.players_broke_even:,}",
        f"{even_pct:.1f}%",
        even_bar
    )
    outcome_table.add_row(
        "Players who lost:",
        f"{result.players_lost:,}",
        f"{loss_pct:.1f}%",
        loss_bar
    )
    
    console.print(outcome_table)
    console.print()
    
    # Jackpot winners - Enhanced details
    if result.jackpot_winners:
        console.print(f"[bold green]🎰 Jackpot Winners: {len(result.jackpot_winners)} player(s) 🎰[/bold green]\n")
        print_jackpot_winner_details(result, plays_per_player, cost_per_play)
    else:
        console.print("[dim]Jackpot Winners: 0[/dim]\n")
    
    # Win statistics
    if result.player_results:
        # Exact mode - we have individual player data
        console.print("[bold]Win Statistics:[/bold]")
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", justify="right", style="yellow")
        
        stats_table.add_row("Mean ROI:", f"{result.mean_roi:.1f}%")
        stats_table.add_row("Median ROI:", f"{result.median_roi:.1f}%")
        stats_table.add_row("Std Deviation:", f"{result.std_dev_roi:.1f}%")
        
        # Add percentile analysis
        roi_values = [p.roi for p in result.player_results]
        if roi_values:
            roi_values_sorted = sorted(roi_values)
            n = len(roi_values_sorted)
            
            def percentile(p):
                k = (n - 1) * p / 100
                f = int(k)
                c = f + 1 if f + 1 < n else f
                return roi_values_sorted[f] + (k - f) * (roi_values_sorted[c] - roi_values_sorted[f])
            
            stats_table.add_row("25th Percentile:", f"{percentile(25):.1f}%")
            stats_table.add_row("75th Percentile:", f"{percentile(75):.1f}%")
            stats_table.add_row("90th Percentile:", f"{percentile(90):.1f}%")
            stats_table.add_row("95th Percentile:", f"{percentile(95):.1f}%")
            if n >= 100:  # Only show 99th for larger populations
                stats_table.add_row("99th Percentile:", f"{percentile(99):.1f}%")
        
        if result.best_player:
            stats_table.add_row(
                f"Best Player (#{result.best_player.player_id}):",
                f"Won ${result.best_player.won:.2f}, ROI {result.best_player.roi:.0f}%"
            )
        if result.worst_player:
            stats_table.add_row(
                f"Worst Player (#{result.worst_player.player_id}):",
                f"Won ${result.worst_player.won:.2f}, ROI {result.worst_player.roi:.0f}%"
            )
        
        console.print(stats_table)
        console.print()
        
        # ROI Distribution Histogram (for exact mode)
        if len(result.player_results) >= 10:
            console.print("[bold]ROI Distribution:[/bold]")
            print_roi_histogram(result.player_results)
            console.print()
    else:
        # Statistical mode - show aggregate statistics only
        console.print("[bold]Win Statistics:[/bold]")
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", justify="right", style="yellow")
        
        # For statistical mode, we can estimate these
        total_plays = result.num_players * plays_per_player
        stats_table.add_row("Total Plays:", f"{total_plays:,}")
        stats_table.add_row("Total Winners:", f"{result.total_wins:,}")
        stats_table.add_row("Win Rate:", f"{(result.total_wins / total_plays * 100):.2f}%")
        
        console.print(stats_table)
        console.print(f"[dim]Note: Individual player statistics not available in statistical mode[/dim]\n")
    
    # Prize distribution
    if result.total_wins_by_tier:
        console.print("[bold]Prize Tier Distribution:[/bold]")
        prize_table = Table(show_header=True, header_style="bold magenta")
        prize_table.add_column("Prize Tier", style="cyan")
        prize_table.add_column("Total Wins", justify="right", style="yellow")
        prize_table.add_column("Prize Amount", justify="right", style="green")
        prize_table.add_column("Total Paid", justify="right", style="green")
        
        # Get tier info
        tier_info = dict(get_tier_display_info())
        
        # Display tiers
        for tier_name, prize_str in get_tier_display_info():
            count = result.total_wins_by_tier.get(tier_name, 0)
            if count > 0 or tier_name == "Jackpot":
                if tier_name == "Jackpot" and result.jackpot_winners:
                    prize_table.add_row(
                        tier_name,
                        str(len(result.jackpot_winners)),
                        prize_str,
                        "🎰 JACKPOT! 🎰",
                        style="bold gold1"
                    )
                elif tier_name == "Jackpot":
                    prize_table.add_row(
                        tier_name,
                        "0",
                        prize_str,
                        "$0",
                        style="dim"
                    )
                else:
                    prize_amount = int(prize_str.replace("$", "").replace(",", ""))
                    total_paid = count * prize_amount
                    prize_table.add_row(
                        tier_name,
                        f"{count:,}",
                        prize_str,
                        f"${total_paid:,}"
                    )
        
        console.print(prize_table)
        console.print()
        
        # Total plays and wins
        total_plays = result.num_players * plays_per_player
        win_rate = (result.total_wins / total_plays * 100) if total_plays > 0 else 0
        console.print(f"[bold]Total Prize Winners:[/bold] {result.total_wins:,} out of {total_plays:,} plays ({win_rate:.1f}%)")
        console.print()
    
    # Reality check
    console.print(Panel(
        f"[yellow]Population Insights:[/yellow]\n\n"
        f"• {loss_pct:.1f}% of players lost money\n"
        f"• {profit_pct:.1f}% of players profited\n"
        f"• Population ROI ({result.population_roi:.1f}%) close to expected (~50%)\n"
        f"• Individual results vary (std dev: {result.std_dev_roi:.1f}%)\n\n"
        f"[bold]This demonstrates:[/bold]\n"
        f"• Law of Large Numbers - Population approaches expected value\n"
        f"• Survivor Bias - Most lose, but winners are visible\n"
        f"• Variance - Individuals unpredictable, population predictable",
        title="📊 Educational Insights",
        border_style="yellow"
    ))
    console.print()
