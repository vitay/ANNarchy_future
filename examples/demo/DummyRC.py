# pylint: disable=no-member
import ANNarchy_future as ann

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

mu = 0.0
sigma = 0.1

class RC(ann.Neuron):

    def __init__(self, params):

        self.tau = self.Parameter(params['tau'])
        self.mu = self.Parameter(0.0)
        self.sigma = self.Parameter(0.1)

        self.r = self.Variable(init=0.0)
        self.u = self.Variable(init=0.0)

    def update(self):

        with self.Equations(method='rk4') as n:

            n.dr_dt = (n.cast(1.0) - n.u + n.Uniform(0.0, 1.0) - n.r) / n.tau
            n.du_dt = (1.0 + n.r + n.Normal(n.mu + 0.01, n.sigma) - n.u) / n.tau

net = ann.Network(verbose=2)
pop = net.add((2, 2), RC({'tau': 20.0}))

net.compile()

print(pop.tau)
pop.tau = 10.0
print(pop.tau)

vs = [pop.r[1,1]]

for t in range(200):
    net.step()
    vs.append(pop.r[1,1])

pop.u = 0.0

for t in range(200):
    net.step()
    vs.append(pop.r[1,1])

plt.plot(vs)
plt.show()
