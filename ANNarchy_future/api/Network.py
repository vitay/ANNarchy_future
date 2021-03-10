import sys
import logging

from .Population import Population
from .Neuron import Neuron

# Verbosity levels for logging
verbosity_levels = [
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG
]

class Network(object):
    """Network class containing the complete neural model.

    Attributes:
        dt: simulation time step in ms.

    """

    def __init__(self, 
                dt : float =1.0, 
                verbose : int =1, 
                logfile : str =None):
        """Constructor of the `Network` class.
        
        The discretization time contant `dt` is determined at the network-level and should stay constant during the whole simulation. 
        
        The `verbose` level specifies which logging messages will be shown:

        * 0 : only errors and exceptions are printed.
        * 1 : errors, exceptions and warnings are displayed (default).
        * 2 : additional information is also displayed (parsing, etc).
        * 3 : debug information is also displayed (which method is entered, variable values, etc...)

        When `logfile` is specified, the logging messages will be saved in that file instead of stdout.

        Args:
            dt: simulation step size in ms. 
            verbose: logging level. ERROR=0, WARNING=1, INFO=2, DEBUG=3
            logfile: file to save the logs. stdout if left empty.
        """
        self.dt = dt

        # Logging module: https://docs.python.org/3/howto/logging.html
        if logfile is not None:
            logging.basicConfig(filename=logfile, level=verbosity_levels[verbose])
        else:
            logging.basicConfig(level=verbosity_levels[verbose])
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating new network with dt="+str(self.dt))

        # List of populations
        self._populations = []

    def add(self, 
            shape: tuple, 
            neuron : Neuron, 
            name : str = None) -> Population:
        """Adds a population to the network.

        Args:
            shape: shape of the population as a single integer or tuple. 
            neuron: Neuron instance. 
            name: optional name. 

        Returns:
            A population instance.
        """
        if isinstance(shape, int):
            shape = (shape,)
        
        # Create the population
        self.logger.info("Adding Population(" + str(shape) + ", " + type(neuron).__name__ + ", " + str(name) + ").")
        pop = Population(shape, neuron, name)
        id_pop = len(self._populations)
        pop._register(self, id_pop)

        # Have the population analyse its attributes
        self.logger.debug("Analysing the population.")
        pop._analyse()

        # Store the population
        self._populations.append(pop)
        self.logger.info("Population created.")

        return pop
 
