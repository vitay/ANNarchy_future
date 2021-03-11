import sys, logging
import numpy as np
import sympy as sp

from .Config import default_dict
from ..api.Array import Value, Array
from..api.Neuron import Neuron

class NeuronParser(object):
    """Neuron parser.

    Attributes:
        neuron (Neuron): Neuron class
        name (str): name of the Neuron class
        attributes (list): list of attributes (values and arrays)
        values (list): list of values
        arrays (list): list of arrays
        update_equations (list): update equations.
        spike_condition (list): spike condition.
        reset_equations (list): reset equations.
    """

    def __init__(self, neuron:Neuron):

        """Initializes the parser.

        Sets:

        * `self.neuron`
        * `self.name`
        """

        self.neuron = neuron
        self._spiking = False
        self.name = self.neuron.__class__.__name__

        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Neuron parser created.")

        # Attributes
        self.attributes = []
        self.values = []
        self.arrays = []

        # Equations to retrieve
        self.update_equations = None
        self.spike_condition = None
        self.reset_equations = None

    def is_spiking(self):
        "Returns True if the Neuron class is spiking."
        return self._spiking

    def extract_variables(self):

        """Iterates over `neuron.__dict__` and extracts all `Value()` and `Array()` instances.

        Sets:

        * `self._spiking`
        * `self.attributes`
        * `self.values`
        * `self.arrays`

        """

        # List attributes
        current_attributes = list(self.neuron.__dict__.keys())

        for attr in current_attributes:
            if isinstance(getattr(self.neuron, attr), (Value, )):
                self.values.append(attr)
                self.attributes.append(attr)
            if isinstance(getattr(self.neuron, attr), (Array, )):
                self.arrays.append(attr)
                self.attributes.append(attr)

        # Get lists of values and arrays
        self.logger.info("Attributes: " + str(self.attributes))
        self.logger.info("Values: " + str(self.values))
        self.logger.info("Arrays: " + str(self.arrays))

        # Set the attributes to the neuron
        self.neuron.attributes = self.attributes
        self.neuron._values_list = self.values
        self.neuron._arrays_list = self.arrays

    def analyse_equations(self):

        """Analyses the neuron equations.

        Calls update(), spike() and reset() to retrieve the `Equations` objects.

        Sets:

        * `self.update_equations`
        * `self.spike_condition`
        * `self.reset_equations`

        """

        # List of methods
        callables = [f for f in dir(self.neuron) if callable(getattr(self.neuron, f))]

        if not 'update' in callables:
            self.logger.error("The Neuron class must implement update(self)")
            sys.exit(1)

        # Analyse update()
        self.logger.info("Calling Neuron.update().")
        try:
            self.neuron.update()
        except Exception:
            self.logger.exception("Unable to analyse update()")
            sys.exit(1)

        self.update_equations =  self.neuron._current_eq

        # For spiking neurons only
        if 'spike' in callables:

            self.logger.info("Neuron has a spike() method.")
            self._spiking = True

            self.logger.info("Calling Neuron.spike().")
            
            # Analyse spike()
            try:
                self.neuron.spike()
            except Exception:
                self.logger.exception("Unable to analyse spike()")
                sys.exit(1)
            self.spike_condition = self.neuron._current_eq
            
            # Analyse reset()
            self.logger.info("Calling Neuron.reset().")
            try:
                self.neuron.reset()
            except Exception:
                self.logger.exception("Unable to analyse reset()")
                sys.exit(1)
            self.reset_equations = self.neuron._current_eq

    def __str__(self):

        code = "Neuron " + self.name + "\n"
        code += "*"*60 + "\n"

        code += "Values: " + str(self.values) + "\n"
        code += "Arrays: " + str(self.arrays) + "\n\n"

        code += "Neural equations:\n"
        for var, eq in self.update_equations.equations:
            code += var + " = "
            code += sp.ccode(eq).replace("\n", " ") % default_dict + "\n"

        if self._spiking:
            code += "\nSpike condition:\n"
            code += sp.ccode(self.spike_condition.equations[0][1])% default_dict + "\n"

            code += "\nReset equations:\n"
            for var, eq in self.reset_equations.equations:
                code += var + " = "
                code += sp.ccode(eq).replace("\n", " ") % default_dict + "\n"

        return code
