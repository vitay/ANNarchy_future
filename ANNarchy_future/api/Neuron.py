import numpy as np

from .Array import Value, Array
from ..parser.Equations import Equations


class Neuron(object):
    """ Abstract class defining single neurons.

    TODO

    """

    def Value(self, 
        value:float, 
        dtype=np.float32) -> Value:

        """Defines a Value for the neuron.

        Values are defined only once for the whole population. 
        If each neuron should have different values, use an `Array` instead. 

        Args:
            value: initial value.
            dtype: numpy type of the value (e.g. np.int, np.float)

        Returns:
            `Value` instance.
        """

        if not hasattr(self, "_data"):
            self._data = []
        val = Value(value, dtype)
        self._data.append(val)

        return val

    def Array(self, 
        init:float = 0.0, 
        dtype=np.float32) -> Array:

        """Defines an Array for the neuron.

        Arrays can take a different value for each neuron in the population.
        If a single value is needed, use `Value` to save some memory.

        Args:
            value: initial value.
            dtype: numpy type of the value (e.g. np.int, np.float)

        Returns:
            `Value` instance.
        """

        if not hasattr(self, "_data"):
            self._data = []
        val = Array(init, dtype)
        self._data.append(val)

        return val

    def Equations(self, method:str = 'euler'):

        """Returns an Equations context.

        ```python
        with self.Equations() as n:

            n.dr_dt = (n.ge - n.r)/n.tau
        ```

        When opening the context as `n`, the variable has all attributes 
        (values and arrays) of the neuron as symbols, which can be combined in Sympy equations.

        Args:
            method: numerical method (euler, midpoint, exponential, rk4, event-driven)
        
        """

        eq = Equations(neuron=self, method=method)
        self._current_eq = eq
        return eq