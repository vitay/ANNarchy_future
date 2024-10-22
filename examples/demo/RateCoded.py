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
        self.alpha = self.Parameter(0.1)

        self.r_mean = self.Variable(0.0, shared=True)

        self.ge = self.Variable(init=0.0, input=True)

        self.v = self.Variable(init=0.0)
        self.r = self.Variable(init=0.0, output=True)

    def update(self, n, method="rk4"):        
        
        # One can declare intermediary variables that won't be allocated in memory!
        shunting = n.ite(n.ge > 1, n.ge, 0)
        
        # ODEs use the dX_dt trick
        n.dv_dt = (n.ge + shunting + sp.exp(n.v**3) + n.Uniform(-1, 1) - n.v) / n.tau
        
        n.v = n.clip(n.v, 0.0) # sets minimum bound
        #n.v = n.clip(n.v, None, 1.0) # sets maximum bound
        #n.v = n.clip(n.v, 0.0, 1.0) # sets both bounds
        
        # Sympy functions can be used directly
        n.r = f(n.v)

        # Shared variables
        n.r_mean = n.alpha * n.r_mean + (1 - n.alpha) * 1.0



class Hebb(ann.Synapse):
    """
    Default rate-coded synapse.
    """

    def __init__(self, eta):

        self.eta = self.Parameter(eta)

        self.w = self.Variable(init=0.0)

    def update(self, s):

        s.w += s.eta * s.pre.r * s.post.r

    def transmit(self, s):

        s.target += s.w * s.pre.r


net = ann.Network(verbose=2)

neur = RateCoded(tau=20.)

pop = net.add(10, neur)
pop2 = net.add(10, neur)

proj = net.connect(pop, pop, 'ge', Hebb(eta=0.01))

proj2 = net.connect(pop, pop2, 'gi', Hebb(eta=0.01))

# proj.dense(w=1.0)

net.compile()

net.step()

print('Done')

print(type(pop.v))