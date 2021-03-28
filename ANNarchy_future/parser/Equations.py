import sys
import logging

import numpy as np
import sympy as sp

import ANNarchy_future.parser as parser

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

        # Objects
        self._neuron = neuron
        self._synapse = synapse

        # Numerical method
        self.method = method

        # Built-in symbols
        self.symbols = parser.symbols_dict.copy()
        
        # Standalone mode
        if self._neuron is None and self._synapse is None:
            self._custom_symbols = symbols
            self._logger.info("Custom symbols: " + str(symbols))
        
        # List of tuples (name, Equation)
        self.equations = []

        # Start recording assignments
        self._started = False
    
    ###########################################################################
    # Context management
    ###########################################################################

    def __enter__(self):

        if self._neuron is not None:

            for attr in self._neuron.attributes:
                # Symbol
                symbol = sp.Symbol(attr)
                self.symbols[attr] = symbol
                setattr(self, attr, symbol)

                if attr in self._neuron._parser.variables:
                    # Add derivative
                    symbol = sp.Symbol("d" + attr + "/dt")
                    self.symbols['d'+attr+'_dt'] = symbol
                    setattr(self, 'd'+attr+'_dt', symbol)

            self._logger.debug("Neuron symbols: " + str(self.symbols))

        elif self._synapse is not None:

            for attr in self._synapse.attributes:
                # Symbol
                symbol = sp.Symbol(attr)
                self.symbols[attr] = symbol
                setattr(self, attr, symbol)

                if attr in self._synapse._parser.variables:
                    # Add derivative
                    symbol = sp.Symbol("d" + attr + "/dt")
                    self.symbols['d'+attr+'_dt'] = symbol
                    setattr(self, 'd'+attr+'_dt', symbol)
            
            self.pre = PreNeuron()
            self.post = PostNeuron()

            for attr in self._synapse.pre_attributes:
                # Symbol
                symbol = sp.Symbol("pre."+attr)
                self.symbols["pre."+attr] = symbol
                setattr(self.pre, attr, symbol)

            for attr in self._synapse.post_attributes:
                # Symbol
                symbol = sp.Symbol("post."+attr)
                self.symbols["post."+attr] = symbol
                setattr(self.post, attr, symbol)

            self._logger.debug("Synapse symbols: " + str(self.symbols))

        else: # Custom set of variables
            for attr in self._custom_symbols:
                # Symbol
                symbol = sp.Symbol(attr)
                self.symbols[attr] = symbol
                setattr(self, attr, symbol)

                # Derivative if needed
                symbol = sp.Symbol("d" + attr + "/dt")
                self.symbols["d"+attr+"_dt"] = symbol
                setattr(self, "d"+attr+"_dt", symbol)

        self._started = True

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        
        self._logger.info(str(self))

    def __str__(self):
        string = ""
        for var, eq in self.equations:
            string += sp.ccode(self.symbols[var]) + " = " + sp.ccode(eq) + "\n"
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
