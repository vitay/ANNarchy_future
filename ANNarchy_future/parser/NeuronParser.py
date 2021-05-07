import sys
import logging
import inspect

import numpy as np
import sympy as sp

import ANNarchy_future.api as api
import ANNarchy_future.parser as parser


class NeuronParser(object):
    """Neuron parser.

    Attributes:
        neuron (api.Neuron): Neuron class.
        name (str): name of the Neuron class.
        attributes (list): list of attributes (parameters and variables).
        parameters (list): list of parameters.
        variables (list): list of variables.
        inputs (list): list of input variables (conductances).
        outputs (list): list of output variables (firing rate).
        update_equations (list): update equations.
        spike_condition (Condition): spike condition.
        reset_equations (list): reset equations.
    """

    def __init__(self, neuron:'api.Neuron'):

        """Initializes the parser.

        Sets:

        * `self.neuron`
        * `self.name`
        """

        self.neuron = neuron
        self._spiking = False
        self.name = self.neuron.__class__.__name__

        # Logging
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Neuron parser created.")

        # Attributes
        self.attributes = []
        self.parameters = []
        self.variables = []
        self.shared = []
        self.inputs = []
        self.outputs = []

        # Equations to retrieve
        self.update_equations = []
        self.update_dependencies = []
        self.spike_condition = []
        self.spike_dependencies = []
        self.reset_equations = []
        self.reset_dependencies = []

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
        * `self.shared`
        * `self.inputs`
        * `self.outputs`

        """

        # List attributes
        current_attributes = list(self.neuron.__dict__.keys())

        for attr in current_attributes:
            var = getattr(self.neuron, attr)
            # Parameter
            if isinstance(var, (api.Parameter, )):
                self.parameters.append(attr)
                self.attributes.append(attr)
            # Variable
            if isinstance(var, (api.Variable, )):
                self.variables.append(attr)
                self.attributes.append(attr)
                if var in self.neuron._inputs:
                    self.inputs.append(attr)
                if var in self.neuron._outputs:
                    self.outputs.append(attr)

        # Shared variables
        for attr in self.attributes:
            if getattr(self.neuron, attr)._shared:
                self.shared.append(attr)

        # Get lists of parameters and variables
        self._logger.info("Attributes: " + str(self.attributes))
        self._logger.info("Parameters: " + str(self.parameters))
        self._logger.info("Variables: " + str(self.variables))

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

        # Analyse update()
        if 'update' in callables:

            self._logger.info("Calling Neuron.update().")

            signature = inspect.signature(self.neuron.update)
            if 'method' in signature.parameters.keys():
                method = signature.parameters['method'].default
                if not method in parser.Config.numerical_methods:
                    self._logger.error(self.name+".update(): "+ method + " is not available.")
                    sys.exit(1)
            else:
                method = 'euler'
            try:
                with self.neuron.Equations(method=method) as n:
                    self.neuron.update(n)
            except Exception:
                self._logger.exception("Unable to analyse " + self.name + ".update()")
                sys.exit(1)

            self.update_equations, self.update_dependencies =  self.process_equations(self.neuron._current_eq)
            self.neuron._current_eq = []

        # For spiking neurons only
        if 'spike' in callables:

            self._logger.info("Neuron has a spike() method.")
            self._spiking = True

            self._logger.info("Calling Neuron.spike().")
            
            # Analyse spike()
            try:
                with self.neuron.Equations() as n:
                    self.neuron.spike(n)
            except Exception:
                self._logger.exception("Unable to analyse spike().")
                sys.exit(1)

            self.spike_condition, self.spike_dependencies = self.process_condition(self.neuron._current_eq)
            self.neuron._current_eq = []
            
            # Analyse reset()
            self._logger.info("Calling Neuron.reset().")
            try:
                with self.neuron.Equations() as n:
                    self.neuron.reset(n)
            except Exception:
                self._logger.exception("Unable to analyse reset().")
                sys.exit(1)

            self.reset_equations, self.reset_dependencies = self.process_equations(self.neuron._current_eq)
            self.neuron._current_eq = []

        # Collect random variables
        self.random_variables = self.neuron.random_variables

    def process_condition(self, equations) -> 'parser.Condition':

        if len(equations) > 1:
            self._logger.error("Neuron.spike() must define only one Equations context.")
            raise SyntaxError()

        name, eq = equations[0].equations[0]

        condition = parser.Condition(self.neuron, name, eq)
        condition.parse()

        return condition, condition._dependencies

    def process_equations(self, equations) -> list:
        
        """Checks all declared equations and applies a numerical method if necessary.
        
        Args:
            equations: list of Equations objects.

        Returns:
            a list of blocks, which are lists of equations of three types: assignments, ODEs and conditions.
        
        """
        dependencies = []
        blocks = parser.get_blocks(self, equations)

        for block in blocks:
            block.dependencies()
            for dep in block._dependencies:
                dependencies.append(dep)
            block.parse()

        dependencies = list(set(dependencies))

        return blocks, dependencies

    def __str__(self):

        code = ""

        code += "Parameters: " + str(self.parameters) + "\n"
        code += "Variables: " + str(self.variables) + "\n\n"

        code += "Neural equations:\n"
        for block in self.update_equations:
            code += block.raw()

        if self._spiking:
            code += "\nSpike emission:\n"
            code += self.spike_condition.raw() + "\n"

            code += "\nReset equations:\n"
            for block in self.reset_equations:
                code += block.raw()

        return code
