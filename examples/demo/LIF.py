# pylint: disable=no-member
import ANNarchy_future as ann

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def f(x):
    return sp.log(1 + x)

class LIF(ann.Neuron):

    def __init__(self, params):

        self.tau = self.Parameter(params['tau'])
        self.V_th = self.Parameter(params['V_th'])

        self.ge = self.Variable(init=0.0, input=True)
        self.v = self.Variable(init=0.0)
        self.u = self.Variable(init=0.0)

    def update(self):

        with self.Equations(method='midpoint') as n:

            n.dv_dt = (n.ge - n.u - n.v) / n.tau
            n.du_dt = (n.v - n.u) / n.tau

            n.dge_dt = (-n.ge) / n.tau

    def spike(self):

        with self.Equations() as n:

            n.spike = n.v >= n.V_th

    def reset(self):

        with self.Equations() as n:

            n.v = 0.0

net = ann.Network()
#net = ann.Network(verbose=3, logfile="test.log") # for debugging
pop = net.add(100, LIF({'tau': 20., 'V_th': 1.0}))

net.compile()