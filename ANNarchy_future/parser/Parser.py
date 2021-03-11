import sys
import sympy as sp

from .Config import default_dict

def ccode(eq):
    eq = sp.ccode(eq)
    return " ".join(eq.replace('\n', ' ').split())


class Condition(object):

    def __init__(self, parser, name, equation):

        self.parser = parser
        self.name = name
        self._equation = equation



    def parse(self):

        code = ccode(self._equation)

        self.equation = {
            'name': self.name,
            'sympy_eq': self._equation,
            'equation': code,
            'human-readable': code % default_dict,
        }

    def __str__(self):
        return self.equation['human-readable']

class AssignmentBlock(object):

    def __init__(self, parser):

        self.parser = parser
        self._equations = []

    def add(self, name, eq):

        self._equations.append((name, eq))

    def parse(self):

        self.equations = []

        for name, eq in self._equations:

            if name in self.parser.values:
                lhs = "%(pop_prefix_value)s" + name + "%(pop_suffix_value)s"
            elif name in self.parser.arrays:
                lhs = "%(pop_prefix_array)s" + name + "%(pop_suffix_array)s"


            code = lhs + " = " + ccode(eq)

            self.equations.append(
                {
                    'name': name,
                    'sympy': eq,
                    'code': code,
                    'human-readable': code % default_dict,
                }
            )


    def __str__(self):
        code = ""
        for eq in self.equations:
            code += eq['human-readable'] + "\n"
        return code


class ODEBlock(object):

    def __init__(self, parser, method):

        self.parser = parser
        self.method = method

        self._equations = []

    def add(self, name, eq):

        self._equations.append((name, eq))

    def parse(self):

        self.pre = []
        self.code = []

        for name, eq in self._equations:

            if self.method == 'euler':

                pre = "__grad__" + name + " = " + ccode(eq)
                code = "%(pop_prefix_array)s" + name + "%(pop_suffix_array)s" + \
                    " += dt*" + "__grad__" + name 

                self.pre.append(pre)
                self.code.append(code)

            elif self.method == 'exponential':

                expanded = eq.expand(
                    modulus=None, power_base=False, power_exp=False,
                    mul=True, log=False, multinomial=False)

                var = sp.Symbol("%(pop_prefix_array)s" + name + "%(pop_suffix_array)s")

                collected_var = sp.collect(expanded, var, evaluate=False, exact=False)

                tau = -1/collected_var[var]

                steady = sp.simplify(tau * expanded)

                
                pre = "__grad__" + name + " = (1.0 - exp(-dt/" + ccode(tau) + "))*(" + ccode(steady) + ")" 
                code = "%(pop_prefix_array)s" + name + "%(pop_suffix_array)s" + \
                    " = " + "__grad__" + name 
                    

                self.pre.append(pre)
                self.code.append(code)

            else:
                self.parser.logger.error(self.method + " is not implemented yet.")
                sys.exit(1)

    def __str__(self):
        code = ""
        for eq in self.pre:
            code += eq % default_dict + "\n"
        for eq in self.code:
            code += eq % default_dict + "\n"
        return code


