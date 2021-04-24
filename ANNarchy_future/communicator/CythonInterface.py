import sys
import logging
import imp

import numpy as np

import ANNarchy_future.api as api
import ANNarchy_future.communicator as communicator

class CythonInterface(communicator.SimulationInterface):

    """Class managing communication with the kernel through a simple cython wrapper.

    """

    def __init__(self, net:'api.Network', library:str):
        
        """
        Args:
            net: Python network.
            library: path to the .so library.
        """
        self.net = net
        self.library:str = library

        # Logger
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Equations() created.")


    def instantiate(self):
        
        """Creates the C++ simulation core instance.
        """
        self.cython_module = imp.load_dynamic(
                self.library, # Name of the network
                self.net._annarchy_dir + self.library+".so" # Path to the library
        )
        self._instance = self.cython_module.pyNetwork(self.net.dt, self.net.seed)

    def add_population(self, pop:'api.Population'):
        """Instantiates a C++ Population.

        """
        # Create population
        getattr(self._instance, "_add_"+ pop.neuron_class)(pop.size)
        

    def add_projection(self, proj:'api.Projection'):
        """Instantiates a C++ Projection.

        """
        # Create projection
        getattr(self._instance, "_add_"+ proj.synapse_class)()
        

    def population_get(self, id_pop:int, attribute:str) -> np.ndarray:

        """Returns the value of the `attribute` for the population of ID `id_pop`.

        Args:

            id_pop: ID of the population.
            attribute: unique name of the attribute.
        """

        return getattr(self._instance.population(id_pop), attribute)

    def population_set(self, id_pop:int, attribute:str, value:np.ndarray):

        """Sets the value of the `attribute` to `value` for the population `id_pop`.
        
        Args:

            id_pop: ID of the population.
            attribute: unique name of the attribute.
            value: value to be set to the attribute.
        """

        setattr(self._instance.population(id_pop), attribute, value)

    def step(self):

        """Single step.

        """

        self._instance.step()