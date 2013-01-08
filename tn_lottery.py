#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate random numbers for playing the TN lottery: http://www.tnlottery.com

Disclaimer: You'll likely just lose your money.

"""
import random


class Lottery(object):

    def _choose(self, num, val_range):
        """Randomly choose ``num`` values in the ``val_range`` range."""
        vmin, vmax = val_range
        return [str(random.randint(vmin, vmax)) for i in xrange(num)]

    def powerball(self):
        """Powerball - http://www.tnlottery.com/howtoplay/#power"""
        values = self._choose(num=5, val_range=(1, 59))
        powerball = self._choose(num=1, val_range=(1, 39))[0]
        return "Powerball:\n\t{0} - Powerball: {1}".format(
            ', '.join(values),
            powerball
        )

    def mega_millions(self):
        """Mega Millions - http://www.tnlottery.com/howtoplay/#mega"""
        values = self._choose(num=5, val_range=(1, 56))
        megaball = self._choose(num=1, val_range=(1, 46))[0]
        return "Mega Millions:\n\t{0} - Mega Ball: {1}".format(
            ', '.join(values),
            megaball
        )


if __name__ == "__main__":
    # Prints randomly generated numbers for the different TN Lottery games.

    lottery = Lottery()
    print("\n-------------------\nTN Lottery Numbers!\n-------------------\n")
    print(lottery.powerball())
    print(lottery.mega_millions())
    print("\nGood Luck! (you'll need it)\n\n")
