import sys
import logging

import numpy as np
import sympy as sp

import ANNarchy_future.api as api
import ANNarchy_future.parser as parser

class Symbol(sp.core.Symbol):
    """Subclass of sp.core.Symbol allowing to store additional attributes.

    """
    def __new__(self, name, method='euler'):

        obj = sp.core.Symbol.__new__(self, name)
        self.method = method
        
        return obj


class PreNeuron(object):
    """
    Placeholder for presynaptic attributes.
    """
    pass

class PostNeuron(object):
    """
    Placeholder for postsynaptic attributes.
    """
    pass

class StandaloneObject(object):
    """
    Mimicks a Neuron or Synapse in standalone mode.
    """
    def __init__(self, attributes):
        self.attributes = attributes

class Equations(object):

    """Context to define equations. 

    It should be primarily used inside a `Neuron` or `Synapse` class, 
    but can also be used in a standalone mode by providing a list of attributes:

    ```python
    with Equations(symbols=['tau', 'v', 'r']) as n:

        n.dv_dt = (n.cast(0.04) - n.v)/n.tau
        
        n.r = sp.tanh(n.v)

    print(n)
    ```

    """

    def __init__(self, 
        symbols : list = None,
        method : str ='euler',
        neuron = None, 
        synapse = None ):

        """Creates the Equations context.

        Args:
            symbols: list of attributes when in standalone mode.
            method: numerical method (euler, midpoint, exponential, rk4, event-driven)
            neuron: Neuron instance (passed by the population).
            synapse: Synapse instance (passed by the projection).

        """

        # Logger
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Equations() created.")

        
        # Standalone mode
        if neuron is None and synapse is None and symbols is not None:
            self.object = StandaloneObject(symbols)
            self.object.random_variables = {}
            self._logger.info("Custom symbols: " + str(symbols))
        elif neuron is not None:
            self.object = neuron
            if not hasattr(neuron, 'random_variables'):
                self.object.random_variables = {}
        elif synapse is not None:
            self.object = synapse
            if not hasattr(synapse, 'random_variables'):
                self.object.random_variables = {}
        else:
            self._logger.error("Equations() requires one argument among `symbols`, `neuron` or `synapse`.")
            sys.exit(1)

        # Numerical method
        self.method = method

        # Built-in symbols
        self.symbols = parser.symbols_dict.copy()
        
        # List of tuples (name, Equation)
        self.equations = []

        # List of random variables
        self.random_variables = {}

        # Start recording assignments
        self._started = False
    
    ###########################################################################
    # Context management
    ###########################################################################

    def __enter__(self):

        if isinstance(self.object, api.Neuron):

            for attr in self.object.attributes:
                # Symbol
                symbol = sp.Symbol(attr)
                self.symbols[attr] = symbol
                setattr(self, attr, symbol)

                if attr in self.object._parser.variables:
                    # Add derivative
                    symbol = sp.Symbol("d" + attr + "/dt")
                    self.symbols['d'+attr+'_dt'] = symbol
                    setattr(self, 'd'+attr+'_dt', symbol)


            self._logger.debug("Neuron symbols: " + str(self.symbols))

        elif isinstance(self.object, api.Synapse):

            for attr in self.object.attributes:
                # Symbol
                symbol = sp.Symbol(attr)
                self.symbols[attr] = symbol
                setattr(self, attr, symbol)

                if attr in self.object._parser.variables:
                    # Add derivative
                    symbol = sp.Symbol("d" + attr + "/dt")
                    self.symbols['d'+attr+'_dt'] = symbol
                    setattr(self, 'd'+attr+'_dt', symbol)
            
            self.pre = PreNeuron()
            self.post = PostNeuron()

            for attr in self.object.pre_attributes:
                # Symbol
                symbol = sp.Symbol("pre."+attr)
                self.symbols["pre."+attr] = symbol
                setattr(self.pre, attr, symbol)

            for attr in self.object.post_attributes:
                # Symbol
                symbol = sp.Symbol("post."+attr)
                self.symbols["post."+attr] = symbol
                setattr(self.post, attr, symbol)

            self._logger.debug("Synapse symbols: " + str(self.symbols))

        else: # Custom set of variables
            for attr in self.object.attributes:
                # Symbol
                symbol = sp.Symbol(attr)
                self.symbols[attr] = symbol
                setattr(self, attr, symbol)

                # Derivative if needed
                symbol = sp.Symbol("d" + attr + "/dt")
                self.symbols['d'+attr+'_dt'] = symbol
                setattr(self, 'd'+attr+'_dt', symbol)

        self._started = True

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._logger.info(str(self))

    def __str__(self):
        string = ""
        for name, dist in self.random_variables.items():
            string += name + " = " + dist.human_readable() + "\n"
        for name, eq in self.equations:
            string += sp.ccode(self.symbols[name]) + " = " + sp.ccode(eq) + "\n"
        return string

    def __getattribute__(self, name):

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):

        # After __enter__(), track modifications to the variables
        if hasattr(self, '_started') and self._started:
            # Do not assign equations to symbols, just store them
            if name in self.symbols.keys():
                self.equations.append((name, value))
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    ###########################################################################
    # Built-in vocabulary
    ###########################################################################
    @property
    def t(self):
        "Current time in ms."
        return self.symbols['t']

    @property
    def dt(self):
        "Step size in ms."
        return self.symbols['dt']

    def ite(self, cond, then, els):
        """If-then-else ternary operator.

        Equivalent to:

        ```python
        def ite(cond, then, els):
            if cond:
                return then
            else:
                return els
        ```

        Args: 
            cond: condition.
            then: returned value when cond is true.
            else: returned value when cond is false.
        """

        return sp.Piecewise((then, cond), (els, True))


    def clip(self, val:sp.Symbol, min:sp.Symbol, max:sp.Symbol = None):
        """Sets the lower and upper bounds of a variable.

        Equivalent to:

        ```python
        def clip(val, min, max):
            if val < min:
                return min
            elif val > max:
                return max
            else:
                return val
        ```

        Args: 
            val: variable.
            min: lower bound.
            max: upper bound.
        
        """
        
        if min is None and max is None: # Do nothing
            return val
        elif min is not None and max is None: # Lower bound
            return sp.Piecewise((min, val<min), (val, True))
        elif min is None and max is not None: # Upper bound
            return sp.Piecewise((max, val>max), (val, True))
        else: # Two-sided clip
            return sp.Piecewise((min, val<min), (max, val>max), (val, True))

    def cast(self, val:float) -> sp.Symbol:
        """Cast floating point numbers to symbols in order to avoid numerical errors.

        Args:
            val (float): 
        """

        return sp.Symbol(str(float(val)))


    ###########################################################################
    # Random distributions
    ###########################################################################
    def Uniform(self, min:float, max:float):
        """
        Uniform distribution between `min` and `max`.

        Args:
            min: lower bound.
            max: upper bound.
        """
        name = "__rand__" + str(len(self.object.random_variables))

        obj = parser.RandomDistributions.Uniform(name, min, max)

        self.random_variables[name] = obj
        self.object.random_variables[name] = obj
        
        return sp.Symbol(name)

    def Normal(self, mu:float, sigma:float):
        """
        Normal distribution with mean `mu` and standard deviation `sigma`.

        Args:
            mu: mean.
            sigma: standard deviation.
        """
        name = "__rand__" + str(len(self.object.random_variables))

        obj = parser.RandomDistributions.Normal(name, mu, sigma)

        self.random_variables[name] = obj
        self.object.random_variables[name] = obj
        
        return sp.Symbol(name)