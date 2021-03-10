import ANNarchy_future as ann

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt


class LIF(ann.Neuron):

    def __init__(self, params):

        self.tau = self.Value(params['tau'])
        self.V_th = self.Value(params['V_th'])

        self.ge = self.Array(init=0.0)
        self.v = self.Array(init=0.0)

    def update(self):

        with self.Equations() as n:

            n.dv_dt = (n.ge - n.v) / n.tau


    def spike(self):

        with self.Equations() as n:

            n.spike = n.v >= n.V_th

    def reset(self):

        with self.Equations() as n:

            n.v = 0

net = ann.Network()
#net = ann.Network(verbose=3, logfile="test.log") # for debugging
pop = net.add(100, LIF({'tau': 20., 'V_th': 1.0}))

print()
print(pop._parser)

net.compile()