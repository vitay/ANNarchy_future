import sys
import logging

import numpy as np
import sympy as sp

from .EquationParser import Condition, AssignmentBlock, ODEBlock
from ..api.Array import Parameter, Variable
from ..api.Neuron import Neuron
from ..api.Synapse import Synapse

class SynapseParser(object):
    """Synapse parser.

    Attributes:
        synapse (Synapse): Synapse class.
        pre(Neuron): pre-synaptic Neuron class.
        post(Neuron); post.synaptic Neuron class.
        name (str): name of the Neuron class
        attributes (list): list of attributes (parameters and variables)
        parameters (list): list of parameters
        variables (list): list of variables

        TODO:
        update_equations (list): update equations.
        spike_condition (Condition): spike condition.
        reset_equations (list): reset equations.
    """

    def __init__(self, 
        synapse:Synapse,
        pre:Neuron,
        post:Neuron):

        """Initializes the parser.

        Sets:

        * `self.synapse`
        * `self.name`
        """

        self.synapse = synapse
        self.pre = pre
        self.post = post
        self._spiking = False
        self.name = self.synapse.__class__.__name__

        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Synapse parser created.")

        # Attributes
        self.attributes = []
        self.parameters = []
        self.variables = []
        self.shared = []

        # Equations to retrieve
        self.update_equations = []

    def is_spiking(self) -> bool:
        "Returns True if the Neuron class is spiking."
        return self._spiking

    def extract_variables(self):

        """Iterates over `synapse.__dict__` and extracts all `Parameter()` and `Variable()` instances.

        Sets:

        * `self._spiking`
        * `self.attributes`
        * `self.parameters`
        * `self.variables`
        * `self.shared`

        """

        # List attributes
        current_attributes = list(self.synapse.__dict__.keys())

        for attr in current_attributes:
            # Parameter
            if isinstance(getattr(self.synapse, attr), (Parameter, )):
                self.parameters.append(attr)
                self.attributes.append(attr)
            # Variable
            if isinstance(getattr(self.synapse, attr), (Variable, )):
                self.variables.append(attr)
                self.attributes.append(attr)

        # Shared variables
        for attr in self.attributes:
            if getattr(self.synapse, attr)._shared:
                self.shared.append(attr)

        # Get lists of parameters and variables
        self.logger.info("Attributes: " + str(self.attributes))
        self.logger.info("Parameters: " + str(self.parameters))
        self.logger.info("Variables: " + str(self.variables))

        # Set the attributes to the synapse
        self.synapse.attributes = self.attributes
        self.synapse.pre_attributes = self.pre.attributes
        self.synapse.post_attributes = self.post.attributes
        self.synapse._parser = self

    def analyse_equations(self):

        """Analyses the synapse equations.

        Calls update(), spike() and reset() to retrieve the `Equations` objects.

        Sets:

        * `self.update_equations`
        * `self.spike_condition`
        * `self.reset_equations`

        """

        # List of methods
        callables = [f for f in dir(self.synapse) if callable(getattr(self.synapse, f))]

        if 'update' in callables:
            self.logger.info("Calling Synapse.update().")
            try:
                self.synapse.update()
            except Exception:
                self.logger.exception("Error when parsing " + self.name + ".update().")
                sys.exit(1)
            else:
                self.update_equations =  self.process_equations(self.synapse._current_eq)
                self.synapse._current_eq = []

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

        code = "Synapse " + self.name + "\n"
        code += "*"*60 + "\n"

        code += "Parameters: " + str(self.parameters) + "\n"
        code += "Variables: " + str(self.variables) + "\n\n"

        code += "Synaptic equations:\n"
        for block in self.update_equations:
            code += str(block)

        return code
