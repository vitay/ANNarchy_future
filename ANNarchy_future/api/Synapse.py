import numpy as np

from .Array import Parameter, Variable

class Synapse(object):

    def Parameter(self, value, shared=True, dtype=np.float32):
        "Creates and returns a single value."
        if not hasattr(self, "_data"):
            self._data = []
        val = Parameter(value, shared=shared, dtype=dtype)
        self._data.append(val)
        return val

    def Variable(self, init=0.0, shared=True, dtype=np.float32):
        "Creates and returns an array."
        if not hasattr(self, "_data"):
            self._data = []
        val = Variable(init, shared=shared, dtype=dtype)
        self._data.append(val)
        return val