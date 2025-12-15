"""Test suite for payouts.py - Prize tier detection and payout calculations."""

import pytest
from tn_lottery.payouts import (
    count_matches,
    check_prize_tier,
    calculate_payout,
    get_tier_display_info,
    get_expected_value_info,
    POWERBALL_PRIZES,
)


class TestCountMatches:
    """Test the count_matches function."""
    
    def test_count_matches_all_match(self):
        """All 5 numbers match."""
        assert count_matches([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 5
    
    def test_count_matches_none_match(self):
        """No numbers match."""
        assert count_matches([1, 2, 3, 4, 5], [6, 7, 8, 9, 10]) == 0
    
    def test_count_matches_some_match(self):
        """3 numbers match."""
        assert count_matches([1, 2, 3, 4, 5], [3, 4, 5, 6, 7]) == 3
    
    def test_count_matches_one_match(self):
        """1 number matches."""
        assert count_matches([1, 2, 3, 4, 5], [1, 10, 20, 30, 40]) == 1
    
    def test_count_matches_two_match(self):
        """2 numbers match."""
        assert count_matches([1, 2, 3, 4, 5], [4, 5, 60, 61, 62]) == 2
    
    def test_count_matches_four_match(self):
        """4 numbers match."""
        assert count_matches([1, 2, 3, 4, 5], [1, 2, 3, 4, 99]) == 4
    
    def test_count_matches_order_independent(self):
        """Order shouldn't matter."""
        assert count_matches([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]) == 5
        assert count_matches([10, 20, 30, 40, 50], [50, 40, 30, 20, 10]) == 5


class TestCheckPrizeTier:
    """Test the check_prize_tier function for all prize tiers."""
    
    def test_jackpot_detection(self):
        """5 white + powerball = jackpot."""
        player = ([1, 2, 3, 4, 5], 10)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Jackpot"
        assert tier.prize == "JACKPOT"
        assert tier.white_matches == 5
        assert tier.powerball_match is True
    
    def test_match_5_no_powerball(self):
        """5 white balls, no powerball = $1,000,000."""
        player = ([1, 2, 3, 4, 5], 10)
        winning = ([1, 2, 3, 4, 5], 20)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match 5"
        assert tier.prize == 1_000_000
        assert tier.white_matches == 5
        assert tier.powerball_match is False
    
    def test_match_4_plus_powerball(self):
        """4 white balls + powerball = $50,000."""
        player = ([1, 2, 3, 4, 50], 10)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match 4 + PB"
        assert tier.prize == 50_000
        assert tier.white_matches == 4
        assert tier.powerball_match is True
    
    def test_match_4_no_powerball(self):
        """4 white balls, no powerball = $100."""
        player = ([1, 2, 3, 4, 50], 10)
        winning = ([1, 2, 3, 4, 5], 20)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match 4"
        assert tier.prize == 100
        assert tier.white_matches == 4
        assert tier.powerball_match is False
    
    def test_match_3_plus_powerball(self):
        """3 white balls + powerball = $100."""
        player = ([1, 2, 3, 50, 60], 10)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match 3 + PB"
        assert tier.prize == 100
        assert tier.white_matches == 3
        assert tier.powerball_match is True
    
    def test_match_3_no_powerball(self):
        """3 white balls, no powerball = $7."""
        player = ([1, 2, 3, 50, 60], 10)
        winning = ([1, 2, 3, 4, 5], 20)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match 3"
        assert tier.prize == 7
        assert tier.white_matches == 3
        assert tier.powerball_match is False
    
    def test_match_2_plus_powerball(self):
        """2 white balls + powerball = $7."""
        player = ([1, 2, 50, 60, 61], 10)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match 2 + PB"
        assert tier.prize == 7
        assert tier.white_matches == 2
        assert tier.powerball_match is True
    
    def test_match_1_plus_powerball(self):
        """1 white ball + powerball = $4."""
        player = ([1, 50, 60, 61, 62], 10)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match 1 + PB"
        assert tier.prize == 4
        assert tier.white_matches == 1
        assert tier.powerball_match is True
    
    def test_match_powerball_only(self):
        """Only powerball matches = $4."""
        player = ([50, 60, 61, 62, 63], 10)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is not None
        assert tier.name == "Match PB"
        assert tier.prize == 4
        assert tier.white_matches == 0
        assert tier.powerball_match is True
    
    def test_no_prize_no_matches(self):
        """No matches should return None."""
        player = ([50, 60, 61, 62, 63], 20)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is None
    
    def test_no_prize_white_only_no_powerball(self):
        """Matches white balls but not powerball (2 white) = no prize."""
        player = ([1, 2, 50, 60, 61], 20)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is None
    
    def test_no_prize_one_white_no_powerball(self):
        """1 white match without powerball = no prize."""
        player = ([1, 50, 60, 61, 62], 20)
        winning = ([1, 2, 3, 4, 5], 10)
        tier = check_prize_tier(player, winning)
        assert tier is None


class TestCalculatePayout:
    """Test the calculate_payout function."""
    
    def test_single_jackpot_win(self):
        """Single jackpot win."""
        player_draws = [([1, 2, 3, 4, 5], 10)]
        winning_draw = ([1, 2, 3, 4, 5], 10)
        
        winnings, wins_by_tier, won_jackpot = calculate_payout(player_draws, winning_draw)
        
        assert won_jackpot is True
        assert winnings == 0.0  # Jackpot not included in winnings total
        assert wins_by_tier == {"Jackpot": 1}
    
    def test_multiple_small_wins(self):
        """Multiple small prize wins."""
        player_draws = [
            ([1, 50, 60, 61, 62], 10),  # Match 1 + PB = $4
            ([50, 60, 61, 62, 63], 10),  # Match PB = $4
            ([1, 2, 3, 50, 60], 10),     # Match 3 + PB = $100
        ]
        winning_draw = ([1, 2, 3, 4, 5], 10)
        
        winnings, wins_by_tier, won_jackpot = calculate_payout(player_draws, winning_draw)
        
        assert won_jackpot is False
        assert winnings == 108.0  # 4 + 4 + 100
        assert wins_by_tier == {
            "Match 1 + PB": 1,
            "Match PB": 1,
            "Match 3 + PB": 1,
        }
    
    def test_no_wins(self):
        """No winning plays."""
        player_draws = [
            ([50, 60, 61, 62, 63], 20),
            ([51, 61, 62, 63, 64], 21),
        ]
        winning_draw = ([1, 2, 3, 4, 5], 10)
        
        winnings, wins_by_tier, won_jackpot = calculate_payout(player_draws, winning_draw)
        
        assert won_jackpot is False
        assert winnings == 0.0
        assert wins_by_tier == {}
    
    def test_duplicate_tier_wins(self):
        """Multiple wins in the same tier."""
        player_draws = [
            ([50, 60, 61, 62, 63], 10),  # Match PB = $4
            ([51, 61, 62, 63, 64], 10),  # Match PB = $4
            ([52, 62, 63, 64, 65], 10),  # Match PB = $4
        ]
        winning_draw = ([1, 2, 3, 4, 5], 10)
        
        winnings, wins_by_tier, won_jackpot = calculate_payout(player_draws, winning_draw)
        
        assert won_jackpot is False
        assert winnings == 12.0  # 3 * $4
        assert wins_by_tier == {"Match PB": 3}
    
    def test_mixed_wins_and_losses(self):
        """Mix of winning and losing plays."""
        player_draws = [
            ([1, 2, 3, 4, 5], 20),      # Match 5 = $1,000,000
            ([50, 60, 61, 62, 63], 20), # No match
            ([1, 2, 3, 50, 60], 10),    # Match 3 + PB = $100
            ([99, 98, 97, 96, 95], 99), # No match
        ]
        winning_draw = ([1, 2, 3, 4, 5], 10)
        
        winnings, wins_by_tier, won_jackpot = calculate_payout(player_draws, winning_draw)
        
        assert won_jackpot is False
        assert winnings == 1_000_100.0
        assert wins_by_tier == {
            "Match 5": 1,
            "Match 3 + PB": 1,
        }
    
    def test_jackpot_plus_other_wins(self):
        """Jackpot win plus other prizes in same batch."""
        player_draws = [
            ([1, 2, 3, 4, 5], 10),    # Jackpot
            ([1, 2, 3, 50, 60], 10),  # Match 3 + PB = $100
        ]
        winning_draw = ([1, 2, 3, 4, 5], 10)
        
        winnings, wins_by_tier, won_jackpot = calculate_payout(player_draws, winning_draw)
        
        assert won_jackpot is True
        assert winnings == 100.0  # Only non-jackpot prizes counted
        assert wins_by_tier == {
            "Jackpot": 1,
            "Match 3 + PB": 1,
        }


class TestPrizeStructure:
    """Test the prize structure constants and helper functions."""
    
    def test_powerball_prizes_count(self):
        """Should have exactly 9 prize tiers."""
        assert len(POWERBALL_PRIZES) == 9
    
    def test_powerball_prizes_ordered(self):
        """Prize tiers should be ordered from highest to lowest."""
        expected_order = [
            "Jackpot",
            "Match 5",
            "Match 4 + PB",
            "Match 4",
            "Match 3 + PB",
            "Match 3",
            "Match 2 + PB",
            "Match 1 + PB",
            "Match PB",
        ]
        actual_order = [tier.name for tier in POWERBALL_PRIZES]
        assert actual_order == expected_order
    
    def test_get_tier_display_info(self):
        """get_tier_display_info should return formatted tier information."""
        info = get_tier_display_info()
        assert len(info) == 9
        assert info[0] == ("Jackpot", "Jackpot")
        assert info[1] == ("Match 5", "$1,000,000")
        assert info[2] == ("Match 4 + PB", "$50,000")
        assert info[8] == ("Match PB", "$4")
    
    def test_get_expected_value_info(self):
        """get_expected_value_info should return odds and EV information."""
        info = get_expected_value_info()
        
        assert "odds" in info
        assert "expected_value_per_play" in info
        assert "roi_excluding_jackpot" in info
        assert "overall_win_probability" in info
        
        # Check some specific odds
        assert info["odds"]["Jackpot"] == 292_201_338
        assert info["odds"]["Match 5"] == 11_688_053
        assert info["odds"]["Match PB"] == 38.32
        
        # Expected value should be positive but less than $2
        assert 0 < info["expected_value_per_play"] < 2.0
        
        # ROI should be less than 1.0 (losing game)
        assert 0 < info["roi_excluding_jackpot"] < 1.0
        
        # Win probability should be around 4%
        assert 0.03 < info["overall_win_probability"] < 0.05
