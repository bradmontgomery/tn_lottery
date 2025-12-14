"""
Scrapes winner data starting at:
https://www.tnlottery.com/winners?page=0

Then counts the amounts & the games.

"""
import re
import time
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
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

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


def fetch_with_retry(url, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """Fetch URL with retry logic.
    
    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries
        
    Returns:
        requests.Response object or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                return resp
            elif resp.status_code == 429:  # Rate limited
                console.print(f"[yellow]Rate limited, waiting {delay * (attempt + 1)}s...[/yellow]")
                time.sleep(delay * (attempt + 1))
            else:
                console.print(f"[yellow]HTTP {resp.status_code}, attempt {attempt + 1}/{max_retries}[/yellow]")
                if attempt < max_retries - 1:
                    time.sleep(delay)
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]Request error: {e}, attempt {attempt + 1}/{max_retries}[/yellow]")
            if attempt < max_retries - 1:
                time.sleep(delay)
    
    return None


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
        return float(clean_str) if clean_str else 0.0
    except ValueError:
        return 0.0


def scrape_tn_lottery():
    """Scrape TN Lottery winners to database."""
    with get_db() as conn:
        # Clear existing data for a fresh scrape (optional, but good for this exercise)
        conn.execute("DELETE FROM tn_winners")
        conn.commit()
        
        total_winners = 0
        failed_pages = []
        
        with console.status("[bold green]Scraping TN Lottery data...") as status:
            for page in range(TN_MAX_PAGES):
                url = TN_URL.format(page=page)
                
                resp = fetch_with_retry(url)
                if not resp:
                    console.print(f"[red]Failed to fetch page {page} after retries[/red]")
                    failed_pages.append(page)
                    continue
                
                try:
                    soup = BeautifulSoup(resp.content, "lxml")
                    
                    # Find all prize amounts
                    amounts = [div.get_text(strip=True) for div in soup.select("div.prize-amount")]
                    games = [div.get_text(strip=True) for div in soup.select("div.game-name")]
                    
                    if not games:
                        console.print(f"[yellow]No data found on page {page}[/yellow]")
                        continue
                    
                    for game, amount_str in zip(games, amounts):
                        amount = parse_amount(amount_str)
                        conn.execute(
                            "INSERT INTO tn_winners (game_name, prize_amount, raw_amount_str) VALUES (?, ?, ?)",
                            (game, amount, amount_str)
                        )
                    
                    total_winners += len(games)
                    console.print(f"Scraped page {page}: {len(games)} winners")
                    
                    # Rate limiting - be nice to the server
                    time.sleep(0.5)
                    
                except Exception as e:
                    console.print(f"[red]Error parsing page {page}: {e}[/red]")
                    failed_pages.append(page)
        
        conn.commit()
    
    console.print(f"[bold green]TN Lottery scraping complete![/bold green]")
    console.print(f"Total winners scraped: {total_winners}")
    if failed_pages:
        console.print(f"[yellow]Failed pages: {failed_pages}[/yellow]")


def scrape_powerball_data():
    """Scrape Powerball winners to database."""
    with get_db() as conn:
        conn.execute("DELETE FROM powerball_winners")
        conn.commit()
        
        total_winners = 0
        failed_pages = []
        
        with console.status("[bold blue]Scraping Powerball data...") as status:
            for page in range(1, PB_MAX_PAGES + 1):
                url = PB_URL.format(page=page)
                
                resp = fetch_with_retry(url)
                if not resp:
                    console.print(f"[red]Failed to fetch page {page} after retries[/red]")
                    failed_pages.append(page)
                    continue
                
                try:
                    soup = BeautifulSoup(resp.content, "lxml")
                    cards = soup.select("a.card")
                    
                    if not cards:
                        console.print(f"[yellow]No data found on page {page}, stopping[/yellow]")
                        break
                    
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
                    
                    total_winners += count
                    console.print(f"Scraped page {page}: {count} winners")
                    
                    # Rate limiting - be nice to the server
                    time.sleep(0.5)
                    
                except Exception as e:
                    console.print(f"[red]Error parsing page {page}: {e}[/red]")
                    failed_pages.append(page)
        
        conn.commit()
    
    console.print(f"[bold blue]Powerball scraping complete![/bold blue]")
    console.print(f"Total winners scraped: {total_winners}")
    if failed_pages:
        console.print(f"[yellow]Failed pages: {failed_pages}[/yellow]")


def generate_report():
    """Generate statistics report from database."""
    init_db()  # Ensure tables exist
    with get_db() as conn:
        # Check if we have any data
        count = conn.execute("SELECT COUNT(*) as c FROM tn_winners").fetchone()["c"]
        if count == 0:
            console.print("[yellow]No TN Lottery data found. Run 'tn-lottery scrape tn' first.[/yellow]")
            return
        
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
            WHERE prize_amount > 0
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
    init_db()  # Ensure tables exist
    with get_db() as conn:
        # Check if we have any data
        count = conn.execute("SELECT COUNT(*) as c FROM powerball_winners").fetchone()["c"]
        if count == 0:
            console.print("[yellow]No Powerball data found. Run 'tn-lottery scrape powerball' first.[/yellow]")
            return
        
        rows = conn.execute("""
            SELECT winner_name, state, prize_amount, raw_amount_str, is_jackpot
            FROM powerball_winners 
            WHERE prize_amount >= 1000000
            ORDER BY prize_amount DESC
        """).fetchall()
        
        if not rows:
            console.print("[yellow]No Powerball winnings over $1 Million found.[/yellow]")
            return
        
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
