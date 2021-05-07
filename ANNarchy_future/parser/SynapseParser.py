import sys
import logging
import inspect

import numpy as np
import sympy as sp

import ANNarchy_future.api as api
import ANNarchy_future.parser as parser


class SynapseParser(object):
    """Synapse parser.

    Attributes:
        synapse (api.Synapse): Synapse class.
        pre (api.Neuron): pre-synaptic Neuron class.
        post (api.Neuron): post-synaptic Neuron class.
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
        synapse:'api.Synapse',
        pre:'api.Neuron',
        post:'api.Neuron'):

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
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Synapse parser created.")

        # Attributes
        self.attributes = []
        self.parameters = []
        self.variables = []
        self.shared = []

        # Equations to retrieve
        self.update_equations = []
        self.update_dependencies = []

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
            if isinstance(getattr(self.synapse, attr), (api.Parameter, )):
                self.parameters.append(attr)
                self.attributes.append(attr)
            # Variable
            if isinstance(getattr(self.synapse, attr), (api.Variable, )):
                self.variables.append(attr)
                self.attributes.append(attr)

        # Shared variables
        for attr in self.attributes:
            if getattr(self.synapse, attr)._shared:
                self.shared.append(attr)

        # Get lists of parameters and variables
        self._logger.info("Attributes: " + str(self.attributes))
        self._logger.info("Parameters: " + str(self.parameters))
        self._logger.info("Variables: " + str(self.variables))

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
            self._logger.info("Calling Synapse.update().")
            
            signature = inspect.signature(self.synapse.update)
            if 'method' in signature.parameters.keys():
                method = signature.parameters['method'].default
                if not method in parser.Config.numerical_methods:
                    self._logger.error(self.name+".update(): "+ method + " is not available.")
                    sys.exit(1)
            else:
                method = 'euler'

            try:
                with self.synapse.Equations(method=method) as s:
                    self.synapse.update(s)
            except Exception:
                self._logger.exception("Error when parsing " + self.name + ".update().")
                sys.exit(1)
            else:
                self.update_equations, self.update_dependencies =  self.process_equations(self.synapse._current_eq)
                self.synapse._current_eq = []

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

        code = "Synapse " + self.name + "\n"
        code += "*"*60 + "\n"

        code += "Parameters: " + str(self.parameters) + "\n"
        code += "Variables: " + str(self.variables) + "\n\n"

        code += "Synaptic equations:\n"
        for block in self.update_equations:
            code += str(block)

        return code
