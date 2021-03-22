import sys
import logging

from .SimulationInterface import SimulationInterface

class CythonInterface(SimulationInterface):

    """Class managing communication with the kernel through a simple cython wrapper.

    """

    def __init__(self, library:str):
        
        """
        Args:

            library: path to the .so library.
        """

        self.library:str = library

        # Logger
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Equations() created.")


    def instantiate(self):
        
        """Creates the C++ simulation core instance.
        """

        raise NotImplementedError

    def get(self, name:str, attribute:str) ->np.ndarray:

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