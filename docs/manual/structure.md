# Structure

## Networks

Everything is inside a Network object to avoid global variables and allow for parallel simulations easily. 

Populations are created with `net.add()`, projections with `net.connect()`.

```python
net = Network()

pop = net.add(100, Izhikevich())

proj = net.connect(pop, pop.ge)
proj.dense(w=1.0)

net.compile()

net.simulate(1000.)

net.save("data.h5")
```

Networks can be inherited for a better parameterization and to allow finer control of the operations:

```python
class BG(Network):
    
    def __init__(self, N):

        self.N = N

		super(self, BG).__init__(dt=1.0)

    def build(self):

		self.striatum = self.add(N, MSN())
		self.gpi = self.add(N/10, GPI())
		self.gpe = self.add(N/10, GPE())
		self.thal = self. add(N, Thal())
				
		self.str_gpi = self.connect(striatum, gpi.gi, Covariance)
		self.str_gpi.dense(w=1.0)

    def step(self):

        # Transmission
        for proj in self.projections():
            proj.transmit()

        # Update neural equations
        for pop in self.populations():
            pop.update()

        # Update synaptic equations
        for proj in self.projections()
            proj.update()
		


```

## Neurons

Neurons have to be defined as classes. This allows to pass them default parameter values in the constructor and simplify instantiation of populations:

```python
pop1 = net.add(100, Izhikevich(a = 0.02))
pop2 = net.add(100, Izhikevich(a = 0.2))
```

There is no explicit distinction between parameters and variables anymore, but between `Values` and `Arrays`:

* Values take a single value for the whole population.
* Arrays take one value per neuron.

An attribute is a variable if it is modified in `update()`, otherwise it is a parameter...

Rate-coded neurons only need to define `update()`:

```python
class RateCoded(ann.Neuron):
    """
    Simple rate-coded neuron.
    """

    def __init__(self, tau):

        self.tau = self.Value(tau)

        self.ge = self.Array(init=0.0)

        self.v = self.Array(init=0.0)
        self.r = self.Array(init=0.0)

    def update(self):

        # n will contain all variables of the model as sympy symbols, 
        # plus some operations (ite = if/then/else)
        with self.Equations() as n:

            # One can declare intermediary variables 
            # that won't be allocated in memory!
            shunting = n.ite(n.ge > 1, n.ge, 0)
            
            # ODEs use the dX_dt trick
            n.dv_dt = (n.ge + shunting + sp.exp(n.v**2) - n.v) / n.tau
            
            # Sympy functions can be used directly
            n.r = sp.tanh(n.v)
```

Spiking neuron declares additionally `spike()` and `reset()`:

```python
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
```

The `Equations()` context provides `sympy` symbols for each value/array of the neuron, plus some specific ones (`t`, `dt`, `spike` for spike emission, etc).

Derivatives are symbolically set as `dX_dt`.

All sympy operations (math `C99`) can be used.

## Areas

We introduce back the notion of Area / node / subnetwork, grouping several populations and their internal connections together:

* cortical columns
* reusable ensembles (BG, Hipp)
* hybrid networks (rate-coded -> spiking, with a specific projection interface)
* multi-scale networks, using DTI data for long-range connections between reservoirs

```python
class BG (ANNarchy.Area):
	
	def __init__(self):
		"Mostly creating the populations and projections."
		
		self.striatum = self.add(1000, MSN())
		self.gpi = self.add(100, GPI())
		self.gpe = self.add(100, GPE())
		self.thal = self. add(100, Thal())
				
		self.str_gpi = self.connect(striatum, gpi.gi, Covariance)
		self.str_gpi.dense(w=1.0)
		
		super(self, BG).__init__()
		
net = Network()

cortex = net.add(10000, Cx())
bg = net.add(BG())

cx_bg = net.connect(cortex, bg.striatum.ge, Corticostriatal)
cx_bg.dense(w=Normal(0.0, 1.0))
```



