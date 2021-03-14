import sys
import sympy as sp

from .Config import default_dict, empty_dict

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
            'sympy': self._equation,
            'equation': code,
            'human-readable': code % default_dict,
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

                    self._dependencies.append(ccode(symbol) % empty_dict)

        self._dependencies = list(set(self._dependencies))

    def __str__(self):

        code = ""
        
        for eq in self.equations:
            code += eq['human-readable'] + "\n"
        
        return code

class AssignmentBlock(Block):

    def parse(self):

        for name, eq in self._equations:

            lhs = self.parser.get_symbol(name)
            
            code = lhs + " = " + ccode(eq)

            self.equations.append(
                {
                    'name': name,
                    'type': 'assignment',
                    'sympy': eq,
                    'code': code,
                    'human-readable': code % default_dict,
                }
            )


class ODEBlock(Block):

    def __init__(self, parser, method):

        self.method = method

        super(ODEBlock, self).__init__(parser)

    def parse(self):

        if self.method == 'euler':
            "Euler equations can be generated independently."

            gradients = []
            updates = []

            for name, eq in self._equations:

                # Compute the gradient
                gradient = "__grad__" + name + " = " + ccode(eq)

                # Update the variable
                update = self.parser.get_symbol(name) + " += dt*" + "__grad__" + name 

                gradients.append(
                    {
                    'name': "__grad__" + name,
                    'type': 'tmp',
                    'sympy': eq,
                    'code': gradient,
                    'human-readable': gradient % default_dict,

                    }
                )
                updates.append(
                    {
                    'name': self.parser.get_symbol(name),
                    'type': 'assignment',
                    'sympy': " += dt*" + "__grad__" + name ,
                    'code': update,
                    'human-readable': update % default_dict,

                    }
                )

            for gradient in gradients:
                self.equations.append(gradient)

            for update in updates:
                self.equations.append(update)

        elif self.method == 'exponential':

            gradients = []
            updates = []

            for name, eq in self._equations:

                # Gradient is of the form v' = (A - v)/tau

                # Expand the equation to better find the time constant:
                # v' = A/tau - v/tau
                expanded = eq.expand(
                    modulus=None, power_base=False, power_exp=False,
                    mul=True, log=False, multinomial=False
                )

                # Current variable v
                var = sp.Symbol(self.parser.get_symbol(name))

                # Factorize over the variable v: X*1 - v/tau
                collected_var = sp.collect(expanded, var, evaluate=False, exact=False)

                # Inverse the factor multiplying v to get tau
                tau = -1/collected_var[var]

                # Multiply the gradient by tau to get (A - v)
                steady = sp.simplify(tau * expanded)
                
                # Compute the gradient v' = (1- exp(-dt/tau))*(A - v)
                gradient = "__grad__" + name + " = (1.0 - exp(-dt/" + ccode(tau) + "))*(" + ccode(steady) + ")" 

                # Update the variable r += v'
                update = self.parser.get_symbol(name) + " = " + "__grad__" + name 
                    
                gradients.append(
                    {
                    'name': "__grad__" + name,
                    'type': 'tmp',
                    'sympy': eq,
                    'code': gradient,
                    'human-readable': gradient % default_dict,

                    }
                )
                updates.append(
                    {
                    'name': self.parser.get_symbol(name),
                    'type': 'assignment',
                    'sympy': " = " + "__grad__" + name  ,
                    'code': update,
                    'human-readable': update % default_dict,

                    }
                )

            for gradient in gradients:
                self.equations.append(gradient)

            for update in updates:
                self.equations.append(update)

        elif self.method == 'midpoint':

            gradients = []
            updates = []

            for name, eq in self._equations:

                # Current symbol v
                var = sp.Symbol(self.parser.get_symbol(name))

                # Compute v + dt/2*v'
                new_var = var + sp.Symbol('dt')*eq/2.0

                # Evaluate gradient in v + dt/2*v'
                new_eq = eq.subs(var, new_var)

                # Gradient v'
                gradient = "__grad__" + name + " = " + ccode(new_eq)

                # Update the variable r += v'
                update = self.parser.get_symbol(name) + " = dt*" + "__grad__" + name 

                gradients.append(
                    {
                    'name': "__grad__" + name,
                    'type': 'tmp',
                    'sympy': new_eq,
                    'code': gradient,
                    'human-readable': gradient % default_dict,

                    }
                )
                updates.append(
                    {
                    'name': self.parser.get_symbol(name),
                    'type': 'assignment',
                    'sympy': " = dt*" + "__grad__" + name ,
                    'code': update,
                    'human-readable': update % default_dict,

                    }
                )

            for gradient in gradients:
                self.equations.append(gradient)

            for update in updates:
                self.equations.append(update)

        else:
            self.parser.logger.error(self.method + " is not implemented yet.")
            sys.exit(1)


