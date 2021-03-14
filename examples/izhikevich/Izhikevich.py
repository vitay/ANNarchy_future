import ANNarchy_future as ann

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

class Izhikevich(ann.Neuron):

    def __init__(self, params):

        self.a = self.Parameter(params['a'])
        self.b = self.Parameter(params['b'])
        self.c = self.Parameter(params['c'])
        self.d = self.Parameter(params['d'])

        self.v_thresh = self.Parameter(params['v_thresh'])
        self.i_offset = self.Parameter(params['i_offset'])

        self.ge = self.Variable(init=0.0)
        self.gi = self.Variable(init=0.0)
        
        self.v = self.Variable(init=-65.0)
        self.u = self.Variable(init=-13.0)

    def update(self):

        with self.Equations(method="midpoint") as n:

            I = n.ge - n.gi + n.i_offset # + noise

            n.dv_dt = n.cast(4e-2) * n.v**2 + n.cast(5.0) * n.v + n.cast(140.0) - n.u + I
            
            n.du_dt = n.a * (n.b * n.v - n.u)

    def spike(self):

        with self.Equations() as n:

            n.spike = (n.v >= n.v_thresh)

    def reset(self):

        with self.Equations() as n:

            n.v = n.c
            n.u += n.d


net = ann.Network(verbose=2)

params = {'a': 0.02, 'b': 0.2, 'c': -65., 'd': 8., 'v_thresh': 30., 'i_offset': 0.0}

net.add(1000, Izhikevich(params))
