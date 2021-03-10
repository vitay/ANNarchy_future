import sys
import logging

from .Array import Value, Array
from .Neuron import Neuron
from ..parser.PopulationParser import PopulationParser

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

    Additionaly, all values and arrays of the neuron type are accessible as attributes:

    ```python
    class Leaky(Neuron):
        def __init__(self):
            self.tau = self.Value(20.)
            self.r = self.Array(0.0)

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
        self._spiking = False

        # Name
        self.name : str = name

        # Internal stuff
        self._net = None
        self._attributes = {}
        self._values_list = []
        self._arrays_list = []

        self.logger = logging.getLogger(__name__)
        self.logger.info("Population created with " + str(self.size) + " neurons.")

    def _register(self, net, id_pop):
        "Called by Network."

        self.logger.debug("Registering population with ID " + str(id_pop))

        self._net = net
        self.id_pop = id_pop

        if self.name is None:
            self.name = "Population " + str(self.id_pop)
        self.logger.debug("Population's name is set to " + str(self.name))

    def _analyse(self):

        # List attributes
        current_attributes = list(self._neuron_type.__dict__.keys())

        for attr in current_attributes:
            if isinstance(getattr(self._neuron_type, attr), (Value, )):
                self._values_list.append(attr)
                self._attributes[attr] = getattr(self._neuron_type, attr)._copy()
                self._attributes[attr]._instantiate(self.shape)
            if isinstance(getattr(self._neuron_type, attr), (Array, )):
                self._arrays_list.append(attr)
                self._attributes[attr] = getattr(self._neuron_type, attr)._copy()
                self._attributes[attr]._instantiate(self.shape)

        # Get lists of values and arrays
        self.attributes = list(self._attributes.keys())
        self.logger.info("Found attributes: " + str(self.attributes))

        # Set the attributes to the neuron
        self._neuron_type.attributes = self.attributes
        self._neuron_type._values_list = self._values_list
        self._neuron_type._arrays_list = self._arrays_list
        self.logger.info("Values: " + str(self._values_list))
        self.logger.info("Arrays: " + str(self._arrays_list))

        # Create the population parser
        self.logger.debug("Creating population parser.")
        self._parser = PopulationParser(self)
        self._parser.analyse()


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