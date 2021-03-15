import sys
import sympy as sp

from .Config import ccode
import ANNarchy_future.parser.NumericalMethods as NM

class Condition(object):

    def __init__(self, parser, name, equation):

        self.parser = parser
        self.name = name
        self._equation = equation

    def parse(self):

        code = ccode(self._equation)

        self.equation = {
            'name': self.name,
            'eq': self._equation,
            'human-readable': code ,
        }

    def __str__(self):
        return self.equation['human-readable']


class Block(object):

    def __init__(self, parser):

        self.parser = parser

        self._modified_variables = []
        self._dependencies = []
        self._equations = []

        # Processed equations accessible from outside
        self.equations = []

    def add(self, name, eq):

        self._equations.append((name, eq))

        self._modified_variables.append(name)

    def dependencies(self):

        for _, eq in self._equations:

            try: 
                symbols = list(eq.free_symbols)
            except: # e.g. v = 0 would return an int, so free_symbols is not set
                continue

            for symbol in symbols:

                if symbol in self.parser.attributes:

                    self._dependencies.append(symbol)

        self._dependencies = list(set(self._dependencies))

    def __str__(self):

        code = ""
        
        for eq in self.equations:
            code += eq['human-readable'] + "\n"
        
        return code

class AssignmentBlock(Block):

    def parse(self):

        for name, eq in self._equations:
            
            hr = name + " = " + ccode(eq)

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

    def __init__(self, parser, method):

        self.method = method

        super(ODEBlock, self).__init__(parser)

    def parse(self):

        if self.method == 'euler':

            self.equations = NM.euler(self._equations)

        elif self.method == 'exponential':

            self.equations = NM.exponential(self._equations)

        elif self.method == 'midpoint':

            self.equations = NM.midpoint(self._equations)

        elif self.method == 'rk4':

            self.equations = NM.rk4(self._equations)

        else:
            self.parser.logger.error(self.method + " is not implemented yet.")
            sys.exit(1)


