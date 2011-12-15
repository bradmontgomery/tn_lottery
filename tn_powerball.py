"""
Generate random numbers for playing the TN lotter.
http://www.tnlottery.com/howtoplay/default.aspx#power
"""
import random

def powerball(num_values=5, num_pball=1, val_range=(1,59), pball_range=(1,39)):
    """
    Generate ``num_values`` numbers in the range provided by ``val_range``
    and ``num_pball`` powerball numbers in the range provided by ``pball_range``.
    """

    vmin, vmax = val_range
    values = [str(random.randint(vmin, vmax)) for i in xrange(num_values)]
    
    pmin, pmax = pball_range
    pball_values = [str(random.randint(pmin, pmax)) for i in xrange(num_pball)]

    return "Lottery Numbers: %s - PB %s" % (', '.join(values), ', '.join(pball_values))


if __name__== "__main__":
    print "\n\n", powerball(), "\n\n"