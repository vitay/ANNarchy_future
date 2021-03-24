import numpy as np

import ANNarchy_future.api as api
from ..parser.Equations import Equations


class Neuron(object):
    """ Abstract class defining single neurons.

    TODO

    """

    def Parameter(self, 
        value:float, 
        shared:bool = True,
        dtype:str='float') -> api.Parameter:

        """Defines a parameter for the neuron.

        Parameters are defined only once for the whole population by default. 
        If each neuron should have different values, set `shared=False`. 

        Args:
            value: initial value.
            shared: locality of the parameter.
            dtype: numerical type of the value ('float', 'int', 'bool').

        Returns:
            `Parameter` instance.
        """

        if not hasattr(self, "_data"):
            self._data = []
            self._inputs = []
            self._outputs = []
            
        val = api.Parameter(init=value, shared=shared, dtype=dtype)
        self._data.append(val)

        return val

    def Variable(self, 
        init:float = 0.0,
        shared:bool = False, 
        input:bool = False, 
        output:bool = False,
        dtype:str='float') -> api.Variable:

        """Defines a variable for the neuron.

        Variables take a different value for each neuron in the population.
        If a single value is needed, set `shared=True` to save some memory.

        Variables receiving inputs from a projection (weighted sums, conductances) should set `input=True`.

        Output variables (e.g. firing rates) that may be used in projections with a delay should set `output=True`.

        Args:
            init: initial value.
            shared: locality of the variable.
            input: is it an input variable?
            output: is it an output variable?
            dtype: numerical type of the variable ('float', 'int', 'bool').

        Returns:
            `Variable` instance.
        """

        if not hasattr(self, "_data"):
            self._data = []
            self._inputs = []
            self._outputs = []

        val = api.Variable(init=init, shared=shared, dtype=dtype)
        
        self._data.append(val)
        
        if input:
            self._inputs.append(val)
        
        if output:
            self._outputs.append(val)

        return val

    def Equations(self, method:str = 'euler'):

        """Returns an Equations context.

        ```python
        with self.Equations() as n:

            n.dr_dt = (n.ge - n.r)/n.tau
        ```

        When opening the context as `n`, the variable has all attributes 
        (parameters and variables) of the neuron as symbols, which can be combined in Sympy equations.

        Args:
            method: numerical method (euler, midpoint, exponential, rk4, event-driven)
        
        """

        eq = Equations(neuron=self, method=method)
        
        if not hasattr(self, '_current_eq'):
            self._current_eq = []

        self._current_eq.append(eq)
        
        return eq