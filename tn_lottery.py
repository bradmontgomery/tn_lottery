#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate random numbers for playing the TN lottery: http://www.tnlottery.com

Disclaimer: You'll likely just lose your money.


This code is available for use under the terms of the MIT License.

Copyright (c) 2013, Brad Montgomery <brad@bradmontgomery.net>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import random


class Lottery(object):

    def _choose(self, num, val_range):
        """Randomly choose ``num`` values in the ``val_range`` range."""
        vmin, vmax = val_range
        return sorted([str(random.randint(vmin, vmax)) for i in range(num)])

    def powerball(self):
        """Powerball - http://www.tnlottery.com/howtoplay/#power"""
        values = self._choose(num=5, val_range=(1, 59))
        powerball = self._choose(num=1, val_range=(1, 35))[0]
        return "Powerball: {0} - Powerball: {1}".format(
            ', '.join(values),
            powerball
        )

    def mega_millions(self):
        """Mega Millions - http://www.tnlottery.com/howtoplay/#mega"""
        values = self._choose(num=5, val_range=(1, 56))
        megaball = self._choose(num=1, val_range=(1, 46))[0]
        return "Mega Millions: {0} - Mega Ball: {1}".format(
            ', '.join(values),
            megaball
        )

    def tn_cash(self):
        """Tennessee Cash - http://www.tnlottery.com/howtoplay/#tncash"""
        values = self._choose(num=5, val_range=(1, 35))
        cash_ball = self._choose(num=1, val_range=(1, 5))[0]
        return "TN Cash: {0} - Cash Ball: {1}".format(
            ', '.join(values),
            cash_ball
        )

    def cash_four(self):
        """Cash 4 - http://www.tnlottery.com/howtoplay/#cash4chart"""
        value = self._choose(num=1, val_range=(0, 9999))[0]
        return "Cash 4: {0:{fill}4d}".format(int(value), fill='0')

    def cash_three(self):
        """Cash 3 - http://www.tnlottery.com/howtoplay/#cashchart"""
        value = self._choose(num=1, val_range=(0, 999))[0]
        return "Cash 3: {0:{fill}3d}".format(int(value), fill='0')

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
