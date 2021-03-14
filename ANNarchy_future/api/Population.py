import sys
import logging

from .Array import Parameter, Variable
from .Neuron import Neuron
from ..parser.NeuronParser import NeuronParser

class Population(object):

    """Population of neurons.

    Populations should not be created explicitly, but returned by `Network.add()`:

    ```python
    net = Network()
    pop = net.add(10, LIF())
    ```

    Attributes:
        shape: shape of the population.
        size: number of neurons.
        name: unique name of the population.
        neuron_class: name of the Neuron class

    Additionaly, all parameters and variables of the neuron type are accessible as attributes:

    ```python
    class Leaky(Neuron):
        def __init__(self):
            self.tau = self.Parameter(20.)
            self.r = self.Variable(0.0)

    net = Network()
    pop = net.add(10, Leaky())

    print(pop.tau) # 20.
    print(pop.r) # [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ```
    """

    def __init__(self, shape : tuple, neuron : Neuron, name : str):

        # Shape and size
        self.shape : tuple = tuple(shape)
        size = 1
        for n in shape:
            size *= n
        self.size : int = int(size)

        # Neuron type
        self._neuron_type = neuron

        # Name
        self.name : str = name

        # Internal stuff
        self._net = None
        self._attributes = {}

        self.logger = logging.getLogger(__name__)
        self.logger.info("Population created with " + str(self.size) + " neurons.")

    ###########################################################################
    # Interface
    ###########################################################################
    def is_spiking(self) -> bool:
        "Returns True if the neuron type is spiking."
        return self._neuron_type.is_spiking()


    ###########################################################################
    # Internal methods
    ###########################################################################
    def _register(self, net, id_pop):
        "Called by Network."

        self.logger.debug("Registering population with ID " + str(id_pop))

        self._net = net
        self.id_pop = id_pop

        if self.name is None:
            self.name = "Population " + str(self.id_pop)
        self.logger.debug("Population's name is set to " + str(self.name))

    def _analyse(self):

        # Create the population parser
        self.logger.debug("Creating neuron parser.")
        self.parser = NeuronParser(self._neuron_type)
        
        # Retrieve attributes
        self.parser.extract_variables()
        self.attributes = self.parser.attributes

        # Neuron class name
        self.neuron_class : str = self.parser.name

        # Instantiate the attributes
        for attr in self.parser.attributes:
            self._attributes[attr] = getattr(self._neuron_type, attr)._copy()
            self._attributes[attr]._instantiate(self.shape)
        
        # Analyse the equations
        self.parser.analyse_equations()

    ###########################################################################
    # Hacks for access to attributes
    ###########################################################################
    def __getattribute__(self, name):
        if name in ['attributes']:
            return object.__getattribute__(self, name)
        else:
            if hasattr(self, 'attributes') and name in self.attributes:
                return self._attributes[name].get_value()
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):

        if hasattr(self, 'attributes') and name in self.attributes:
            self._attributes[name].set_value(value)
        else:
            object.__setattr__(self, name, value)