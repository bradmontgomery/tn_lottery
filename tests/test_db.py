"""
Integration tests for database operations.

Tests database initialization, data insertion, and queries.
"""
import pytest
import sqlite3
import os
from pathlib import Path
from tn_lottery.db import init_db, get_db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_lottery.db"
    monkeypatch.setenv('TN_LOTTERY_DB', str(db_path))
    
    # Force reload of DB_PATH
    import tn_lottery.db
    monkeypatch.setattr(tn_lottery.db, 'DB_PATH', str(db_path))
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


class TestDatabaseInitialization:
    """Test database initialization."""
    
    def test_init_db_creates_database_file(self, temp_db):
        """Database file should be created."""
        init_db()
        assert temp_db.exists()
        
    def test_init_db_creates_tn_winners_table(self, temp_db):
        """Should create tn_winners table."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tn_winners'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'tn_winners'
        
    def test_init_db_creates_powerball_winners_table(self, temp_db):
        """Should create powerball_winners table."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='powerball_winners'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'powerball_winners'
        
    def test_init_db_tn_winners_has_correct_columns(self, temp_db):
        """TN winners table should have expected columns."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tn_winners)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        
        expected_columns = {'id', 'game_name', 'prize_amount', 'raw_amount_str', 'date_scraped'}
        assert expected_columns.issubset(columns)
        
    def test_init_db_powerball_winners_has_correct_columns(self, temp_db):
        """Powerball winners table should have expected columns."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(powerball_winners)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        
        expected_columns = {
            'id', 'winner_name', 'state', 'prize_amount', 
            'is_jackpot', 'draw_date', 'raw_amount_str', 'date_scraped'
        }
        assert expected_columns.issubset(columns)
        
    def test_init_db_is_idempotent(self, temp_db):
        """Running init_db multiple times should not error."""
        init_db()
        init_db()  # Should not raise
        init_db()  # Should not raise
        
        # Tables should still exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        assert 'tn_winners' in tables
        assert 'powerball_winners' in tables


class TestDatabaseContextManager:
    """Test get_db context manager."""
    
    def test_get_db_returns_connection(self, temp_db):
        """get_db should return a connection."""
        init_db()
        
        import tn_lottery.db
        with tn_lottery.db.get_db() as conn:
            assert isinstance(conn, sqlite3.Connection)
            
    def test_get_db_closes_connection(self, temp_db):
        """Connection should be closed after context exits."""
        init_db()
        
        import tn_lottery.db
        with tn_lottery.db.get_db() as conn:
            pass
        
        # Connection should be closed
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")
            
    def test_get_db_has_row_factory(self, temp_db):
        """Connection should have row_factory set."""
        init_db()
        
        import tn_lottery.db
        with tn_lottery.db.get_db() as conn:
            assert conn.row_factory == sqlite3.Row


class TestTNWinnersTable:
    """Test TN winners table operations."""
    
    def test_insert_tn_winner(self, temp_db):
        """Should insert TN winner data."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tn_winners (game_name, prize_amount, raw_amount_str)
            VALUES (?, ?, ?)
        """, ('Powerball', 1000000.0, '$1,000,000'))
        conn.commit()
        conn.close()
        
        # Verify insertion
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tn_winners")
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[1] == 'Powerball'  # game_name
        assert row[2] == 1000000.0    # prize_amount
        assert row[3] == '$1,000,000'  # raw_amount_str
        
    def test_insert_multiple_tn_winners(self, temp_db):
        """Should insert multiple winners."""
        init_db()
        
        winners = [
            ('Powerball', 1000000.0, '$1,000,000'),
            ('Mega Millions', 500000.0, '$500,000'),
            ('Cash 4 Life', 1000.0, '$1,000'),
        ]
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO tn_winners (game_name, prize_amount, raw_amount_str)
            VALUES (?, ?, ?)
        """, winners)
        conn.commit()
        conn.close()
        
        # Verify count
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tn_winners")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 3
        
    def test_query_tn_winners_by_game(self, temp_db):
        """Should query winners by game name."""
        init_db()
        
        # Insert test data
        winners = [
            ('Powerball', 1000000.0, '$1,000,000'),
            ('Powerball', 50000.0, '$50,000'),
            ('Mega Millions', 500000.0, '$500,000'),
        ]
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO tn_winners (game_name, prize_amount, raw_amount_str)
            VALUES (?, ?, ?)
        """, winners)
        conn.commit()
        
        # Query Powerball winners
        cursor.execute("SELECT * FROM tn_winners WHERE game_name = ?", ('Powerball',))
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 2
        assert all(row[1] == 'Powerball' for row in rows)
        
    def test_sum_tn_prize_amounts(self, temp_db):
        """Should calculate total prize amounts."""
        init_db()
        
        # Insert test data
        winners = [
            ('Powerball', 1000000.0, '$1,000,000'),
            ('Powerball', 50000.0, '$50,000'),
            ('Powerball', 100.0, '$100'),
        ]
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO tn_winners (game_name, prize_amount, raw_amount_str)
            VALUES (?, ?, ?)
        """, winners)
        conn.commit()
        
        # Sum Powerball prizes
        cursor.execute("""
            SELECT SUM(prize_amount) FROM tn_winners WHERE game_name = ?
        """, ('Powerball',))
        total = cursor.fetchone()[0]
        conn.close()
        
        assert total == 1050100.0


class TestPowerballWinnersTable:
    """Test Powerball winners table operations."""
    
    def test_insert_powerball_winner(self, temp_db):
        """Should insert Powerball winner data."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO powerball_winners 
            (winner_name, state, prize_amount, is_jackpot, draw_date, raw_amount_str)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('John Doe', 'TN', 1000000.0, True, '2024-01-01', '$1 Million'))
        conn.commit()
        conn.close()
        
        # Verify insertion
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM powerball_winners")
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[1] == 'John Doe'     # winner_name
        assert row[2] == 'TN'           # state
        assert row[3] == 1000000.0      # prize_amount
        assert row[4] == 1              # is_jackpot (stored as 1)
        
    def test_query_jackpot_winners(self, temp_db):
        """Should query only jackpot winners."""
        init_db()
        
        # Insert test data
        winners = [
            ('Alice', 'TN', 10000000.0, True, '2024-01-01', '$10M'),
            ('Bob', 'CA', 50000.0, False, '2024-01-02', '$50K'),
            ('Charlie', 'TN', 5000000.0, True, '2024-01-03', '$5M'),
        ]
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO powerball_winners 
            (winner_name, state, prize_amount, is_jackpot, draw_date, raw_amount_str)
            VALUES (?, ?, ?, ?, ?, ?)
        """, winners)
        conn.commit()
        
        # Query jackpot winners
        cursor.execute("""
            SELECT * FROM powerball_winners WHERE is_jackpot = 1
        """)
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 2
        assert all(row[4] == 1 for row in rows)  # is_jackpot column
        
    def test_query_winners_by_state(self, temp_db):
        """Should query winners by state."""
        init_db()
        
        # Insert test data
        winners = [
            ('Alice', 'TN', 10000000.0, True, '2024-01-01', '$10M'),
            ('Bob', 'CA', 50000.0, False, '2024-01-02', '$50K'),
            ('Charlie', 'TN', 5000000.0, True, '2024-01-03', '$5M'),
        ]
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO powerball_winners 
            (winner_name, state, prize_amount, is_jackpot, draw_date, raw_amount_str)
            VALUES (?, ?, ?, ?, ?, ?)
        """, winners)
        conn.commit()
        
        # Query TN winners
        cursor.execute("""
            SELECT * FROM powerball_winners WHERE state = ?
        """, ('TN',))
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 2
        assert all(row[2] == 'TN' for row in rows)


class TestDatabaseEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_database_queries(self, temp_db):
        """Queries on empty database should return no results."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tn_winners")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 0
        
    def test_null_values_handled(self, temp_db):
        """NULL values should be handled properly."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tn_winners (game_name, prize_amount)
            VALUES (?, ?)
        """, ('Powerball', 1000.0))
        conn.commit()
        
        cursor.execute("SELECT raw_amount_str FROM tn_winners")
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] is None
        
    def test_large_prize_amount(self, temp_db):
        """Should handle large prize amounts."""
        init_db()
        
        large_amount = 1587500000.0  # $1.5875 billion (actual Powerball record)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tn_winners (game_name, prize_amount, raw_amount_str)
            VALUES (?, ?, ?)
        """, ('Powerball', large_amount, '$1,587,500,000'))
        conn.commit()
        
        cursor.execute("SELECT prize_amount FROM tn_winners")
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == large_amount
        
    def test_special_characters_in_names(self, temp_db):
        """Should handle special characters in names."""
        init_db()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO powerball_winners 
            (winner_name, state, prize_amount, is_jackpot, draw_date, raw_amount_str)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("O'Brien & Smith", 'TN', 1000.0, False, '2024-01-01', '$1K'))
        conn.commit()
        
        cursor.execute("SELECT winner_name FROM powerball_winners")
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == "O'Brien & Smith"
