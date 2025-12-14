"""
Scrapes winner data starting at:
https://www.tnlottery.com/winners?page=0

Then counts the amounts & the games.

"""
import re
import requests
import statistics
import rich_click as click
from rich.console import Console
from rich.table import Table
from rich.progress import track
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
from tn_lottery.db import init_db, get_db

console = Console()

TN_URL = "https://www.tnlottery.com/winners?page={page}"
PB_URL = "https://www.powerball.com/winners-gallery?pg={page}"
TN_MAX_PAGES = 20
PB_MAX_PAGES = 25 # Based on pagination seen in HTML

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


def parse_amount(amount_str):
    """Parse amount string to float."""
    if not amount_str:
        return 0.0
    
    clean_str = amount_str.lower().strip().replace(",", "").replace("$", "")
    
    if "million" in clean_str:
        clean_str = clean_str.replace("million", "").strip()
        try:
            return float(clean_str) * 1_000_000
        except ValueError:
            pass
            
    try:
        # Remove any non-numeric chars except .
        clean_str = re.sub(r"[^\d\.]", "", clean_str)
        return float(clean_str)
    except ValueError:
        return 0.0


def scrape_tn_lottery():
    """Scrape TN Lottery winners to database."""
    with get_db() as conn:
        # Clear existing data for a fresh scrape (optional, but good for this exercise)
        conn.execute("DELETE FROM tn_winners")
        conn.commit()
        
        with console.status("[bold green]Scraping TN Lottery data...") as status:
            for page in range(TN_MAX_PAGES):
                url = TN_URL.format(page=page)
                try:
                    resp = requests.get(url, headers=HEADERS)
                    if resp.status_code != 200:
                        console.print(f"[red]Failed to fetch page {page}: Status {resp.status_code}[/red]")
                        break
                        
                    soup = BeautifulSoup(resp.content, "lxml")
                    
                    # Find all prize amounts
                    amounts = [div.get_text(strip=True) for div in soup.select("div.prize-amount")]
                    games = [div.get_text(strip=True) for div in soup.select("div.game-name")]
                    
                    if not games:
                        console.print(f"[yellow]No data found on page {page}[/yellow]")
                    
                    for game, amount_str in zip(games, amounts):
                        amount = parse_amount(amount_str)
                        conn.execute(
                            "INSERT INTO tn_winners (game_name, prize_amount, raw_amount_str) VALUES (?, ?, ?)",
                            (game, amount, amount_str)
                        )
                    
                    console.print(f"Scraped page {page}: {len(games)} winners")
                    
                except Exception as e:
                    console.print(f"[red]Error scraping page {page}: {e}[/red]")
        
        conn.commit()
    console.print("[bold green]TN Lottery scraping complete![/bold green]")


def scrape_powerball_data():
    """Scrape Powerball winners to database."""
    with get_db() as conn:
        conn.execute("DELETE FROM powerball_winners")
        conn.commit()
        
        with console.status("[bold blue]Scraping Powerball data...") as status:
            for page in range(1, PB_MAX_PAGES + 1):
                url = PB_URL.format(page=page)
                try:
                    resp = requests.get(url, headers=HEADERS)
                    if resp.status_code != 200:
                        break
                        
                    soup = BeautifulSoup(resp.content, "lxml")
                    cards = soup.select("a.card")
                    
                    count = 0
                    for card in cards:
                        detail = card.select_one(".detail-wrap")
                        if not detail:
                            continue
                            
                        amount_tag = detail.select_one("h3")
                        name_tag = detail.select_one("h4")
                        state_tag = detail.select_one("h5")
                        
                        amount_str = amount_tag.get_text(strip=True) if amount_tag else ""
                        name = name_tag.get_text(strip=True) if name_tag else "Unknown"
                        state = state_tag.get_text(strip=True) if state_tag else "Unknown"
                        
                        amount = parse_amount(amount_str)
                        is_jackpot = "jackpot" in amount_str.lower() or amount > 20_000_000 # Heuristic
                        
                        conn.execute(
                            """INSERT INTO powerball_winners 
                               (winner_name, state, prize_amount, is_jackpot, raw_amount_str) 
                               VALUES (?, ?, ?, ?, ?)""",
                            (name, state, amount, is_jackpot, amount_str)
                        )
                        count += 1
                        
                    console.print(f"Scraped page {page}: {count} winners")
                    
                except Exception as e:
                    console.print(f"[red]Error scraping page {page}: {e}[/red]")
        
        conn.commit()
    console.print("[bold blue]Powerball scraping complete![/bold blue]")


def generate_report():
    """Generate statistics report from database."""
    with get_db() as conn:
        # Most commonly won games
        rows = conn.execute("""
            SELECT game_name, COUNT(*) as count 
            FROM tn_winners 
            GROUP BY game_name 
            ORDER BY count DESC 
            LIMIT 5
        """).fetchall()
        
        console.print("\n[bold]The Most commonly won games are:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Game")
        table.add_column("Wins", justify="right")
        for row in rows:
            table.add_row(row["game_name"], str(row["count"]))
        console.print(table)

        # Most commonly won amounts
        rows = conn.execute("""
            SELECT raw_amount_str, COUNT(*) as count 
            FROM tn_winners 
            GROUP BY raw_amount_str 
            ORDER BY count DESC 
            LIMIT 5
        """).fetchall()
        
        console.print("\n[bold]The most commonly won amounts are:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Amount")
        table.add_column("Wins", justify="right")
        for row in rows:
            table.add_row(row["raw_amount_str"], str(row["count"]))
        console.print(table)
        
        # Best paying games
        rows = conn.execute("""
            SELECT game_name, AVG(prize_amount) as avg_amount 
            FROM tn_winners 
            GROUP BY game_name 
            ORDER BY avg_amount DESC
        """).fetchall()
        
        console.print("\n[bold]The best-paying games on average are:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Game")
        table.add_column("Average Amount", justify="right")
        for row in rows:
            table.add_row(row["game_name"], f"${int(row['avg_amount']):,}")
        console.print(table)


def show_timeline():
    """Timeline of Powerball winnings over $1 Million."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT winner_name, state, prize_amount, raw_amount_str, is_jackpot
            FROM powerball_winners 
            WHERE prize_amount >= 1000000
            ORDER BY prize_amount DESC
        """).fetchall()
        
        console.print("\n[bold]Powerball Winnings > $1 Million (by Amount)[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Winner")
        table.add_column("State")
        table.add_column("Amount", justify="right")
        table.add_column("Jackpot?", justify="center")
        
        for row in rows:
            is_jackpot = "Yes" if row["is_jackpot"] else "No"
            style = "bold gold1" if row["is_jackpot"] else "white"
            table.add_row(
                str(row["winner_name"]), 
                str(row["state"]), 
                str(row["raw_amount_str"]), 
                is_jackpot,
                style=style
            )
        console.print(table)
        
        # Frequency analysis
        console.print("\n[bold]Frequency of High Winnings[/bold]")
        # Group by amount ranges
        ranges = [
            (1_000_000, 2_000_000, "$1M - $2M"),
            (2_000_000, 10_000_000, "$2M - $10M"),
            (10_000_000, 100_000_000, "$10M - $100M"),
            (100_000_000, float('inf'), "> $100M")
        ]
        
        for min_val, max_val, label in ranges:
            count = conn.execute("""
                SELECT COUNT(*) as c FROM powerball_winners 
                WHERE prize_amount >= ? AND prize_amount < ?
            """, (min_val, max_val)).fetchone()["c"]
            console.print(f"{label}: {count} winners")


@click.group()
def cli():
    """Scrape and analyze lottery winner data."""
    init_db()


@cli.command()
def scrape_tn():
    """Scrape TN Lottery winners to database."""
    scrape_tn_lottery()


@cli.command()
def scrape_powerball():
    """Scrape Powerball winners to database."""
    scrape_powerball_data()


@cli.command()
def report():
    """Generate statistics report from database."""
    generate_report()


@cli.command()
def timeline():
    """Timeline of Powerball winnings over $1 Million."""
    show_timeline()


if __name__ == "__main__":
    cli()
