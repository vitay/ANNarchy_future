import sys
import logging

import numpy as np
import sympy as sp

from .Config import default_dict

class Equations(object):

    """Context to define equations. 

    It should be primarily used inside a `Neuron` or `Synapse` class, 
    but can also be used in a standalone mode by providing a list of attributes:

    ```python
    with Equations(symbols=['tau', 'v', 'r']) as n:
        n.dv_dt = (n.cast(1.0) - n.v)/n.tau
        n.r = sp.tanh(n.v)

    print(n)
    ```

    """

    def __init__(self, 
        symbols : list = None, 
        neuron = None, 
        synapse=None):

        """Creates the Equations context.

        Args:
            symbols: list of attributes when in standalone mode.
            neuron: Neuron instance (passed by the population).
            synapse: Synapse instance (passed by the projection).

        """

        self.logger = logging.getLogger(__name__)
        self.logger.info("Equations() created.")

        self.neuron = neuron
        self.synapse = synapse

        self.symbols = {
            't': sp.Symbol("t"),
            'dt': sp.Symbol("dt"),
            'spike': sp.Symbol("spike"),
        }
        
        if self.neuron is None and self.synapse is None:
            self._custom_symbols = symbols
            self.logger.info("Custom symbols: " + str(symbols))
        
        self.equations = []
        self._started = False
    
    def __enter__(self):

        if self.neuron is not None:

            for attr in self.neuron.attributes:
                if attr in self.neuron._values_list:
                    # Symbol
                    symbol = sp.Symbol("%(pop_prefix_value)s"+attr+"%(pop_suffix_value)s")
                    self.symbols[attr] = symbol
                    setattr(self, attr, symbol)

                elif attr in self.neuron._arrays_list:
                    # Symbol
                    symbol = sp.Symbol("%(pop_prefix_array)s"+attr+"%(pop_suffix_array)s")
                    self.symbols[attr] = symbol
                    setattr(self, attr, symbol)

                    # Derivative if needed
                    symbol = sp.Symbol("__grad__" + attr)
                    self.symbols["d"+attr+"_dt"] = symbol
                    setattr(self, "d"+attr+"_dt", symbol)
                    
                else:
                    self.logger.error(attr + "is not a value or array of the neuron.")
                    sys.exit()

            self.logger.info("Neuron symbols: " + str(self.symbols))

        elif self.synapse is not None:

            for attr in self.synapse.attributes:
                if attr in self.synapse._values_list:
                    # Symbol
                    symbol = sp.Symbol("%(proj_prefix_value)s"+attr+"%(proj_suffix_value)s")
                    self.symbols[attr] = symbol
                    setattr(self, attr, symbol)

                elif attr in self.synapse._arrays_list:
                    # Symbol
                    symbol = sp.Symbol("%(proj_prefix_value)s"+attr+"%(proj_suffix_array)s")
                    self.symbols[attr] = symbol
                    setattr(self, attr, symbol)

                    # Derivative if needed
                    symbol = sp.Symbol("__grad__" + attr)
                    self.symbols["d"+attr+"_dt"] = symbol
                    setattr(self, "d"+attr+"_dt", symbol)
                    
                else:
                    self.logger.error(attr + "is not a value or array of the synapse.")
                    sys.exit()

            self.logger.info("Synapse symbols: " + str(self.symbols))

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
        
        self.logger.info("Raw equations:")
        self.logger.info(str(self))
        self.logger.info("Simplified equations:")
        self.logger.info(str(self) % default_dict)

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

    def ite(self, cond, then, els):
        """If-then-else ternary condition.

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

    def cast(self, val:float) -> sp.Symbol:
        """Cast floating point numbers to symbols in order to avoid numerical errors.

        Args:
            val (float): 
        """

        return sp.Symbol(str(float(val)))
