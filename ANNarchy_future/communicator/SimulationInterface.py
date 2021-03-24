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

    def get(self, name:str, attribute:str) -> np.ndarray:

        """Returns the value of the `attribute` for the object 
        (Population or Projection) specified by `name`.

        Args:

            name: unique name of the object.
            attribute: unique name of the attribute.
        """

        raise NotImplementedError

    def set(self, name:str, attribute:str, value:np.ndarray):

        """Sets the value of the `attribute` to `value` for the object 
        (Population or Projection) specified by `name`.
        
        Args:

            name: unique name of the object.
            attribute: unique name of the attribute.
            value: value to be set o the attribute.
        """

        raise NotImplementedError

