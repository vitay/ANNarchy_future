from ANNarchy_future import *
import numpy as np

Izhikevich = Neuron(
    parameters= {
        'a': Array(value=0.02, dtype=np.float32),
        'b': Array(value=0.2),
        'c': Value(value=-65.), 
        'd': Value(value=-2.),
        'VT': Value(value=30.),
        
    },
    equations = {
        'v': Array(eq="dv/dt = 0.04 * v^2 + 5.0 * v + 140.0 - u + I + ge - gi", value=0.0, method='midpoint'),
        'u': Array(
                eq="du/dt = a * (b * v - u)", 
                value=0.0, 
                method='midpoint', 
                min=0.0, 
                max=100.
            ),
        'ge': Array(eq=None, value=0.0, during_refractory=False), 
        'gi': Array(eq="tau*dgi/dt=-gi", during_refractory=False),
    },
    spike = "v > VT",
    reset = ["v = c", "u += d"],
    refractory = None, # the default, or 5.0, or "tau_ref",
    name = "Izhikevich",
    description = """
        Some text describing what the neuron does, 
        equations that can be parsed for the report, etc.
    """
)

default_spiking_synapse = Synapse(
    psp = "w",
    operator = "sum" # optional
)

STDP = Synapse(
    parameters = {
        'tau_plus': Value(value=20.),
        'tau_minus': Value(value=20.),
    },
    equations = {
       'x': Array(eq="tau_plus  * dx/dt = -x", method="event-driven"),
       'y': Array(eq="tau_minus  * dy/dt = -y", method="event-driven"),
    },
    psp = "w",
    pre_spike = [
        "x +=1 ",
        "w +=y ",
    ],
    post_spike = [
        "y +=1",
        "w -=x",
    ],
    name = "STDP",
    description= """
        Spike timing dependent plasticity
    """
)

# Create the network
net = Network(dt=0.1)

# Add a population
pop = net.add(10, Izhikevich)
print(pop.a)
pop.a = np.linspace(1.0, 10.0, pop.size)
print(pop.a)
print(type(pop.a))

# Connect the population with itself
proj = net.connect(pre=pop, post=pop, target=pop.ge, synapse=default_spiking_synapse)
proj.fill(w=1.0, d=5.0) # default is a single weight for the whole population, not learnable
proj.fill(w=1.0, d=5.0, connector=Dense(self_connection=False), format='lil')
proj.fill(w=Uniform(0.0, 1.0), d=5.0, connector=Sparse(p=0.1))
proj.fill(w=1.0, d=5.0, connector=One2One())
proj.fill(w=np.ones((pop.size, pop.size)), d=0.0)

# Monitor
net.monitor([pop.v, proj.w])

# Compile the network
net.compile(backend='single') # single, openmp, mpi, cuda, etc

# Simulate
net.simulate(1000, monitor=True)

# Retrieve the simulated data
data = net.recorded()
