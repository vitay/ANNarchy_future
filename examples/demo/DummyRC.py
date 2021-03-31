# pylint: disable=no-member
import ANNarchy_future as ann

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt



class RC(ann.Neuron):

    def __init__(self, params):

        self.tau = self.Parameter(params['tau'])

        self.r = self.Variable(init=0.0)
        self.u = self.Variable(init=0.0)

    def update(self):

        with self.Equations(method='euler') as n:

            n.dr_dt = (n.cast(1.0) - n.u - n.r) / n.tau
            n.du_dt = (1.0 + n.r - n.u) / n.tau

net = ann.Network()
pop = net.add((2, 2), RC({'tau': 20.0}))

net.compile()

print(pop.tau)

vs = [pop.r[1,1]]

for t in range(200):
    net.step()
    vs.append(pop.r[1,1])

plt.plot(vs)
plt.show()
