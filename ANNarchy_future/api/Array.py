import numpy as np

class Value(object):
    "Placeholder for single parameters"
    def __init__(self, value, dtype):
        self._init_value = value
        self._instantiated = False
        self._dtype = dtype

    def _copy(self):
        return Value(self._init_value, self._dtype)

    def _instantiate(self, shape):
        self._instantiated = True
        self.shape = 1
        self._value = self._init_value
    
    def get_value(self):
        if not self._instantiated:
            return self._init_value
        return self._value
    
    def set_value(self, val):
        if not self._instantiated:
            self._init_value = val
        else:
            self._value = val

class Array(object):
    "Placeholder for arrays"
    def __init__(self, init, dtype):

        self._init_value = init
        self._dtype = dtype

        self._instantiated = False

    def _copy(self):
        return Array(
            self._init_value, 
            self._dtype
        )

    def _instantiate(self, shape):
        self._instantiated = True
        self._value = np.full(shape, self._init_value, dtype=self._dtype)
        self.shape = self._value.shape
    
    def get_value(self):
        if not self._instantiated:
            return self._init_value
        return self._value
    
    def set_value(self, val):
        if not self._instantiated:
            self._init_value = val
        else:
            if isinstance(val, np.ndarray):
                if val.shape == self.shape:
                    self._value = val
                elif val.shape == (1,):
                    self._value = np.full(self.shape, val[0], dtype=self._dtype)
                else:
                    print("Array assignment error", val, val.shape)
            elif isinstance(val, (float, int, bool)):
                self._value = np.full(self.shape, val)
            else:
                print("Array assignment error", val)
