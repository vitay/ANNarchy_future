import numpy as np

class SimulationInterface(object):

    """Simulation interface for the C++ kernel.

    Must be implemented by either:

    * `CythonInterface` for single, openmp and cuda.
    * `gRPCInterface` for mpi.

    """

    def instantiate(self):
        
        """Creates the C++ simulation core instance.
        """

        raise NotImplementedError


