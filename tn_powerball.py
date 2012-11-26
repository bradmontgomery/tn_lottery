#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate random numbers for playing the TN lotter.
http://www.tnlottery.com/howtoplay/default.aspx#power
"""
import random


def powerball(num_values=5, num_pball=1, val_range=(1, 59),
              pball_range=(1, 39)):
    """
    Generate ``num_values`` numbers in the range provided by ``val_range``
    and ``num_pball`` powerball numbers in the range provided by
    ``pball_range``.

    """

    vmin, vmax = val_range
    values = [str(random.randint(vmin, vmax)) for i in xrange(num_values)]

    pmin, pmax = pball_range
    pball_values = [str(random.randint(pmin, pmax)) for i in xrange(num_pball)]

    return "Lottery Numbers: {0} - PB {1}".format(
        ', '.join(values),
        ', '.join(pball_values)
    )


if __name__ == "__main__":
    # Output's something like:
    #
    #   ---------------
    #   Lottery Numbers
    #   ---------------
    #
    #   2, 14, 21, 1, 5 - PB 21
    #
    print("\n\n\t---------------\n\tLottery Numbers\n\t---------------\n")
    print("\t{0}\n\n".format(powerball()))
