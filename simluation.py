#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Assumptions:
- We're just playing the Powerball
- We play every time possible (2-times a week)
- We play 5 sets of numbers for $2 each ($10 / ticket)
- We only "win" if we hit the jackpot (all numbers match)
-- todo: match minor wins.

"""

import sys
from lottery import Lottery

COST = 2  # cost per play
PLAYS = 5  # The number of sets we play for each ticket


def ticket(lotto, plays, cost):
    numbers = []
    for i in range(plays):
        numbers.append(lotto.powerball)
    return (numbers, plays * cost)


def run():
    spent = 0  # how much we've spent
    ticket_numbers = []  # a list of possible lotto numbers
    trials = 0  # Number of time's we've bought a ticket

    lotto = Lottery()
    winning_numbers = lotto.powerball()

    while winning_numbers not in ticket_numbers:
        # Buy a new ticket
        ticket_numbers, cost = ticket(lotto, PLAYS, COST)

        # Track the cost & number of times we've played
        spent += cost
        trials += 1
        sys.stdout.write(".")

        # Print some info every year
        if trials % 104 == 0:
            years = trials / 104
            sys.stdout.write("\n{0} Years, ${1}\n".format(years, spent))

    sys.stdout.write("\n\nYOU WON!\n\n")
    years = trials / 104
    sys.stdout.write("\n{0} Years, ${1}\n".format(years, spent))


if __name__ == "__main__":
    run()
