import sys
import logging

import numpy as np
import sympy as sp


from .Parser import ccode, Condition, AssignmentBlock, ODEBlock
from ..api.Array import Parameter, Variable
from ..api.Neuron import Neuron

class NeuronParser(object):
    """Neuron parser.

    Attributes:
        neuron (Neuron): Neuron class
        name (str): name of the Neuron class
        attributes (list): list of attributes (parameters and variables)
        parameters (list): list of parameters
        variables (list): list of variables
        update_equations (list): update equations.
        spike_condition (Condition): spike condition.
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
        self.parameters = []
        self.variables = []

        # Equations to retrieve
        self.update_equations = None
        self.spike_condition = None
        self.reset_equations = None

    def is_spiking(self) -> bool:
        "Returns True if the Neuron class is spiking."
        return self._spiking

    def extract_variables(self):

        """Iterates over `neuron.__dict__` and extracts all `Parameter()` and `Variable()` instances.

        Sets:

        * `self._spiking`
        * `self.attributes`
        * `self.parameters`
        * `self.variables`

        """

        # List attributes
        current_attributes = list(self.neuron.__dict__.keys())

        for attr in current_attributes:
            if isinstance(getattr(self.neuron, attr), (Parameter, )):
                self.parameters.append(attr)
                self.attributes.append(attr)
            if isinstance(getattr(self.neuron, attr), (Variable, )):
                self.variables.append(attr)
                self.attributes.append(attr)

        # Get lists of parameters and variables
        self.logger.info("Attributes: " + str(self.attributes))
        self.logger.info("Parameters: " + str(self.parameters))
        self.logger.info("Variables: " + str(self.variables))

        # Set the attributes to the neuron
        self.neuron.attributes = self.attributes
        self.neuron._parser = self

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

        self.update_equations =  self.process_equations(self.neuron._current_eq)
        self.neuron._current_eq = []

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

            self.spike_condition = self.process_condition(self.neuron._current_eq)
            self.neuron._current_eq = []
            
            # Analyse reset()
            self.logger.info("Calling Neuron.reset().")
            try:
                self.neuron.reset()
            except Exception:
                self.logger.exception("Unable to analyse reset()")
                sys.exit(1)

            self.reset_equations = self.process_equations(self.neuron._current_eq)
            self.neuron._current_eq = []

    def process_condition(self, equations) -> Condition:

        if len(equations) > 1:
            self.logger.error("Neuron.spike() must define only one Equations context.")
            raise SyntaxError()

        name, eq = equations[0].equations[0]

        condition = Condition(self.neuron, name, eq)
        condition.parse()

        return condition

    def process_equations(self, equations) -> list:
        
        """Checks all declared equations and applies a numerical method if necessary.
        
        Args:
            equations: list of Equations objects.

        Returns:
            a list of blocks, which are lists of equations of three types: assignments, ODEs and conditions.
        
        """
        blocks = []

        # Iterate over the equations to group them into blocks
        for context in equations:

            _current_assignment_block = None
            _current_ODE_block = None
            
            for name, eq in context.equations:
                
                # ODE block
                if name.startswith("d") and name.endswith('_dt'):
                    if _current_assignment_block is not None:
                        blocks.append(_current_assignment_block)
                        _current_assignment_block = None
                    if _current_ODE_block is None:
                        _current_ODE_block = ODEBlock(self, context.method)
                    _current_ODE_block.add(name[1:-3], eq)

                # Assignment block
                else:
                    if _current_ODE_block is not None:
                        blocks.append(_current_ODE_block)
                        _current_ODE_block = None
                    if _current_assignment_block is None:
                        _current_assignment_block = AssignmentBlock(self)
                    _current_assignment_block.add(name, eq)

            # Append the last block
            if _current_assignment_block is not None:
                blocks.append(_current_assignment_block)
            if _current_ODE_block is not None:
                blocks.append(_current_ODE_block)

        for block in blocks:
            block.dependencies()
            block.parse()

        return blocks

    def __str__(self):

        code = "Neuron " + self.name + "\n"
        code += "*"*60 + "\n"

        code += "Parameters: " + str(self.parameters) + "\n"
        code += "Variables: " + str(self.variables) + "\n\n"

        code += "Neural equations:\n"
        for block in self.update_equations:
            code += str(block)

        if self._spiking:
            code += "\nSpike condition:\n"
            code += str(self.spike_condition) + "\n"

            code += "\nReset equations:\n"
            for block in self.reset_equations:
                code += str(block)

        return code
