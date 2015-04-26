#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys

from lottery import Lottery


parser = argparse.ArgumentParser(
    description="Generate numbers for some TN Lottery Games"
)
parser.add_argument(
    '-l',
    '--list',
    action="store_true",
    help="list available games"
)
parser.add_argument(
    '-g',
    '--game',
    type=str,
    help="play a single game (see the list)"
)
parser.add_argument(
    '-n',
    '--number',
    type=int,
    default=1,
    help="number of plays"
)


def run():
    # Parse the options.
    options = parser.parse_args()

    # Print a list of games & exist (if applicable)
    if options.list:
        print("""\nYou may use the following with the -g or --game flag:
    * powerball -- Powerball.
    * megamillions -- Mega Millions.
    * hotlotto -- Hot Lotto Sizzler.
    * tncash -- Tennessee Cash.
    * cash4 -- Cash 4.
    * cash3 -- Cash 3.
        """)
        sys.exit()

    # The full list of games.
    games = ['powerball', 'megamillions', 'hotlotto', 'tncash', 'cash4', 'cash3']
    if options.game and options.game not in games:
        sys.stderr.write("\n{0} is not a valid game.\n".format(options.game))
        sys.exit(1)
    elif options.game:
        games = [options.game]

    # Prints randomly generated numbers for the selected TN Lottery games.
    print("\n" + "+" * 50)
    game_name = options.game if options.game else "TN Lottery"
    print("{0} Numbers!".format(game_name))
    print("-" * 50)
    for n in range(options.number):
        lottery = Lottery()
        if "powerball" in games:
            print(lottery.print_powerball())
        if "megamillions" in games:
            print(lottery.print_mega_millions())
        if "hotlotto" in games:
            print(lottery.print_hot_lotto_sizzler())
        if "tncash" in games:
            print(lottery.print_tn_cash())
        if "cash4" in games:
            print(lottery.print_cash_four())
        if "cash3" in games:
            print(lottery.print_cash_three())
        if options.number > 1 and len(games) > 1:
            print("-" * 50)
    print("\nGood Luck! (you'll need it)\n\n")


if __name__ == "__main__":
    run()
