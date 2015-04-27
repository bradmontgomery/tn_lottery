#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Question: How much money & how much time would it take (for one person) to win
the Powerball?

Assumptions:

- A single immortal is playing.
- We're just playing the Powerball
- We play every time possible (2-times a week; powerball is Wed & Sat)
- We play 5 sets of numbers for $2 each ($10 / ticket)
- We only "win" if we hit the jackpot (5 numbers match + the powerball number)

"""

import locale
from lottery import Lottery

COST = 2  # cost per play
PLAYS = 5  # The number of sets we play for each ticket
# Report progress every few years (52 weeks * 2 plays/week = 104 is 1 year)
YEARS = 104 * 10


def ticket(lotto, plays, cost):
    """Generate a 'play ticket' consistent of numbers to play;

    * lotto: An instance of the Lottery class.
    * plays: The number of *plays* to generate (i.e. the set of numbers)
    * cost: how much a single play costs.

    Returns a tuple of consisting of 1) a list of powerball numbers, and 2)
    the cost of playing.

    """
    numbers = []
    for i in range(plays):
        numbers.append(lotto.powerball())
    return (numbers, plays * cost)


def check(plays, winning_numbers):
    """Check if the given plays match any of the winning numbers:

    * plays is a list of powerball play tuples.
    * winning_numbers is a powerball play tuple.

    A powerball play tuple contains a list of 5 numbers followed by a
    powerball number. e.g. ([6, 20, 21, 52, 55], 27)

    """
    return winning_numbers in plays


def play(lotto):
    plays, cost = ticket(lotto, PLAYS, COST)
    winning_numbers = lotto.powerball()
    return (check(plays, winning_numbers), cost)


def report(trials, spent, won=False):
    """Print how how many years have been played & how much money spent."""
    if won:
        print("YOU WON!")
    years = int(trials/YEARS * 10)  # years grouped by 10s
    cost = locale.currency(spent, grouping=True)
    print("{0} Years: {1}".format(years, cost))


def run():
    locale.setlocale(locale.LC_ALL, '')  # Assume US because that's where TN is.

    lotto = Lottery()
    spent = 0  # how much we've spent
    trials = 0  # Number of time's we've bought a ticket
    won = False

    while not won:
        # Generate a ticket & a drawing
        won, cost = play(lotto)
        spent += cost
        trials += 1

        # Print some info every year
        if trials % YEARS == 0:
            report(trials, spent, won)

    report(trials, spent, won)


if __name__ == "__main__":
    run()
