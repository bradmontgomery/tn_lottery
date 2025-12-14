import sqlite3
from contextlib import contextmanager

DB_NAME = "lottery.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
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
