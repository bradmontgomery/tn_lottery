#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Powerball Prize Tier Definitions

Contains the official Powerball prize structure and payout logic.
Current rules as of 2021 (5 white balls from 1-69, 1 powerball from 1-26).
"""

from collections import namedtuple

# Prize tier definition
PrizeTier = namedtuple('PrizeTier', ['name', 'white_matches', 'powerball_match', 'prize'])

# Powerball Prize Structure
# Reference: https://www.powerball.com/prizes-and-odds
POWERBALL_PRIZES = [
    PrizeTier("Jackpot", 5, True, "JACKPOT"),
    PrizeTier("Match 5", 5, False, 1_000_000),
    PrizeTier("Match 4 + PB", 4, True, 50_000),
    PrizeTier("Match 4", 4, False, 100),
    PrizeTier("Match 3 + PB", 3, True, 100),
    PrizeTier("Match 3", 3, False, 7),
    PrizeTier("Match 2 + PB", 2, True, 7),
    PrizeTier("Match 1 + PB", 1, True, 4),
    PrizeTier("Match PB", 0, True, 4),
]


def count_matches(player_numbers, winning_numbers):
    """Count how many white balls match between player and winning numbers.
    
    Args:
        player_numbers: List of 5 white ball numbers (player's selection)
        winning_numbers: List of 5 white ball numbers (winning draw)
        
    Returns:
        Integer count of matching numbers
    """
    player_set = set(player_numbers)
    winning_set = set(winning_numbers)
    return len(player_set & winning_set)


def check_prize_tier(player_draw, winning_draw):
    """Determine the prize tier for a single play.
    
    Args:
        player_draw: Tuple of (white_balls_list, powerball_number)
        winning_draw: Tuple of (white_balls_list, powerball_number)
        
    Returns:
        PrizeTier namedtuple if won, None if no prize
    """
    player_white, player_pb = player_draw
    winning_white, winning_pb = winning_draw
    
    white_matches = count_matches(player_white, winning_white)
    pb_match = (player_pb == winning_pb)
    
    # Check each prize tier in order
    for tier in POWERBALL_PRIZES:
        if (tier.white_matches == white_matches and 
            tier.powerball_match == pb_match):
            return tier
    
    return None


def calculate_payout(player_draws, winning_draw):
    """Calculate total winnings from multiple plays.
    
    Args:
        player_draws: List of tuples (white_balls_list, powerball_number)
        winning_draw: Tuple of (white_balls_list, powerball_number)
        
    Returns:
        Tuple of (total_winnings: float, wins_by_tier: dict, won_jackpot: bool)
        wins_by_tier maps tier name to count
    """
    total_winnings = 0.0
    wins_by_tier = {}
    won_jackpot = False
    
    for player_draw in player_draws:
        tier = check_prize_tier(player_draw, winning_draw)
        if tier:
            # Track win count by tier
            wins_by_tier[tier.name] = wins_by_tier.get(tier.name, 0) + 1
            
            # Add to winnings
            if tier.prize == "JACKPOT":
                won_jackpot = True
                # We don't add jackpot to total_winnings (it's special)
            else:
                total_winnings += tier.prize
    
    return (total_winnings, wins_by_tier, won_jackpot)


def get_tier_display_info():
    """Get formatted information about all prize tiers for display.
    
    Returns:
        List of tuples (tier_name, prize_amount_str)
    """
    return [(tier.name, f"${tier.prize:,}" if tier.prize != "JACKPOT" else "Jackpot") 
            for tier in POWERBALL_PRIZES]


def get_expected_value_info():
    """Get information about expected value and odds.
    
    Note: These are the official odds, not calculated from simulation.
    Reference: https://www.powerball.com/prizes-and-odds
    
    Returns:
        Dict with odds and expected value information
    """
    # Official Powerball odds (1 in X)
    odds = {
        "Jackpot": 292_201_338,
        "Match 5": 11_688_053,
        "Match 4 + PB": 913_129,
        "Match 4": 36_525,
        "Match 3 + PB": 14_494,
        "Match 3": 579.76,
        "Match 2 + PB": 701.33,
        "Match 1 + PB": 91.98,
        "Match PB": 38.32,
    }
    
    # Calculate expected value (excluding jackpot)
    ev = 0.0
    for tier in POWERBALL_PRIZES:
        if tier.prize != "JACKPOT":
            probability = 1.0 / odds[tier.name]
            ev += probability * tier.prize
    
    return {
        "odds": odds,
        "expected_value_per_play": ev,
        "roi_excluding_jackpot": ev / 2.0,  # $2 per play
        "overall_win_probability": 1.0 / 24.87,  # ~4% chance to win anything
    }
