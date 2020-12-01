from .Population import Population
from .Projection import Projection

import copy
 
class Network(object):
    """
    Neural Network.
    """
    def __init__(self, dt=1.0):
        """
        :param dt: simulation step size in ms. Default: 1.0. 
        """
        self.dt = dt

        # Populations
        self.populations = {}
        self.population_names = []
        self._population_attributes = {}

        # Projection
        self.projections = {}
        self.projection_names = []

    #############################################################
    ### Populations
    #############################################################

    def add(self, shape, neuron, name=None):
        "Adds a population to the network."
        if name is None:
            name = 'pop'+str(len(self.population_names))

        pop = Population(self, shape, neuron, name)

        self.populations[name] = pop
        self.population_names.append(name)
        self._population_attributes[name] = {}

        pop._init()

        return pop

    #############################################################
    ### Projections
    #############################################################

    def connect(self, pre, post, target, synapse, name=None):
        "Connects two populations."
        if name is None:
            name = 'proj'+str(len(self.projection_names))

        proj = Projection(self, pre, post, target, synapse, name)
        
        self.projections[name] = proj
        self.projection_names.append(name)
        
        return proj

    #############################################################
    ### Simulation
    #############################################################

    def simulate(self, duration, monitor=True):
        "Simulates for the given duration."
        pass

    #############################################################
    ### Monitoring
    #############################################################

    def monitor(self, arrays):
        "Monitors different arrays."
        self.arrays = arrays

    def recorded(self):
        "Returns recorded arrays."
        return {}


    #############################################################
    ### Compilation
    #############################################################

    def compile(self, backend='single'):
        "Compiles the network."
        self._backend = backend

        # Code generation

        # Instantiate the network
        self._instantiate()

    def _instantiate(self):
        pass

    def _register_population_attribute(self, pop, name, val):
        "Attributes are centralized at the network level to communicate with the C++ kernel."
        # Deep copy the array, as it may be reused in many populations
        val = copy.deepcopy(val)

        # Populate it if it is an array
        val._instantiate(pop.shape)

        # Store the attribute
        self._population_attributes[pop.name][name] = val
