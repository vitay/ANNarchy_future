import sys
import logging
import textwrap

import numpy as np

import ANNarchy_future.api as api
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

    def __init__(self, 
        shape : tuple, 
        neuron : 'api.Neuron', 
        name : str):

        # Shape and size
        self.shape : tuple = tuple(shape)
        size = 1
        for n in shape:
            size *= n
        self.size : int = int(size)

        # Neuron type
        self._neuron_type = neuron
        self.neuron_class:str = neuron.__class__.__name__

        # Name
        self.name : str = name

        # Internal stuff
        self._net = None
        self._attributes = {}
        self._instantiated = False

        self._logger = logging.getLogger(__name__)
        self._logger.info("Population created with " + str(self.size) + " neurons.")

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

        self._logger.debug("Registering population with ID " + str(id_pop))

        self._net = net
        self._id_pop = id_pop

        if self.name is None:
            self.name = "Population " + str(self._id_pop)
        self._logger.debug("Population's name is set to " + str(self.name))

    def _analyse(self):

        # Create the population parser
        self._logger.debug("Creating neuron parser.")
        self._parser = NeuronParser(self._neuron_type)
        
        # Retrieve attributes
        self._parser.extract_variables()
        self.attributes = self._parser.attributes

        # Instantiate the attributes
        for attr in self._parser.attributes:
            self._attributes[attr] = getattr(self._neuron_type, attr)._copy()
            self._attributes[attr]._instantiate(self.shape)
        
        # Analyse the equations
        self._parser.analyse_equations()

    ###########################################################################
    # Hacks for access to attributes
    ###########################################################################
    def __getattribute__(self, name):
        if name in ['attributes', '_instantiated']:
            return object.__getattribute__(self, name)
        else:
            if hasattr(self, 'attributes') and name in self.attributes:
                # After compile()
                if self._instantiated:
                    return self._reshape(self._net._interface.population_get(self._id_pop, name))
                # Before compile()
                else:
                    return self._attributes[name].get_value()
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):

        if hasattr(self, 'attributes') and name in self.attributes:
            # After compile()
            if self._instantiated:
                self._net._interface.population_set(self._id_pop, name, self._to_numpy(name, value))
            # Before compile()
            else:
                self._attributes[name].set_value(value)
        else:
            object.__setattr__(self, name, value)

    def _reshape(self, array:np.ndarray) -> np.ndarray:
        "Reshapes the parameter/variable to match the shape of the population"
        if isinstance(array, np.ndarray):
            try:
                new_array = array.reshape(self.shape)
            except:
                self._logger.exception(
                    "The provided array of shape {} does not match the shape {} of the population."
                    .format(str(array.shape), str(self.shape)))
                sys.exit(1)
            return new_array
        elif isinstance(array, list):
            try:
                new_array = np.array(array).reshape(self.shape)
            except:
                self._logger.exception(
                    "The provided list of shape {} does not match the shape {} of the population."
                    .format(len(array), str(self.shape)))
                sys.exit(1)
            return new_array
        else: # shared variable
            return array

    def _flatten(self, attribute:str) -> np.ndarray:
        "Transforms an attribute array into a 1D list. Does nothing for shared variables."
        value = self._attributes[attribute].get_value()
        if isinstance(value, np.ndarray):
            return value.flatten()
        elif isinstance(value, (float, int, bool)):
            return value
        return value

    def _to_numpy(self, name, value):
        "Processes a new value of an attribute to make sure it is shared or 1D."
        # 
        if name in self._parser.shared:
            if not isinstance(value, (float, int, bool)):
                self._logger.error("Shared attributes expect a single value.")
                sys.exit(1)

            return value

        if isinstance(value, np.ndarray):
            if not value.shape == self.shape and not value.size == self.size:
                self._logger.error("Shapes do not match.")
                sys.exit(1)
            return value.flatten()

        elif isinstance(value, list):
            value = np.array(value)
            if not value.shape == self.shape and not value.size == self.size:
                self._logger.error("Shapes do not match.")
                sys.exit(1)
            return value.flatten()
            
        elif isinstance(value, (float, int, bool)):
            return np.full(self.size, value)

            

    def __str__(self):
        s = str("Population at " + hex(id(self))) + "\n"
        s += "    Name: " + self.name + "\n"
        s += "    Size: " + str(self.size) + " ; Shape: " + str(self.shape) + "\n"
        s += "    Neuron type: " + self._parser.name + "\n"
        s += textwrap.indent(str(self._parser), '    ') + "\n"

        return s