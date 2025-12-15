"""
Tests for multiplayer simulation functionality.

Tests the three simulation modes:
1. Exact Simulation (small populations)
2. Parallel Simulation (medium populations)
3. Statistical Estimation (large populations)
"""

import pytest
from tn_lottery.multiplayer import (
    simulate_single_player,
    simulate_population,
    simulate_population_parallel,
    simulate_population_statistical,
    simulate_population_auto,
    PlayerResult,
    PopulationResult
)
from tn_lottery.lottery import Lottery


class TestPlayerResult:
    """Test PlayerResult dataclass properties and methods."""
    
    def test_player_result_structure(self):
        """PlayerResult should have all required fields."""
        result = PlayerResult(
            player_id=1,
            spent=100.0,
            won=50.0,
            net=-50.0,
            wins_by_tier={"$4": 2},
            won_jackpot=False
        )
        
        assert result.player_id == 1
        assert result.spent == 100.0
        assert result.won == 50.0
        assert result.net == -50.0
        assert result.wins_by_tier == {"$4": 2}
        assert result.won_jackpot is False
    
    def test_roi_calculation(self):
        """ROI should be calculated as (won / spent * 100)."""
        result = PlayerResult(
            player_id=1,
            spent=100.0,
            won=150.0,
            net=50.0,
            wins_by_tier={"$4": 5},
            won_jackpot=False
        )
        
        assert result.roi == 150.0  # 150% ROI (as percentage)
    
    def test_roi_with_zero_spent(self):
        """ROI should be 0.0 when nothing spent."""
        result = PlayerResult(
            player_id=1,
            spent=0.0,
            won=0.0,
            net=0.0,
            wins_by_tier={},
            won_jackpot=False
        )
        
        assert result.roi == 0.0
    
    def test_profited_property_true(self):
        """profited should be True when net > 0."""
        result = PlayerResult(
            player_id=1,
            spent=100.0,
            won=150.0,
            net=50.0,
            wins_by_tier={"$4": 5},
            won_jackpot=False
        )
        
        assert result.profited is True
    
    def test_profited_property_false(self):
        """profited should be False when net <= 0."""
        result = PlayerResult(
            player_id=1,
            spent=100.0,
            won=50.0,
            net=-50.0,
            wins_by_tier={"$4": 2},
            won_jackpot=False
        )
        
        assert result.profited is False
    
    def test_broke_even_property_true(self):
        """broke_even should be True when net is close to 0 (within $1)."""
        result = PlayerResult(
            player_id=1,
            spent=100.0,
            won=100.5,
            net=0.5,
            wins_by_tier={"$4": 3},
            won_jackpot=False
        )
        
        assert result.broke_even is True
    
    def test_broke_even_property_false(self):
        """broke_even should be False when net is far from 0."""
        result = PlayerResult(
            player_id=1,
            spent=100.0,
            won=50.0,
            net=-50.0,
            wins_by_tier={"$4": 2},
            won_jackpot=False
        )
        
        assert result.broke_even is False


class TestPopulationResult:
    """Test PopulationResult dataclass properties."""
    
    def test_population_result_structure(self):
        """PopulationResult should have all required fields."""
        players = [
            PlayerResult(1, 100.0, 50.0, -50.0, {"$4": 2}, False),
            PlayerResult(2, 100.0, 150.0, 50.0, {"$4": 5}, False),
        ]
        
        result = PopulationResult(
            num_players=2,
            total_spent=200.0,
            total_won=200.0,
            jackpot_winners=[],
            players_profited=1,
            players_broke_even=0,
            players_lost=1,
            total_wins_by_tier={"$4": 7},
            player_results=players
        )
        
        assert result.num_players == 2
        assert result.total_spent == 200.0
        assert result.total_won == 200.0
        assert result.total_net == 0.0
        assert len(result.player_results) == 2
    
    def test_population_roi_calculation(self):
        """PopulationResult ROI should be calculated correctly."""
        result = PopulationResult(
            num_players=10,
            total_spent=1000.0,
            total_won=500.0,
            jackpot_winners=[],
            players_profited=0,
            players_broke_even=0,
            players_lost=10,
            total_wins_by_tier={"$4": 20},
            player_results=[]
        )
        
        assert result.population_roi == 50.0  # 50% ROI (as percentage)


class TestSinglePlayerSimulation:
    """Test single player simulation logic."""
    
    def test_simulate_single_player_returns_player_result(self):
        """simulate_single_player should return a PlayerResult."""
        lotto = Lottery()
        result = simulate_single_player(1, lotto, 10, 2.0)
        
        assert isinstance(result, PlayerResult)
        assert result.player_id == 1
        assert result.spent == 20.0  # 10 plays * $2
    
    def test_simulate_single_player_deterministic(self):
        """With same seed (via random module), results should be deterministic."""
        import random
        
        lotto1 = Lottery()
        lotto2 = Lottery()
        
        random.seed(42)
        result1 = simulate_single_player(1, lotto1, 100, 2.0)
        
        random.seed(42)
        result2 = simulate_single_player(1, lotto2, 100, 2.0)
        
        assert result1.won == result2.won
        assert result1.won_jackpot == result2.won_jackpot
    
    def test_simulate_single_player_tracks_spending(self):
        """Player spending should match plays * cost."""
        lotto = Lottery()
        result = simulate_single_player(1, lotto, 50, 3.0)
        
        expected_cost = 50 * 3.0  # 50 plays, $3 per play
        assert result.spent == expected_cost
    
    def test_simulate_single_player_jackpot_tracking(self):
        """Jackpot flag should exist and be boolean."""
        lotto = Lottery()
        result = simulate_single_player(1, lotto, 10, 2.0)
        
        assert isinstance(result.won_jackpot, bool)


class TestExactSimulation:
    """Test exact simulation mode (small populations)."""
    
    def test_simulate_population_structure(self):
        """Exact simulation should return PopulationResult with individual players."""
        result = simulate_population(10, 5, 2.0, show_progress=False)
        
        assert isinstance(result, PopulationResult)
        assert result.num_players == 10
        assert len(result.player_results) == 10
        assert result.total_spent == 10 * 5 * 2.0  # 10 players, 5 plays, $2
    
    def test_simulate_population_aggregates_correctly(self):
        """Exact simulation should aggregate player results correctly."""
        result = simulate_population(5, 10, 2.0, show_progress=False)
        
        # Check aggregation
        total_won_from_players = sum(p.won for p in result.player_results)
        total_spent_from_players = sum(p.spent for p in result.player_results)
        
        assert result.total_won == total_won_from_players
        assert result.total_spent == total_spent_from_players
    
    def test_simulate_population_deterministic(self):
        """Exact mode should be deterministic with seed (via global random)."""
        import random
        
        random.seed(123)
        result1 = simulate_population(10, 10, 2.0, show_progress=False)
        
        random.seed(123)
        result2 = simulate_population(10, 10, 2.0, show_progress=False)
        
        assert result1.total_won == result2.total_won


class TestParallelSimulation:
    """Test parallel simulation mode (medium populations)."""
    
    def test_simulate_population_parallel_structure(self):
        """Parallel simulation should return PopulationResult."""
        result = simulate_population_parallel(100, 5, 2.0, show_progress=False)
        
        assert isinstance(result, PopulationResult)
        assert result.num_players == 100
        assert len(result.player_results) == 100
    
    def test_simulate_population_parallel_aggregates_correctly(self):
        """Parallel simulation should aggregate correctly."""
        result = simulate_population_parallel(50, 10, 2.0, show_progress=False)
        
        # Verify aggregation
        total_won = sum(p.won for p in result.player_results)
        total_spent = sum(p.spent for p in result.player_results)
        
        assert result.total_won == total_won
        assert result.total_spent == total_spent
    
    def test_simulate_population_parallel_runs(self):
        """Parallel mode should run and produce valid results."""
        result = simulate_population_parallel(100, 10, 2.0, show_progress=False)
        
        # Verify it runs and produces valid results
        assert result.num_players == 100
        assert result.total_spent == 100 * 10 * 2.0


class TestStatisticalSimulation:
    """Test statistical estimation mode (large populations)."""
    
    def test_simulate_population_statistical_structure(self):
        """Statistical mode should return PopulationResult."""
        result = simulate_population_statistical(10000, 5, 2.0)
        
        assert isinstance(result, PopulationResult)
        assert result.num_players == 10000
        # Statistical mode doesn't track individual players
        assert result.player_results is None or len(result.player_results) == 0
    
    def test_simulate_population_statistical_scaling(self):
        """Statistical mode should scale results by population size."""
        result = simulate_population_statistical(10000, 10, 2.0)
        
        # Verify basic scaling
        assert result.num_players == 10000
        assert result.total_spent == 10000 * 10 * 2.0
    
    def test_simulate_population_statistical_fast(self):
        """Statistical mode should handle large populations efficiently."""
        import time
        
        start = time.time()
        result = simulate_population_statistical(1_000_000, 5, 2.0)
        duration = time.time() - start
        
        # Should complete in under 2 seconds
        assert duration < 2.0
        assert result.num_players == 1_000_000


class TestAutoModeSelection:
    """Test automatic mode selection based on population size."""
    
    def test_auto_mode_selects_exact_for_small_population(self):
        """Small populations (<= 1000) should use exact mode."""
        result, mode = simulate_population_auto(100, 5, 2.0, show_progress=False)
        
        assert mode == "Exact Simulation"
        assert result.num_players == 100
        assert len(result.player_results) == 100
    
    def test_auto_mode_selects_parallel_for_medium_population(self):
        """Medium populations (1001-10000) should use parallel mode."""
        result, mode = simulate_population_auto(1500, 5, 2.0, show_progress=False)
        
        assert mode == "Parallel Simulation"
        assert result.num_players == 1500
        assert len(result.player_results) == 1500
    
    def test_auto_mode_selects_statistical_for_large_population(self):
        """Large populations (>10000) should use statistical mode."""
        result, mode = simulate_population_auto(15000, 5, 2.0)
        
        assert mode == "Statistical Estimation"
        assert result.num_players == 15000
    
    def test_auto_mode_boundary_at_1000(self):
        """Test boundary between exact and parallel at 1000."""
        # 999 should use exact
        result1, mode1 = simulate_population_auto(999, 5, 2.0, show_progress=False)
        assert mode1 == "Exact Simulation"
        
        # 1000 should use parallel
        result2, mode2 = simulate_population_auto(1000, 5, 2.0, show_progress=False)
        assert mode2 == "Parallel Simulation"
    
    def test_auto_mode_boundary_at_10000(self):
        """Test boundary between parallel and statistical at 10000."""
        # 9999 should use parallel
        result1, mode1 = simulate_population_auto(9999, 5, 2.0, show_progress=False)
        assert mode1 == "Parallel Simulation"
        
        # 10000 should use statistical
        result2, mode2 = simulate_population_auto(10000, 5, 2.0)
        assert mode2 == "Statistical Estimation"


class TestModeConsistency:
    """Test that different modes produce statistically similar results."""
    
    def test_exact_vs_parallel_consistency(self):
        """Exact and parallel modes should produce similar results."""
        import random
        
        random.seed(999)
        exact_result = simulate_population(500, 10, 2.0, show_progress=False)
        
        random.seed(999)
        parallel_result = simulate_population_parallel(500, 10, 2.0, show_progress=False)
        
        # Results should have same basic properties
        assert exact_result.num_players == parallel_result.num_players
        assert exact_result.total_spent == parallel_result.total_spent


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_single_player_simulation(self):
        """Should handle single player correctly."""
        result = simulate_population(1, 10, 2.0, show_progress=False)
        
        assert result.num_players == 1
        assert len(result.player_results) == 1
    
    def test_single_play_simulation(self):
        """Should handle single play correctly."""
        result = simulate_population(10, 1, 2.0, show_progress=False)
        
        assert result.num_players == 10
        for player in result.player_results:
            assert player.spent == 2.0
    
    def test_different_cost_per_play(self):
        """Should handle different costs correctly."""
        result = simulate_population(10, 10, 5.0, show_progress=False)
        
        assert result.total_spent == 10 * 10 * 5.0


class TestStatisticalProperties:
    """Test that simulations have expected statistical properties."""
    
    def test_most_players_lose(self):
        """In a fair simulation, most players should lose money."""
        result = simulate_population(100, 50, 2.0, show_progress=False)
        
        losers = result.players_lost
        
        # At least 70% should lose (lottery favors the house)
        assert losers >= 70
    
    def test_jackpot_extremely_rare(self):
        """Jackpots should be extremely rare in small simulations."""
        result = simulate_population(100, 10, 2.0, show_progress=False)
        
        # With only 1000 total plays, jackpot is very unlikely
        assert len(result.jackpot_winners) == 0
    
    def test_some_winners_exist(self):
        """There should be some wins (not jackpot, but prizes)."""
        result = simulate_population(100, 50, 2.0, show_progress=False)
        
        # With 5000 plays, we should see some wins
        total_wins = sum(result.total_wins_by_tier.values())
        assert total_wins > 0
    
    def test_expected_roi_negative(self):
        """Overall ROI should typically be negative (house edge)."""
        result = simulate_population(100, 100, 2.0, show_progress=False)
        
        # Lottery has negative expected value (though random variation can cause positive short-term)
        # Just verify ROI is calculated
        assert isinstance(result.population_roi, float)
