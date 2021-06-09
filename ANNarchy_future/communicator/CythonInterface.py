import sys
import logging
import imp

import numpy as np

import ANNarchy_future.api as api
import ANNarchy_future.communicator as communicator

class CythonInterface(communicator.SimulationInterface):

    """Class managing communication with the kernel through a simple cython wrapper.

    """

    def __init__(self, net:'api.Network', library:str, library_path:str):
        
        """
        Args:
            net: Python network.
            library: name of the .so library (e.g. "ANNarchyCore").
            library_path: path to the .so library (e.g. "./annarchy/build/ANNarchyCore.so")
        """
        self.net = net
        self.library:str = library
        self.library_path:str = library_path

        # Logger
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Equations() created.")


    def instantiate(self):
        
        """Creates the C++ simulation core instance.
        """
        self.cython_module = imp.load_dynamic(
                self.library, # Name of the network
                self.library_path # Path to the library
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
        getattr(self._instance, "_add_"+ proj.synapse_class + 
            "_" + proj.pre.neuron_class + "_" + proj.post.neuron_class)(proj.pre._id_pop, proj.post._id_pop)
        

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

        """Single simulation step.

        Calls the Cython instance `step()` method.

        """

        self._instance.step()

    def simulate(self, duration:int):

        """Simulates for the specified duration in steps..

        Calls the Cython instance `simulate()` method.

        """

        self._instance.simulate(duration)

    def monitor(self, variables: dict):

        """Monitors the provided variables.

        TODO

        """

        self._instance.monitor(variables)

    def get_monitored(self):

        """Returns the monitored variables.

        TODO

        """

        return self._instance.get_monitored()