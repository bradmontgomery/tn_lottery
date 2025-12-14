#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import rich_click as click
from rich.console import Console
from rich.table import Table
from tn_lottery.lottery import Lottery

console = Console()


def list_games():
    """Display a list of available lottery games."""
    console.print("\nYou may use the following with the -g or --game flag:")
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="green")
    for key, title in Lottery.game_data.items():
        table.add_row(key, title)
    console.print(table)


def generate_numbers(game=None, number=1):
    """Generate random lottery numbers.
    
    Args:
        game: Specific game to play (if None, plays all games)
        number: Number of times to generate numbers
    """
    # The full list of games.
    games = Lottery.games()
    if game and game not in games:
        console.print(f"[bold red]\n{game} is not a valid game.[/bold red]")
        sys.exit(1)
    elif game:
        games = [game]  # Just play a single game

    # Prints randomly generated numbers for the selected TN Lottery game
    console.print("\n" + "[bold blue]" + "+" * 50 + "[/bold blue]")
    game_name = game if game else "TN Lottery"
    console.print(f"[bold green]{game_name} Numbers![/bold green]")
    console.print("[bold blue]" + "-" * 50 + "[/bold blue]")
    for n in range(number):
        lottery = Lottery()
        if "powerball" in games:
            console.print(lottery.print_powerball())
        if "megamillions" in games:
            console.print(lottery.print_mega_millions())
        if "hotlotto" in games:
            console.print(lottery.print_hot_lotto_sizzler())
        if "tncash" in games:
            console.print(lottery.print_tn_cash())
        if "cash4" in games:
            console.print(lottery.print_cash_four())
        if "cash3" in games:
            console.print(lottery.print_cash_three())
        if number > 1 and len(games) > 1:
            console.print("-" * 50)
    console.print("\n[bold yellow]Good Luck! (you'll need it)[/bold yellow]\n\n")


@click.command()
@click.option('-l', '--list', 'list_games_flag', is_flag=True, help="list available games")
@click.option('-g', '--game', type=str, help="play a single game (see the list)")
@click.option('-n', '--number', type=int, default=1, help="number of plays")
def run(list_games_flag, game, number):
    """Generate numbers for some TN Lottery Games"""
    if list_games_flag:
        list_games()
        sys.exit()
    
    generate_numbers(game, number)


if __name__ == "__main__":
    run()
