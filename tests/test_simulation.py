"""Test suite for simulation.py - Individual simulation logic."""

import random
import pytest
from tn_lottery.lottery import Lottery
from tn_lottery.simulation import (
    generate_ticket,
    play_drawing,
    create_simple_bar_chart,
)


class TestGenerateTicket:
    """Test ticket generation."""
    
    def test_generate_ticket_structure(self):
        """Should return tuple of (numbers_list, cost)."""
        lotto = Lottery()
        result = generate_ticket(lotto, plays=5, cost_per_play=2.0)
        assert isinstance(result, tuple)
        assert len(result) == 2
        numbers, cost = result
        assert isinstance(numbers, list)
        assert isinstance(cost, (int, float))
    
    def test_generate_ticket_count(self):
        """Should generate requested number of plays."""
        lotto = Lottery()
        numbers, _ = generate_ticket(lotto, plays=5, cost_per_play=2.0)
        assert len(numbers) == 5
        
        numbers, _ = generate_ticket(lotto, plays=10, cost_per_play=2.0)
        assert len(numbers) == 10
    
    def test_generate_ticket_cost_calculation(self):
        """Cost should be plays * cost_per_play."""
        lotto = Lottery()
        
        _, cost = generate_ticket(lotto, plays=5, cost_per_play=2.0)
        assert cost == 10.0
        
        _, cost = generate_ticket(lotto, plays=3, cost_per_play=2.5)
        assert cost == 7.5
        
        _, cost = generate_ticket(lotto, plays=1, cost_per_play=3.0)
        assert cost == 3.0
    
    def test_generate_ticket_format(self):
        """Each play should be valid powerball tuple."""
        lotto = Lottery()
        numbers, _ = generate_ticket(lotto, plays=5, cost_per_play=2.0)
        
        for play in numbers:
            assert isinstance(play, tuple)
            assert len(play) == 2
            white_balls, powerball = play
            assert isinstance(white_balls, list)
            assert len(white_balls) == 5
            assert isinstance(powerball, int)
            assert 1 <= powerball <= 26


class TestPlayDrawing:
    """Test single drawing execution."""
    
    def test_play_drawing_structure(self):
        """Should return tuple of (winnings, wins_by_tier, won_jackpot, cost)."""
        lotto = Lottery()
        result = play_drawing(lotto, plays_per_ticket=5, cost_per_play=2.0)
        
        assert isinstance(result, tuple)
        assert len(result) == 4
        
        winnings, wins_by_tier, won_jackpot, cost = result
        assert isinstance(winnings, (int, float))
        assert isinstance(wins_by_tier, dict)
        assert isinstance(won_jackpot, bool)
        assert isinstance(cost, (int, float))
    
    def test_play_drawing_cost(self):
        """Cost should match plays_per_ticket * cost_per_play."""
        lotto = Lottery()
        _, _, _, cost = play_drawing(lotto, plays_per_ticket=5, cost_per_play=2.0)
        assert cost == 10.0
    
    def test_play_drawing_winnings_non_negative(self):
        """Winnings should never be negative."""
        lotto = Lottery()
        for _ in range(100):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=5, cost_per_play=2.0)
            assert winnings >= 0
    
    def test_play_drawing_wins_by_tier_is_dict(self):
        """wins_by_tier should be dictionary."""
        lotto = Lottery()
        _, wins_by_tier, _, _ = play_drawing(lotto, plays_per_ticket=5, cost_per_play=2.0)
        assert isinstance(wins_by_tier, dict)
        
        # All keys should be strings (tier names)
        for key in wins_by_tier.keys():
            assert isinstance(key, str)
        
        # All values should be positive integers
        for value in wins_by_tier.values():
            assert isinstance(value, int)
            assert value > 0
    
    def test_play_drawing_jackpot_is_bool(self):
        """won_jackpot should be boolean."""
        lotto = Lottery()
        for _ in range(10):
            _, _, won_jackpot, _ = play_drawing(lotto, plays_per_ticket=5, cost_per_play=2.0)
            assert isinstance(won_jackpot, bool)


class TestSimulationStatistics:
    """Test statistical properties of simulation over many plays."""
    
    def test_win_rate_approximately_correct(self):
        """Over many plays, should win something about 4% of the time."""
        lotto = Lottery()
        random.seed(42)  # Make reproducible
        
        num_plays = 1000
        wins = 0
        
        for _ in range(num_plays):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if winnings > 0:
                wins += 1
        
        win_rate = wins / num_plays
        # Should be roughly 4% (1 in 24.87), allow margin 2-6%
        assert 0.02 < win_rate < 0.06, f"Win rate {win_rate:.2%} outside expected range"
    
    def test_most_common_wins_are_small(self):
        """Most wins should be $4 or $7 prizes (lowest tiers)."""
        lotto = Lottery()
        random.seed(42)
        
        all_winnings = []
        for _ in range(500):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if winnings > 0:
                all_winnings.append(winnings)
        
        # Most common wins should be small amounts
        if all_winnings:  # Only check if we had any wins
            small_wins = [w for w in all_winnings if w <= 10]
            # Majority should be small prizes
            assert len(small_wins) / len(all_winnings) > 0.7
    
    def test_jackpot_is_extremely_rare(self):
        """Jackpot should be extremely rare (not hit in reasonable sample)."""
        lotto = Lottery()
        random.seed(42)
        
        jackpots = 0
        for _ in range(1000):
            _, _, won_jackpot, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if won_jackpot:
                jackpots += 1
        
        # With 1 in 292M odds, we shouldn't hit jackpot in 1000 plays
        assert jackpots == 0


class TestCreateSimpleBarChart:
    """Test bar chart generation."""
    
    def test_bar_chart_empty(self):
        """Zero value should create empty bar."""
        bar = create_simple_bar_chart(0, 100, width=10)
        assert len(bar) == 10
        assert bar == "░" * 10
    
    def test_bar_chart_full(self):
        """Max value should create full bar."""
        bar = create_simple_bar_chart(100, 100, width=10)
        assert len(bar) == 10
        assert bar == "█" * 10
    
    def test_bar_chart_half(self):
        """Half value should create half bar."""
        bar = create_simple_bar_chart(50, 100, width=10)
        assert len(bar) == 10
        assert bar == "█" * 5 + "░" * 5
    
    def test_bar_chart_custom_width(self):
        """Should respect custom width."""
        bar = create_simple_bar_chart(50, 100, width=20)
        assert len(bar) == 20
        
        bar = create_simple_bar_chart(50, 100, width=5)
        assert len(bar) == 5
    
    def test_bar_chart_handles_zero_max(self):
        """Should handle zero max value without error."""
        bar = create_simple_bar_chart(0, 0, width=10)
        assert len(bar) == 10
        assert bar == "░" * 10


class TestSimulationHelpers:
    """Test simulation helper functions and edge cases."""
    
    def test_generate_ticket_single_play(self):
        """Should work with single play."""
        lotto = Lottery()
        numbers, cost = generate_ticket(lotto, plays=1, cost_per_play=2.0)
        assert len(numbers) == 1
        assert cost == 2.0
    
    def test_generate_ticket_many_plays(self):
        """Should work with many plays."""
        lotto = Lottery()
        numbers, cost = generate_ticket(lotto, plays=100, cost_per_play=2.0)
        assert len(numbers) == 100
        assert cost == 200.0
    
    def test_play_drawing_different_costs(self):
        """Should work with different cost_per_play values."""
        lotto = Lottery()
        
        _, _, _, cost = play_drawing(lotto, plays_per_ticket=5, cost_per_play=1.0)
        assert cost == 5.0
        
        _, _, _, cost = play_drawing(lotto, plays_per_ticket=5, cost_per_play=3.0)
        assert cost == 15.0
        
        _, _, _, cost = play_drawing(lotto, plays_per_ticket=2, cost_per_play=2.5)
        assert cost == 5.0


class TestSimulationDeterminism:
    """Test that simulation can be made deterministic for testing."""
    
    def test_seeded_drawing_reproducible(self):
        """Same seed should produce same drawing result."""
        random.seed(123)
        lotto1 = Lottery()
        result1 = play_drawing(lotto1, plays_per_ticket=5, cost_per_play=2.0)
        
        random.seed(123)
        lotto2 = Lottery()
        result2 = play_drawing(lotto2, plays_per_ticket=5, cost_per_play=2.0)
        
        # Results should be identical
        assert result1[0] == result2[0]  # winnings
        assert result1[1] == result2[1]  # wins_by_tier
        assert result1[2] == result2[2]  # won_jackpot
        assert result1[3] == result2[3]  # cost
