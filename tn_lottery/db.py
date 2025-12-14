import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

def get_db_path():
    """Get the database file path.
    
    Uses TN_LOTTERY_DB environment variable if set, otherwise defaults to
    ~/.local/share/tn-lottery/lottery.db or ./lottery.db as fallback.
    """
    # Check environment variable first
    if env_path := os.getenv('TN_LOTTERY_DB'):
        return env_path
    
    # Try to use XDG data directory
    try:
        data_dir = Path.home() / '.local' / 'share' / 'tn-lottery'
        data_dir.mkdir(parents=True, exist_ok=True)
        return str(data_dir / 'lottery.db')
    except (OSError, PermissionError):
        # Fallback to current directory if we can't create data dir
        return 'lottery.db'

DB_PATH = get_db_path()

@contextmanager
def get_db():
    """Get a database connection with context manager support."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tn_winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT,
                prize_amount REAL,
                raw_amount_str TEXT,
                date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS powerball_winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                winner_name TEXT,
                state TEXT,
                prize_amount REAL,
                is_jackpot BOOLEAN,
                draw_date TEXT,
                raw_amount_str TEXT,
                date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
