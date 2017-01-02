r"""Example computation server."""
import time

import numpy as np
from matplotlib import pyplot as plt

from asyncplot import server
from asyncplot import client


class Plotter(object):
    def __init__(self):
        plt.clf()

    def draw(self, x, y):
        plt.ioff()
        plt.clf()
        plt.plot(x, y)
        print y
        plt.ion()
        plt.draw()
        time.sleep(0.5)     # Pretend this is slow
    

def run():
    # Create a plot instance.  This should launch the plot process, and pop up
    # the initial plot window.
    with server.Server(Plotter=Plotter, wait_for_client=True) as p:
        # Start the computation
        x = np.linspace(0, 2*np.pi, 10)
        dt = 0.001
        t = 0
        for n in xrange(10000000):
            if n % 100000 == 0:
                print n
            t += dt
            y = np.sin(x - t)
            p.update(x=x, y=y)


def run_client():
    #create the Client instance and pass the Plotter object, then call run().
    c = client.Client(Plotter=Plotter)
    c.run()


if __name__ == "__main__":
    run()
