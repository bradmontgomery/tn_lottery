#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random


class Lottery(object):

    game_data = {
        'powerball': 'Powerball',
        'megamillions': 'Mega Millions',
        'hotlotto': 'Hot Lotto Sizzler',
        'tncash': 'Tennessee Cash',
        'cash4': 'Cash 4',
        'cash3': 'Cash 3',
    }

    @staticmethod
    def title(game):
        return Lottery.game_data.get(game)

    @staticmethod
    def games():
        """A list of supported games."""
        return list(Lottery.game_data.keys())

    def _padding(self):
        """Padding size for game titles."""
        return max(len(g) for g in Lottery.game_data.values())

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
        return "{0}: {1} - {2:02d}".format(
            self.game_data['powerball'].ljust(self._padding()),
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
        return "{0}: {1} - {2:02d}".format(
            self.game_data['megamillions'].ljust(self._padding()),
            ', '.join(self._to_str_list(values)),
            megaball
        )

    def hot_lotto_sizzler(self):
        """Returns a tuple of (``values``, ``hotball``) for the Hot Lotto
        Sizzler game. See: http://www.tnlottery.com/howtoplay/#hotlotto

        """
        values = self._choose(num=5, val_range=(1, 47))
        hotball = self._choose(num=1, val_range=(1, 19))[0]
        return (values, hotball)

    def print_hot_lotto_sizzler(self):
        """Returns a string containing Hot Lotto Sizzler numbers."""
        values, hotball = self.hot_lotto_sizzler()
        return "{0}: {1} - {2:02d}".format(
            self.game_data['hotlotto'].ljust(self._padding()),
            ', '.join(self._to_str_list(values)),
            hotball
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
        return "{0}: {1} - {2:02d}".format(
            self.game_data['tncash'].ljust(self._padding()),
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
        return "{0}: {1:{fill}4d}".format(
            self.game_data['cash4'].ljust(self._padding()),
            int(value),
            fill='0'
        )

    def cash_three(self):
        """Returns a 3-digit number for Cash 3.
        See: http://www.tnlottery.com/howtoplay/#cashchart

        """
        return self._choose(num=1, val_range=(0, 999))[0]

    def print_cash_three(self):
        """Returns a string containing Cash Three numbers."""
        value = self.cash_three()
        return "{0}: {1:{fill}3d}".format(
            self.game_data['cash3'].ljust(self._padding()),
            int(value),
            fill='0'
        )
