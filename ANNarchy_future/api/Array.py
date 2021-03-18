import sys
import logging

import numpy as np

###########################################################################
# Basic Array object
###########################################################################
class Array(object):
    "Placeholder for neural data."

    def __init__(self, 
        init:float, 
        shared:bool, 
        dtype:str ):

        self._init_value = init
        self._shared = shared

        dtypes = {
            'float': np.float,
            'int': np.int,
            'bool': np.bool,
        }
        self._dtype_string = dtype
        self._dtype = dtypes[dtype]

        self.logger = logging.getLogger(__name__)

        self._instantiated = False

    def _instantiate(self, shape):
        self._instantiated = True
        if self._shared:
            self.shape = 1
            self._value = self._init_value
        else:
            self.shape = shape
            self._value = np.full(self.shape, self._init_value, dtype=self._dtype)

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
                    self.logger.error("Shapes do not match: " + str(self.shape) + " <- " + str(val.shape))
                    sys.exit(1)
            elif isinstance(val, (float, int, bool)):
                self._value = np.full(self.shape, val, dtype=self._dtype)
            else:
                print("Array assignment error", val)

###########################################################################
# Parameter object
###########################################################################
class Parameter(Array):
    "Placeholder for parameters"

    def __init__(self, 
        init:float, 
        shared:bool, 
        dtype:str ):

        super().__init__(init, shared, dtype)

    def _copy(self):
        return Parameter(
            init=self._init_value, 
            shared=self._shared, 
            dtype=self._dtype_string,
        )

###########################################################################
# Variable object
###########################################################################
class Variable(Array):
    "Placeholder for variables"

    def __init__(self, 
        init:float, 
        shared:bool, 
        dtype:str):

        super().__init__(init, shared, dtype)

    def _copy(self):
        return Variable(
            init=self._init_value,
            shared=self._shared, 
            dtype=self._dtype_string,
        )

    
