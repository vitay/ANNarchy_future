import sys
import sympy as sp

import ANNarchy_future.parser as parser

def get_blocks(parser, equations:list) -> list:
    """Splits multiple Equations() calls into blocks of AssignmentBlocks and ODEBlocks.

    Args:
        parser (NeuronParser or SynapseParser): parser.
        equations: a list of Equations() contexts.

    Returns:
        A list of blocks.
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
                    _current_ODE_block = ODEBlock(parser, context.method)
                _current_ODE_block.add(name[1:-3], eq)

            # Assignment block
            else:
                if _current_ODE_block is not None:
                    blocks.append(_current_ODE_block)
                    _current_ODE_block = None
                if _current_assignment_block is None:
                    _current_assignment_block = AssignmentBlock(parser)
                _current_assignment_block.add(name, eq)

        # Append the last block
        if _current_assignment_block is not None:
            blocks.append(_current_assignment_block)
        if _current_ODE_block is not None:
            blocks.append(_current_ODE_block)

    return blocks

class Condition(object):
    """Parser for single conditions.

    Examples:
    - neuron.spike
    - synapse.transmit
    """

    def __init__(self, parser, name:str, equation):
        """
        Args:
            parser (NeuronParser or SynapseParser): parser.
            name (str): name of the condition.
            equation (sympy.Expression): condition.
        """

        self.parser = parser
        self.name = name
        self._equation = equation

    def parse(self):
        "Parses the boolean condition."

        hr = parser.ccode(self._equation)

        self.equation = {
            'name': self.name,
            'eq': self._equation,
            'human-readable': hr ,
        }

    def raw(self):
        "Raw representation of the equation."

        return self.equation['human-readable']

    def __str__(self):
        return self.equation['human-readable']


class Block(object):
    """Base class for blocks.
    """

    def __init__(self, parser):
        """
        Args:
            parser (NeuronParser or SynapseParser): parser.
        """

        self.parser = parser

        self._modified_variables = []
        self._dependencies = []
        self._equations = []

        # Processed equations accessible from outside
        self.equations = []

    def add(self, name, eq):
        """Adds a single equation to the block.
        """

        self._equations.append((name, eq))

        self._modified_variables.append(name)

    def dependencies(self):
        """
        Sets all dependencies in the block in `self._dependencies`:
        """

        for _, eq in self._equations:

            try: 
                symbols = list(eq.free_symbols)
            except: # e.g. v = 0 would return an int, so free_symbols is not set
                continue

            for symbol in symbols:

                if symbol in self.parser.attributes:

                    self._dependencies.append(symbol)

        self._dependencies = list(set(self._dependencies))

    def raw(self):
        "Raw representation of the equations."

        code = ""
        
        for name, eq in self._equations:
            code += name + " = " + " ".join(sp.ccode(eq).replace('\n', ' ').split()) + "\n"

        return code

    def __str__(self):

        code = ""
        
        for eq in self.equations:
            code += eq['human-readable'] + "\n"
        
        return code

class AssignmentBlock(Block):
    """Block of assignments.
    """

    def parse(self):
        """Parses the block of assignments.
        """

        for name, eq in self._equations:
            
            hr = name + " = " + parser.ccode(eq)

            self.equations.append(
                {
                    'type': 'assignment',
                    'name': name,
                    'op': "=",
                    'rhs': eq,
                    'human-readable': hr,
                }
            )


class ODEBlock(Block):
    """Block of ODEs.
    """

    def __init__(self, parser, method):
        """
        Args:
            parser (NeuronParser or SynapseParser): parser.
            method (str): numerical method.
        """

        self.method = method

        super(ODEBlock, self).__init__(parser)

    def parse(self):
        """Parses the block of ODEs by calling the numerical method.
        """

        if self.method == 'euler':

            self.equations = parser.NM.euler(self._equations)

        elif self.method == 'exponential':

            self.equations = parser.NM.exponential(self._equations)

        elif self.method == 'midpoint':

            self.equations = parser.NM.midpoint(self._equations)

        elif self.method == 'rk4':

            self.equations = parser.NM.rk4(self._equations)

        else:
            self.parser.logger.error(self.method + " is not implemented yet.")
            sys.exit(1)


