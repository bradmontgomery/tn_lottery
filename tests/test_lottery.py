"""Test suite for lottery.py - Random number generation for all games."""

import random
import pytest
from tn_lottery.lottery import Lottery


class TestLotteryGames:
    """Test that Lottery knows about all supported games."""
    
    def test_games_list(self):
        """Should return list of all supported games."""
        games = Lottery.games()
        assert isinstance(games, list)
        assert len(games) == 6
        assert 'powerball' in games
        assert 'megamillions' in games
        assert 'hotlotto' in games
        assert 'tncash' in games
        assert 'cash4' in games
        assert 'cash3' in games
    
    def test_title_lookup(self):
        """Should return proper title for each game."""
        assert Lottery.title('powerball') == 'Powerball'
        assert Lottery.title('megamillions') == 'Mega Millions'
        assert Lottery.title('hotlotto') == 'Hot Lotto Sizzler'
        assert Lottery.title('tncash') == 'Tennessee Cash'
        assert Lottery.title('cash4') == 'Cash 4'
        assert Lottery.title('cash3') == 'Cash 3'
    
    def test_title_unknown_game(self):
        """Should return None for unknown game."""
        assert Lottery.title('unknown') is None


class TestPowerball:
    """Test Powerball number generation."""
    
    def test_powerball_returns_tuple(self, lottery):
        """Should return tuple of (list, int)."""
        result = lottery.powerball()
        assert isinstance(result, tuple)
        assert len(result) == 2
        values, powerball = result
        assert isinstance(values, list)
        assert isinstance(powerball, int)
    
    def test_powerball_white_balls_count(self, lottery):
        """Should return exactly 5 white balls."""
        values, _ = lottery.powerball()
        assert len(values) == 5
    
    def test_powerball_white_balls_range(self, lottery):
        """White balls should be in range 1-69."""
        for _ in range(100):
            values, _ = lottery.powerball()
            for num in values:
                assert 1 <= num <= 69
    
    def test_powerball_range(self, lottery):
        """Powerball should be in range 1-26."""
        for _ in range(100):
            _, powerball = lottery.powerball()
            assert 1 <= powerball <= 26
    
    def test_powerball_white_balls_sorted(self, lottery):
        """White balls should be sorted."""
        for _ in range(100):
            values, _ = lottery.powerball()
            assert values == sorted(values)
    
    def test_powerball_white_balls_unique(self, lottery):
        """White balls should be unique (no duplicates)."""
        for _ in range(100):
            values, _ = lottery.powerball()
            assert len(values) == len(set(values))
    
    def test_powerball_randomness(self, lottery):
        """Should generate different results (not always the same)."""
        results = [lottery.powerball() for _ in range(10)]
        # Very unlikely to get 10 identical results
        unique_results = set(tuple(v) + (pb,) for v, pb in results)
        assert len(unique_results) > 1
    
    def test_print_powerball_format(self, lottery):
        """print_powerball should return formatted string."""
        result = lottery.print_powerball()
        assert isinstance(result, str)
        assert 'Powerball' in result
        assert '-' in result


class TestMegaMillions:
    """Test Mega Millions number generation."""
    
    def test_mega_millions_returns_tuple(self, lottery):
        """Should return tuple of (list, int)."""
        result = lottery.mega_millions()
        assert isinstance(result, tuple)
        assert len(result) == 2
        values, megaball = result
        assert isinstance(values, list)
        assert isinstance(megaball, int)
    
    def test_mega_millions_white_balls_count(self, lottery):
        """Should return exactly 5 white balls."""
        values, _ = lottery.mega_millions()
        assert len(values) == 5
    
    def test_mega_millions_white_balls_range(self, lottery):
        """White balls should be in range 1-70."""
        for _ in range(100):
            values, _ = lottery.mega_millions()
            for num in values:
                assert 1 <= num <= 70
    
    def test_mega_millions_megaball_range(self, lottery):
        """Mega Ball should be in range 1-25."""
        for _ in range(100):
            _, megaball = lottery.mega_millions()
            assert 1 <= megaball <= 25
    
    def test_mega_millions_white_balls_sorted(self, lottery):
        """White balls should be sorted."""
        for _ in range(100):
            values, _ = lottery.mega_millions()
            assert values == sorted(values)
    
    def test_mega_millions_white_balls_unique(self, lottery):
        """White balls should be unique."""
        for _ in range(100):
            values, _ = lottery.mega_millions()
            assert len(values) == len(set(values))
    
    def test_print_mega_millions_format(self, lottery):
        """print_mega_millions should return formatted string."""
        result = lottery.print_mega_millions()
        assert isinstance(result, str)
        assert 'Mega Millions' in result
        assert '-' in result


class TestHotLotto:
    """Test Hot Lotto Sizzler number generation."""
    
    def test_hot_lotto_returns_tuple(self, lottery):
        """Should return tuple of (list, int)."""
        result = lottery.hot_lotto_sizzler()
        assert isinstance(result, tuple)
        assert len(result) == 2
        values, hotball = result
        assert isinstance(values, list)
        assert isinstance(hotball, int)
    
    def test_hot_lotto_white_balls_count(self, lottery):
        """Should return exactly 5 white balls."""
        values, _ = lottery.hot_lotto_sizzler()
        assert len(values) == 5
    
    def test_hot_lotto_white_balls_range(self, lottery):
        """White balls should be in range 1-47."""
        for _ in range(100):
            values, _ = lottery.hot_lotto_sizzler()
            for num in values:
                assert 1 <= num <= 47
    
    def test_hot_lotto_hotball_range(self, lottery):
        """Hot Ball should be in range 1-19."""
        for _ in range(100):
            _, hotball = lottery.hot_lotto_sizzler()
            assert 1 <= hotball <= 19
    
    def test_hot_lotto_white_balls_sorted(self, lottery):
        """White balls should be sorted."""
        for _ in range(100):
            values, _ = lottery.hot_lotto_sizzler()
            assert values == sorted(values)
    
    def test_hot_lotto_white_balls_unique(self, lottery):
        """White balls should be unique."""
        for _ in range(100):
            values, _ = lottery.hot_lotto_sizzler()
            assert len(values) == len(set(values))
    
    def test_print_hot_lotto_format(self, lottery):
        """print_hot_lotto_sizzler should return formatted string."""
        result = lottery.print_hot_lotto_sizzler()
        assert isinstance(result, str)
        assert 'Hot Lotto Sizzler' in result
        assert '-' in result


class TestTNCash:
    """Test Tennessee Cash number generation."""
    
    def test_tn_cash_returns_tuple(self, lottery):
        """Should return tuple of (list, int)."""
        result = lottery.tn_cash()
        assert isinstance(result, tuple)
        assert len(result) == 2
        values, cashball = result
        assert isinstance(values, list)
        assert isinstance(cashball, int)
    
    def test_tn_cash_white_balls_count(self, lottery):
        """Should return exactly 5 white balls."""
        values, _ = lottery.tn_cash()
        assert len(values) == 5
    
    def test_tn_cash_white_balls_range(self, lottery):
        """White balls should be in range 1-35."""
        for _ in range(100):
            values, _ = lottery.tn_cash()
            for num in values:
                assert 1 <= num <= 35
    
    def test_tn_cash_cashball_range(self, lottery):
        """Cash Ball should be in range 1-5."""
        for _ in range(100):
            _, cashball = lottery.tn_cash()
            assert 1 <= cashball <= 5
    
    def test_tn_cash_white_balls_sorted(self, lottery):
        """White balls should be sorted."""
        for _ in range(100):
            values, _ = lottery.tn_cash()
            assert values == sorted(values)
    
    def test_tn_cash_white_balls_unique(self, lottery):
        """White balls should be unique."""
        for _ in range(100):
            values, _ = lottery.tn_cash()
            assert len(values) == len(set(values))
    
    def test_print_tn_cash_format(self, lottery):
        """print_tn_cash should return formatted string."""
        result = lottery.print_tn_cash()
        assert isinstance(result, str)
        assert 'Tennessee Cash' in result
        assert '-' in result


class TestCashFour:
    """Test Cash 4 number generation."""
    
    def test_cash_four_returns_int(self, lottery):
        """Should return an integer."""
        result = lottery.cash_four()
        assert isinstance(result, int)
    
    def test_cash_four_range(self, lottery):
        """Should be in range 0-9999."""
        for _ in range(100):
            result = lottery.cash_four()
            assert 0 <= result <= 9999
    
    def test_cash_four_can_be_zero(self, lottery):
        """Should be able to generate 0 (0000)."""
        # Run many times to increase odds of getting 0
        random.seed(0)  # Make deterministic
        lottery_inst = Lottery()
        results = [lottery_inst.cash_four() for _ in range(1000)]
        # At least one should be in 0-9 range (single digit)
        assert any(r < 10 for r in results)
    
    def test_print_cash_four_format(self, lottery):
        """print_cash_four should return 4-digit formatted string."""
        result = lottery.print_cash_four()
        assert isinstance(result, str)
        assert 'Cash 4' in result
        # Should have 4-digit number with leading zeros if needed
        assert any(char.isdigit() for char in result)


class TestCashThree:
    """Test Cash 3 number generation."""
    
    def test_cash_three_returns_int(self, lottery):
        """Should return an integer."""
        result = lottery.cash_three()
        assert isinstance(result, int)
    
    def test_cash_three_range(self, lottery):
        """Should be in range 0-999."""
        for _ in range(100):
            result = lottery.cash_three()
            assert 0 <= result <= 999
    
    def test_cash_three_can_be_zero(self, lottery):
        """Should be able to generate 0 (000)."""
        random.seed(0)
        lottery_inst = Lottery()
        results = [lottery_inst.cash_three() for _ in range(1000)]
        # At least one should be in 0-9 range
        assert any(r < 10 for r in results)
    
    def test_print_cash_three_format(self, lottery):
        """print_cash_three should return 3-digit formatted string."""
        result = lottery.print_cash_three()
        assert isinstance(result, str)
        assert 'Cash 3' in result
        # Should have 3-digit number
        assert any(char.isdigit() for char in result)


class TestLotteryInternals:
    """Test internal helper methods."""
    
    def test_padding(self, lottery):
        """_padding should return max game title length."""
        padding = lottery._padding()
        assert padding == len('Hot Lotto Sizzler')  # Longest title
        assert padding == 17
    
    def test_choose(self, lottery):
        """_choose should generate sorted random numbers."""
        result = lottery._choose(num=5, val_range=(1, 50))
        assert len(result) == 5
        assert all(1 <= n <= 50 for n in result)
        assert result == sorted(result)
    
    def test_to_str_list(self, lottery):
        """_to_str_list should format numbers with leading zeros."""
        result = lottery._to_str_list([1, 5, 10, 25, 69])
        assert result == ['01', '05', '10', '25', '69']
    
    def test_to_str_list_preserves_order(self, lottery):
        """_to_str_list should preserve input order."""
        result = lottery._to_str_list([69, 25, 10, 5, 1])
        assert result == ['69', '25', '10', '05', '01']


class TestDeterministicBehavior:
    """Test that randomness can be seeded for reproducibility."""
    
    def test_seeded_powerball_reproducible(self):
        """Same seed should produce same results."""
        random.seed(42)
        lottery1 = Lottery()
        result1 = lottery1.powerball()
        
        random.seed(42)
        lottery2 = Lottery()
        result2 = lottery2.powerball()
        
        assert result1 == result2
    
    def test_different_seeds_different_results(self):
        """Different seeds should produce different results."""
        random.seed(42)
        lottery1 = Lottery()
        result1 = lottery1.powerball()
        
        random.seed(123)
        lottery2 = Lottery()
        result2 = lottery2.powerball()
        
        # Very unlikely to be the same
        assert result1 != result2
