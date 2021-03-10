import numpy as np

from .Array import Value, Array
from ..parser.Equations import Equations


class Neuron(object):
    """ Abstract class defining single neurons.

    TODO

    """

    def Value(self, 
            value, 
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
            init=0.0, 
            dtype=np.float32):
        "Creates and returns an array."
        if not hasattr(self, "_data"):
            self._data = []
        val = Array(init, dtype)
        self._data.append(val)
        return val

    def Equations(self):
        "Returns an Equations context."
        eq = Equations(neuron=self)
        self._current_eq = eq
        return eq