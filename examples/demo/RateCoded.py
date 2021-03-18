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
            n.dv_dt = (n.ge + shunting + sp.exp(n.v**3) - n.v) / n.tau
            n.v = n.clip(n.v, 1.0) # sets minimum bound
            #n.v = n.clip(n.v, None, 0.0) # sets maximum bound
            #n.v = n.clip(n.v, 0.0, 1.0) # sets both bounds
            
            # Sympy functions can be used directly
            n.r = f(n.v)


net = ann.Network(verbose=2)
pop = net.add(10, RateCoded(tau=20.))

print("Attributes:", pop.attributes)

print("Tau:", pop.tau)
print("v = 0:", pop.v)

pop.v = 1.

print("v = 1:", pop.v)

pop.v *= 5.

print("v = 5:", pop.v)

pop.v[:3] = 1.

print("v[:3] = 1:", pop.v)


print()
print(pop.parser)

net.compile()
