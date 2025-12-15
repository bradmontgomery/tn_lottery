"""
Statistical Validation Tests

Tests to verify that the lottery simulation's statistical properties
match theoretical probabilities and expected values.

These tests run large numbers of simulations to validate:
- Powerball jackpot odds (1 in 292,201,338)
- Overall win rate (~4%)
- Expected value (~50% return on investment)
- Prize tier distribution matches theoretical odds
"""

import random
from collections import defaultdict

import pytest

from tn_lottery.lottery import Lottery
from tn_lottery.payouts import check_prize_tier, POWERBALL_PRIZES
from tn_lottery.simulation import generate_ticket, play_drawing


class TestPowerballJackpotOdds:
    """Test that jackpot odds match theoretical probability."""
    
    def test_jackpot_odds_large_sample(self):
        """
        Test jackpot odds over a large sample.
        
        Theoretical odds: 1 in 292,201,338
        With 100k plays, we don't expect to see a jackpot.
        This test verifies no jackpots occur in reasonable samples.
        """
        random.seed(42)
        lotto = Lottery()
        jackpot_count = 0
        plays = 100_000
        
        for _ in range(plays):
            _, _, hit_jackpot, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if hit_jackpot:
                jackpot_count += 1
        
        # With 100k plays, probability of ANY jackpot is ~0.034%
        # So we expect 0 jackpots in most runs
        assert jackpot_count <= 1, f"Got {jackpot_count} jackpots in {plays} plays - suspiciously high"
    
    def test_no_jackpot_in_moderate_sample(self):
        """Verify that jackpots are rare in moderate-sized samples."""
        random.seed(123)
        lotto = Lottery()
        jackpot_count = 0
        
        for _ in range(10_000):
            _, _, hit_jackpot, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if hit_jackpot:
                jackpot_count += 1
        
        assert jackpot_count == 0, "Jackpot should be extremely rare"


class TestOverallWinRate:
    """Test that overall win rate matches theoretical ~4%."""
    
    def test_win_rate_large_sample(self):
        """
        Test overall win rate over 50k plays.
        
        Theoretical win rate: ~3.97% (1 in 25.17)
        Expected range: 3.5% to 4.5%
        """
        random.seed(42)
        lotto = Lottery()
        total_plays = 50_000
        wins = 0
        
        for _ in range(total_plays):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if winnings > 0:
                wins += 1
        
        win_rate = wins / total_plays
        
        # Allow 10% margin (3.57% to 4.37%)
        assert 0.0357 <= win_rate <= 0.0437, f"Win rate {win_rate:.4f} outside expected range 3.57%-4.37%"
    
    def test_win_rate_medium_sample(self):
        """Test win rate with medium sample size."""
        random.seed(999)
        lotto = Lottery()
        total_plays = 25_000
        wins = 0
        
        for _ in range(total_plays):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if winnings > 0:
                wins += 1
        
        win_rate = wins / total_plays
        
        # Allow wider margin for smaller sample (3.0% to 5.0%)
        assert 0.03 <= win_rate <= 0.05, f"Win rate {win_rate:.4f} outside expected range 3%-5%"
    
    def test_loss_rate_is_majority(self):
        """Verify that most plays result in losses."""
        random.seed(555)
        lotto = Lottery()
        total_plays = 10_000
        losses = 0
        
        for _ in range(total_plays):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if winnings == 0:
                losses += 1
        
        loss_rate = losses / total_plays
        
        # Should be around 96%
        assert loss_rate > 0.94, f"Loss rate {loss_rate:.4f} too low - should be >94%"


class TestExpectedValue:
    """Test that expected value approximates 50% return."""
    
    def test_roi_large_sample(self):
        """
        Test ROI over large sample.
        
        Powerball theoretical return: ~50% (varies by jackpot size)
        For non-jackpot prizes only, ROI should be significantly negative.
        """
        random.seed(42)
        lotto = Lottery()
        total_spent = 0.0
        total_won = 0.0
        plays = 100_000
        cost = 2.0
        
        for _ in range(plays):
            winnings, _, _, cost_spent = play_drawing(lotto, plays_per_ticket=1, cost_per_play=cost)
            total_spent += cost_spent
            total_won += winnings
        
        roi = ((total_won - total_spent) / total_spent) * 100
        
        # Without jackpot, ROI should be very negative (around -90% to -70%)
        # This validates that the game is -EV without jackpot
        assert roi < -50, f"ROI {roi:.2f}% too high - lottery should have negative expected value"
        assert roi > -95, f"ROI {roi:.2f}% too low - seems broken"
    
    def test_total_payout_less_than_spent(self):
        """Verify that over many plays, total payout < total spent."""
        random.seed(789)
        lotto = Lottery()
        total_spent = 0.0
        total_won = 0.0
        
        for _ in range(50_000):
            winnings, _, _, cost = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            total_spent += cost
            total_won += winnings
        
        # Should lose money overall
        assert total_won < total_spent, "Should lose money over many plays"
        
        # But should win something
        assert total_won > 0, "Should win some prizes"
    
    def test_average_winnings_per_play(self):
        """Test average winnings per play."""
        random.seed(321)
        lotto = Lottery()
        total_won = 0.0
        plays = 25_000
        
        for _ in range(plays):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            total_won += winnings
        
        avg_win = total_won / plays
        
        # Average win should be small (< $1 per $2 play without jackpot)
        assert avg_win < 1.0, f"Average win ${avg_win:.2f} too high"
        assert avg_win > 0.05, f"Average win ${avg_win:.2f} too low"


class TestPrizeTierDistribution:
    """Test that prize tier distribution matches expected odds."""
    
    def test_tier_distribution_ratios(self):
        """
        Test that prize tiers appear in expected ratios.
        
        Lower tiers should be MUCH more common than higher tiers.
        """
        random.seed(42)
        lotto = Lottery()
        tier_counts = defaultdict(int)
        plays = 50_000
        
        for _ in range(plays):
            # Generate a player ticket
            player_numbers, _ = generate_ticket(lotto, plays=1, cost_per_play=2.0)
            player = player_numbers[0]
            
            # Generate winning numbers
            winning = lotto.powerball()
            
            # Check what tier we hit
            tier = check_prize_tier(player, winning)
            if tier:
                tier_counts[tier.name] += 1
        
        # Verify we have some wins
        total_wins = sum(tier_counts.values())
        assert total_wins > 0, "Should have some wins"
        
        # Lower prizes should be most common
        tier_9_count = tier_counts.get("Match PB", 0)
        tier_8_count = tier_counts.get("Match 1+PB", 0)
        
        # Tier 9 (just PB) should be most common
        assert tier_9_count > tier_8_count, "Lower tiers should be more common"
    
    def test_higher_tiers_are_rare(self):
        """Verify that higher prize tiers are rare."""
        random.seed(999)
        lotto = Lottery()
        high_tier_count = 0
        plays = 10_000
        
        for _ in range(plays):
            player_numbers, _ = generate_ticket(lotto, plays=1, cost_per_play=2.0)
            player = player_numbers[0]
            winning = lotto.powerball()
            tier = check_prize_tier(player, winning)
            
            if tier and tier.prize >= 10000:  # High value prizes
                high_tier_count += 1
        
        # High value prizes should be very rare
        high_tier_rate = high_tier_count / plays
        assert high_tier_rate < 0.001, f"High tier rate {high_tier_rate:.4f} too high"
    
    def test_tier_9_most_common(self):
        """
        Tier 9 (just matching PB) should be the most common prize.
        
        Theoretical odds: 1 in 38.32
        Expected rate: ~2.61%
        """
        random.seed(777)
        lotto = Lottery()
        tier_9_count = 0
        plays = 25_000
        
        for _ in range(plays):
            player_numbers, _ = generate_ticket(lotto, plays=1, cost_per_play=2.0)
            player = player_numbers[0]
            winning = lotto.powerball()
            tier = check_prize_tier(player, winning)
            
            if tier and tier.name == "Match PB":
                tier_9_count += 1
        
        tier_9_rate = tier_9_count / plays
        
        # Should be around 2.61% (allow 2% to 3.5% range)
        assert 0.02 <= tier_9_rate <= 0.035, f"Tier 9 rate {tier_9_rate:.4f} outside expected range 2%-3.5%"


class TestStatisticalConsistency:
    """Test that results are statistically consistent across runs."""
    
    def test_consistent_win_rate_across_seeds(self):
        """Win rate should be consistent across different random seeds."""
        win_rates = []
        plays_per_seed = 10_000
        
        for seed in [100, 200, 300, 400, 500]:
            random.seed(seed)
            lotto = Lottery()
            wins = 0
            
            for _ in range(plays_per_seed):
                winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
                if winnings > 0:
                    wins += 1
            
            win_rate = wins / plays_per_seed
            win_rates.append(win_rate)
        
        # All win rates should be within reasonable range
        min_rate = min(win_rates)
        max_rate = max(win_rates)
        
        assert min_rate > 0.03, "Minimum win rate too low"
        assert max_rate < 0.05, "Maximum win rate too high"
        assert max_rate - min_rate < 0.015, "Win rates vary too much across seeds"
    
    def test_consistent_roi_across_seeds(self):
        """ROI should be consistent across different random seeds."""
        rois = []
        plays_per_seed = 10_000
        
        for seed in [111, 222, 333, 444, 555]:
            random.seed(seed)
            lotto = Lottery()
            total_spent = 0.0
            total_won = 0.0
            
            for _ in range(plays_per_seed):
                winnings, _, _, cost = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
                total_spent += cost
                total_won += winnings
            
            roi = ((total_won - total_spent) / total_spent) * 100
            rois.append(roi)
        
        # All ROIs should be negative and within reasonable range
        for roi in rois:
            assert roi < -50, f"ROI {roi:.2f}% not negative enough"
            assert roi > -95, f"ROI {roi:.2f}% too negative"


class TestMultiplePlayStatistics:
    """Test statistics when playing multiple times per drawing."""
    
    def test_multiple_plays_increases_win_probability(self):
        """Playing 5 times should increase win probability vs playing once."""
        random.seed(42)
        lotto = Lottery()
        
        # Single play win rate
        wins_single = 0
        for _ in range(5_000):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if winnings > 0:
                wins_single += 1
        rate_single = wins_single / 5_000
        
        # Multiple plays win rate
        random.seed(42)
        wins_multi = 0
        for _ in range(5_000):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=5, cost_per_play=2.0)
            if winnings > 0:
                wins_multi += 1
        rate_multi = wins_multi / 5_000
        
        # Multiple plays should have higher win rate
        assert rate_multi > rate_single, "Multiple plays should increase win rate"
    
    def test_multiple_plays_still_negative_ev(self):
        """Even with multiple plays per drawing, EV should still be negative."""
        random.seed(999)
        lotto = Lottery()
        total_spent = 0.0
        total_won = 0.0
        
        for _ in range(5_000):
            winnings, _, _, cost = play_drawing(lotto, plays_per_ticket=10, cost_per_play=2.0)
            total_spent += cost
            total_won += winnings
        
        # Should still lose money overall
        assert total_won < total_spent, "Should lose money even with multiple plays"


class TestEdgeCaseStatistics:
    """Test statistical properties of edge cases."""
    
    def test_zero_cost_doesnt_affect_win_rate(self):
        """Win rate should be independent of cost per play."""
        random.seed(42)
        lotto = Lottery()
        
        # Test with $2 cost
        wins_2 = 0
        for _ in range(5_000):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
            if winnings > 0:
                wins_2 += 1
        
        # Test with $3 cost (same seed)
        random.seed(42)
        wins_3 = 0
        for _ in range(5_000):
            winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=3.0)
            if winnings > 0:
                wins_3 += 1
        
        # Win counts should be identical (same random draws)
        assert wins_2 == wins_3, "Win rate should be independent of cost"
    
    def test_small_sample_variance(self):
        """Small samples should show more variance."""
        win_rates = []
        
        for seed in range(10):
            random.seed(seed)
            lotto = Lottery()
            wins = 0
            
            for _ in range(100):  # Small sample
                winnings, _, _, _ = play_drawing(lotto, plays_per_ticket=1, cost_per_play=2.0)
                if winnings > 0:
                    wins += 1
            
            win_rates.append(wins / 100)
        
        # Should see significant variance
        variance = max(win_rates) - min(win_rates)
        assert variance > 0.02, "Small samples should show variance"


class TestPrizeTierProbabilities:
    """Test specific prize tier probabilities."""
    
    def test_match_pb_only_frequency(self):
        """
        Test Match PB (Tier 9) frequency.
        
        Theoretical: 1 in 38.32 = 2.61%
        """
        random.seed(42)
        lotto = Lottery()
        match_pb_count = 0
        plays = 25_000
        
        for _ in range(plays):
            player_numbers, _ = generate_ticket(lotto, plays=1, cost_per_play=2.0)
            player = player_numbers[0]
            winning = lotto.powerball()
            tier = check_prize_tier(player, winning)
            
            if tier and tier.name == "Match PB":
                match_pb_count += 1
        
        frequency = match_pb_count / plays
        
        # Allow 20% margin: 2.1% to 3.1%
        assert 0.021 <= frequency <= 0.031, f"Match PB frequency {frequency:.4f} outside expected range"
    
    def test_match_3_frequency(self):
        """
        Test Match 3 (Tier 7) frequency.
        
        Theoretical: 1 in 579.76 = 0.17%
        """
        random.seed(42)
        lotto = Lottery()
        match_3_count = 0
        plays = 50_000
        
        for _ in range(plays):
            player_numbers, _ = generate_ticket(lotto, plays=1, cost_per_play=2.0)
            player = player_numbers[0]
            winning = lotto.powerball()
            tier = check_prize_tier(player, winning)
            
            if tier and tier.name == "Match 3":
                match_3_count += 1
        
        frequency = match_3_count / plays
        
        # Allow wide margin: 0.1% to 0.3%
        assert 0.001 <= frequency <= 0.003, f"Match 3 frequency {frequency:.5f} outside expected range"
