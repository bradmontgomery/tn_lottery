TN lotto
========

Tools to generate random numbers for the `Tennessee lottery <http://www.tnlottery.com>`_.


Usage
-----

Run ``python play.py -h`` for instructions. You can generate numbers for
various games.


Examples
--------

Generate one set of numbers for all games
::

    $ python play.py

    TN Lottery Numbers!
    --------------------------------------------------
    Powerball: 03, 19, 22, 35, 47 - Powerball: 05
    Mega Millions: 08, 24, 26, 29, 53 - Mega Ball: 31
    TN Cash: 01, 05, 09, 17, 33 - Cash Ball: 04
    Cash 4: 7639
    Cash 3: 666

Generate 5 sets of numbers for the Powerball
::

    $ ./play.py -g powerball -n 5

    powerball Numbers!
    --------------------------------------------------
    Powerball: 05, 17, 23, 24, 54 - Powerball: 04
    Powerball: 21, 23, 35, 53, 58 - Powerball: 07
    Powerball: 15, 27, 30, 43, 47 - Powerball: 03
    Powerball: 17, 33, 38, 53, 55 - Powerball: 27
    Powerball: 03, 08, 29, 31, 35 - Powerball: 26


*Disclaimer*: You'll likely just lose your money.


Simulation
----------

Run ``python simulation.py``. Currently, this just simulates playing the
powerball, with the following assumptions:

- We play every time possible (two times a week)
- We play 5 sets of numbers on each ticket at $2 each ($10 / ticket)
- We only "win" if we hit the jackpot (all numbers match)

The simulation runs until we hit the jackpot or kill it with Ctrl-C. It'll
periodically print the number of years you've played and the amount of money
spent playing.
