import sys, logging
import numpy as np
import sympy as sp

from .Config import default_dict

class PopulationParser(object):
    """
    Population parser.
    """

    def __init__(self, pop):

        self.pop = pop
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Population parser created.")

        # Equations to retrieve
        self._update_equations = None
        self._spiking_equation = None
        self._reset_equations = None

    def analyse(self):
        """
        Calls update(), spike() and reset() in order to obtain the equations.
        """
        self.logger.debug("Starting analyse()")

        # Analyse update()
        self.logger.info("Calling Neuron.update().")
        try:
            self.pop._neuron_type.update()
        except Exception:
            self.logger.exception("Unable to analyse update()")
            sys.exit()

        self._update_equations =  self.pop._neuron_type._current_eq

        # For spiking neurons only
        if 'spike' in [f for f in dir(self.pop._neuron_type) if callable(getattr(self.pop._neuron_type, f))]:

            self.logger.info("Neuron has a spike() method.")
            self.pop._spiking = True

            self.logger.info("Calling Neuron.spike().")
            
            # Analyse spike()
            try:
                self.pop._neuron_type.spike()
            except Exception as e:
                self.logger.exception("Unable to analyse spike()")
                sys.exit()
            self._spiking_equation = self.pop._neuron_type._current_eq
            
            # Analyse reset()
            self.logger.info("Calling Neuron.reset().")
            try:
                self.pop._neuron_type.reset()
            except Exception as e:
                self.logger.exception("Unable to analyse reset()")
                sys.exit()
            self._reset_equations = self.pop._neuron_type._current_eq

    def __str__(self):

        code = "Neural equations:\n"
        for var, eq in self._update_equations.equations:
            code += var + " = "
            code += sp.ccode(eq).replace("\n", " ") % default_dict + "\n"

        if self.pop._spiking:
            code += "\nSpike condition:\n"
            code += sp.ccode(self._spiking_equation.equations[0][1])% default_dict + "\n"

            code += "\nReset equations:\n"
            for var, eq in self._reset_equations.equations:
                code += var + " = "
                code += sp.ccode(eq).replace("\n", " ") % default_dict + "\n"

        return code
