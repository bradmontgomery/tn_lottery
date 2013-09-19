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
        return [str(v) for v in values]

    def powerball(self):
        """Powerball - http://www.tnlottery.com/howtoplay/#power"""
        values = self._choose(num=5, val_range=(1, 59))
        powerball = self._choose(num=1, val_range=(1, 35))[0]
        return "Powerball: {0} - Powerball: {1}".format(
            ', '.join(self._to_str_list(values)),
            powerball
        )

    def mega_millions(self):
        """Mega Millions - http://www.tnlottery.com/howtoplay/#mega"""
        values = self._choose(num=5, val_range=(1, 56))
        megaball = self._choose(num=1, val_range=(1, 46))[0]
        return "Mega Millions: {0} - Mega Ball: {1}".format(
            ', '.join(self._to_str_list(values)),
            megaball
        )

    def tn_cash(self):
        """Tennessee Cash - http://www.tnlottery.com/howtoplay/#tncash"""
        values = self._choose(num=5, val_range=(1, 35))
        cash_ball = self._choose(num=1, val_range=(1, 5))[0]
        return "TN Cash: {0} - Cash Ball: {1}".format(
            ', '.join(self._to_str_list(values)),
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
