#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lottery import Lottery


if __name__ == "__main__":
    # Prints randomly generated numbers for the different TN Lottery games.
    lottery = Lottery()
    print("\n-------------------\nTN Lottery Numbers!\n-------------------\n")
    print(lottery.powerball())
    print(lottery.mega_millions())
    print(lottery.tn_cash())
    print(lottery.cash_four())
    print(lottery.cash_three())
    print("\nGood Luck! (you'll need it)\n\n")
