import numpy as np

from .Array import Value, Array

class Synapse(object):

    def Value(self, value, dtype=np.float32):
        "Creates and returns a single value."
        if not hasattr(self, "_data"):
            self._data = []
        val = Value(value, dtype)
        self._data.append(val)
        return val

    def Array(self, init=0.0, dtype=np.float32):
        "Creates and returns an array."
        if not hasattr(self, "_data"):
            self._data = []
        val = Array(init, dtype)
        self._data.append(val)
        return val