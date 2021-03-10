import ANNarchy_future as ann

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

class Izhikevich(ann.Neuron):

    def __init__(self, params):

        self.a = self.Value(params['a'])
        self.b = self.Value(params['b'])
        self.c = self.Value(params['c'])
        self.d = self.Value(params['d'])
        self.v_thresh = self.Value(params['v_thresh'])
        self.i_offset = self.Value(params['i_offset'])

        self.ge = self.Array(init=0.0)
        self.gi = self.Array(init=0.0)
        
        self.v = self.Array(init=-65.0)
        self.u = self.Array(init=-13.0)

    def update(self):

        with self.Equations() as n:

            I = n.ge - n.gi + n.i_offset # + noise
            n.dv_dt = n.C(4e-2) * n.v**2 + n.C(5.0) * n.v + n.C(140.0) - n.u + I
            n.du_dt = n.a * (n.b * n.v - n.u)

        return n

    def spike(self):

        with self.Equations() as n:

            n.spike = n.v >= n.v_thresh

    def reset(self):

        with self.Equations() as n:

            n.v = n.c
            n.u += n.d

        return n

net = ann.Network(verbose=2)
params = {'a': 0.02, 'b': 0.2, 'c': -65., 'd': 8., 'v_thresh': 30., 'i_offset': 0.0}
net.add(1000, Izhikevich(params))
