# pylint: disable=no-member
import ANNarchy_future as ann

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def f(x):
    return sp.log(1 + x)

class RateCoded(ann.Neuron):
    """
    Simple rate-coded neuron.
    """

    def __init__(self, tau):

        self.tau = self.Parameter(tau)

        self.r_mean = self.Variable(0.0, shared=True)

        self.ge = self.Variable(init=0.0, input=True)

        self.v = self.Variable(init=0.0)
        self.r = self.Variable(init=0.0, output=True)

    def update(self):

        # n will contain all variables of the model as sympy symbols, plus some operations (ite = if/then/else)
        with self.Equations(method='euler') as n:

            # One can declare intermediary variables that won't be allocated in memory!
            shunting = n.ite(n.ge > 1, n.ge, 0)
            
            # ODEs use the dX_dt trick
            n.dv_dt = (n.ge + shunting + sp.exp(n.v**3) + n.Uniform(-1, 1) - n.v) / n.tau
            n.v = n.clip(n.v, 0.0) # sets minimum bound
            #n.v = n.clip(n.v, None, 1.0) # sets maximum bound
            #n.v = n.clip(n.v, 0.0, 1.0) # sets both bounds
            
            # Sympy functions can be used directly
            n.r = f(n.v)



class Hebb(ann.Synapse):
    """
    Default rate-coded synapse.
    """

    def __init__(self, eta):

        self.eta = self.Parameter(eta)

        self.alpha = self.Parameter(0.1)

        self.w = self.Variable(init=0.0)

        self.mw = self.Variable(init=0.0)

    def update(self):

        with self.Equations() as s:

            s.w += s.eta * s.pre.r * s.post.r 

            s.mw += s.alpha * s.mw + (1 - s.alpha)*s.w

    def transmit(self):

        with self.Equations() as s:
            
            s.target += s.w * s.pre.r


net = ann.Network(verbose=2)

neur = RateCoded(tau=20.)

pop = net.add(10, neur)

proj = net.connect(pop, pop, 'ge', Hebb(eta=0.01))

proj = net.connect(pop, pop, 'gi', Hebb(eta=0.01))

# proj.dense(w=1.0)

net.compile()

net.step()
