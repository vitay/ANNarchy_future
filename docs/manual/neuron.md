# Neuron

```python
class LIF(ann.Neuron):

    def __init__(self, params):

        self.tau = self.Parameter(params['tau'])
        self.V_th = self.Parameter(params['V_th'])

        self.ge = self.Variable(init=0.0)
        self.v = self.Variable(init=0.0)

    def update(self):

        with self.Equations() as n:

            n.dv_dt = (n.ge - n.v) / n.tau


    def spike(self):

        with self.Equations() as n:

            n.spike = n.v >= n.V_th

    def reset(self):

        with self.Equations() as n:

            n.v = 0
```