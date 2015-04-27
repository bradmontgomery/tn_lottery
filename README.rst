TN lotto
========

Tools to generate random numbers for the `Tennessee lottery <http://www.tnlottery.com>`_, and a very simple powerball simulator.

Supported Games
---------------

* Powerball
* Mega Millions
* Hot Lotto Sizzler
* Tennessee Cash
* Cash 4
* Cash 3

Usage
-----

1. Check out this repo.
2. Run ``python tn_lottery/play.py -h`` for instructions.

You can generate numbers forvarious games.


Examples
--------

Generate one set of numbers for all games
::

    $ python tn_lottery/play.py

    TN Lottery Numbers!
    --------------------------------------------------
    Powerball: 03, 19, 22, 35, 47 - Powerball: 05
    Mega Millions: 08, 24, 26, 29, 53 - Mega Ball: 31
    TN Cash: 01, 05, 09, 17, 33 - Cash Ball: 04
    Cash 4: 7639
    Cash 3: 666

Generate 5 sets of numbers for the Powerball
::

    $ ./tn_lottery/play.py -g powerball -n 5

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

Run ``python tn_lottery/simulation.py``. Currently, this just simulates playing
the powerball, with the following assumptions:

- You are an immortal playing the TN powerball every chance you get. (2-times
  a week; powerball is Wed & Sat)
- You play 5 sets of numbers for $2 each ($10 / ticket)
- You only "win" if you hit the jackpot (5 numbers match + the powerball number)

The simulation runs until we hit the jackpot or kill it with Ctrl-C. It'll
periodically print the number of years you've played and the amount of money
spent playing.
