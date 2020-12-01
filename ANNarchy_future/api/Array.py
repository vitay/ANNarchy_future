import numpy as np

class Value:
    """
    Single numerical value.
    """

    def __init__(self, value=0.0, dtype=np.float32):

        self.value = value
        self.dtype = dtype


    def _instantiate(self, shape):
        "Creates numpy arrays of the correct size."
        self.value = np.full((1,), self.value, dtype=self.dtype)

    def __repr__(self):
        return str(self.value)

class Array:
    """
    Array of numerical values.
    """

    def __init__(self, value=0.0, eq="", method=None, min=None, max=None, dtype=np.float32, during_refractory=False):

        self._network = None

        self.value = value
        self.eq = eq
        self.method = method
        self.min = min
        self.max = max
        self.dtype = dtype
        self.during_refractory = during_refractory

    def _instantiate(self, shape):
        "Creates numpy arrays of the correct size."
        self.value = np.full(shape, self.value, dtype=self.dtype)

    def __repr__(self):
        return str(self.value)