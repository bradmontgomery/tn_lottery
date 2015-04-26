#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random


class Lottery(object):

    def _choose(self, num, val_range):
        """Randomly choose ``num`` values in the ``val_range`` range."""
        vmin, vmax = val_range
        return sorted([random.randint(vmin, vmax) for i in range(num)])

    def _to_str_list(self, values):
        """convert a list of int's to a list of str's."""
        return ["{0:02d}".format(v) for v in values]

    def powerball(self):
        """Returns a tuple of (``values``, ``powerball``) for the Powerball.
        See: http://www.tnlottery.com/howtoplay/#power

        """
        values = self._choose(num=5, val_range=(1, 59))
        powerball = self._choose(num=1, val_range=(1, 35))[0]
        return (values, powerball)

    def print_powerball(self):
        """Returns a string containing powerball numbers."""
        values, powerball = self.powerball()
        return "Powerball: {0} - Powerball: {1:02d}".format(
            ', '.join(self._to_str_list(values)),
            powerball
        )

    def mega_millions(self):
        """Returns a tuple of (``values``, ``megaball``) for Mega Millions.
        See: http://www.tnlottery.com/howtoplay/#mega

        """
        values = self._choose(num=5, val_range=(1, 56))
        megaball = self._choose(num=1, val_range=(1, 46))[0]
        return (values, megaball)

    def print_mega_millions(self):
        """Returns a string containing Mega Millions numbers."""
        values, megaball = self.mega_millions()
        return "Mega Millions: {0} - Mega Ball: {1:02d}".format(
            ', '.join(self._to_str_list(values)),
            megaball
        )

    def tn_cash(self):
        """Returns a tuple of (``values``, ``cashball``) for of Tennessee Cash.
        See: http://www.tnlottery.com/howtoplay/#tncash

        """
        values = self._choose(num=5, val_range=(1, 35))
        cash_ball = self._choose(num=1, val_range=(1, 5))[0]
        return (values, cash_ball)

    def print_tn_cash(self):
        """Returns a string containing TN Cash numbers."""
        values, cash_ball = self.tn_cash()
        return "TN Cash: {0} - Cash Ball: {1:02d}".format(
            ', '.join(self._to_str_list(values)),
            cash_ball
        )

    def cash_four(self):
        """Returns a 4-digit number for Cash 4.
        See: http://www.tnlottery.com/howtoplay/#cash4chart

        """
        return self._choose(num=1, val_range=(0, 9999))[0]

    def print_cash_four(self):
        """Returns a string containing Cash Four numbers."""
        value = self.cash_four()
        return "Cash 4: {0:{fill}4d}".format(int(value), fill='0')

    def cash_three(self):
        """Returns a 3-digit number for Cash 3.
        See: http://www.tnlottery.com/howtoplay/#cashchart

        """
        return self._choose(num=1, val_range=(0, 999))[0]

    def print_cash_three(self):
        """Returns a string containing Cash Three numbers."""
        value = self.cash_three()
        return "Cash 3: {0:{fill}3d}".format(int(value), fill='0')
