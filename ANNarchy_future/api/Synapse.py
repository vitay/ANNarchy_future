import numpy as np

from .Array import Parameter, Variable
from ..parser.Equations import Equations


class Synapse(object):
    """ Abstract class defining single synapses.

    TODO

    """

    def Parameter(self, 
        value:float, 
        shared:bool = True,
        dtype:str = 'float') -> Parameter:

        """Defines a parameter for the synapse.

        Parameters are defined only once for the whole projection by default. 
        If each neuron should have different values, set `shared=False`. 

        Args:
            value: initial value.
            shared: locality of the parameter
            dtype: numpy type of the value (e.g. np.int, np.float)

        Returns:
            `Parameter` instance.
        """

        if not hasattr(self, "_data"):
            self._data = []
        val = Parameter(init=value, shared=shared, dtype=dtype)
        self._data.append(val)

        return val

    def Variable(self, 
        init:float = 0.0,
        shared:bool = False, 
        dtype:str = 'float') -> Variable:

        """Defines a variable for the synapse.

        Variables take a different value for each synapse in the projection by default.
        If a single value for the whole projection is needed, set `shared=True` to save some memory.

        Args:
            value: initial value.
            shared: locality of the variable.
            dtype: numerical type of the value ('float', 'int', 'bool').

        Returns:
            `Variable` instance.
        """

        if not hasattr(self, "_data"):
            self._data = []
        val = Variable(init=init, shared=shared, dtype=dtype)
        self._data.append(val)

        return val

    def Equations(self, method:str = 'euler'):

        """Returns an Equations context.

        ```python
        with self.Equations() as s:

            s.w += s.eta * s.pre.r * s.post.r
        ```

        When opening the context as `s`, the variable has all attributes 
        (parameters and variables) of the synapse as symbols, which can be combined in Sympy equations.

        The attributes of the pre- and post-synaptic neurons are accessible under `s.pre` and `s.post`.

        Args:
            method: numerical method (euler, midpoint, exponential, rk4, event-driven)
        
        """

        eq = Equations(synapse=self, method=method)
        
        if not hasattr(self, '_current_eq'):
            self._current_eq = []

        self._current_eq.append(eq)
        
        return eq