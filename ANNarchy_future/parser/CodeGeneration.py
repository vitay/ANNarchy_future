import sys
import logging
import string

import sympy as sp

from sympy.codegen.rewriting import optims_c99, optimize, ReplaceOptim
from sympy.core.mul import Mul
from sympy.core.expr import UnevaluatedExpr

def ccode(eq) -> str:
    """Transforms a sympy expression into C99 code.

    Applies C99 optimizations (`sympy.codegen.rewriting.optims_c99`).

    Expands `pow(x; 2)` into `x*x` and `pow(x, 3)` into `x*x*x` for performance.

    Args:
        eq (sympy expression): expression to convert.

    Returns:
        a string representing the C code.
    """
    # If the rhs is a int or float (v = 0.0), cast it to a symbol to avoid numerical errors.
    if isinstance(eq, (float)):
        eq = sp.Symbol(str(float(eq))) 
    elif isinstance(eq, (int)):
        eq = sp.Symbol(str(int(eq))) 

    # Optimize for C99
    try:
        eq = optimize(eq, optims_c99)
    except:
        logger = logging.getLogger(__name__)
        logger.exception(str(eq))
        sys.exit(1)

    # Explicitly expand the use of pow(x, 2)
    pow2 = ReplaceOptim(
        lambda p: p.is_Pow and p.exp == 2,
        lambda p: UnevaluatedExpr(Mul(p.base, p.base, evaluate=False))
    )
    eq = pow2(eq)
    

    # Explicitly expand the use of pow(x, 3)
    pow3 = ReplaceOptim(
        lambda p: p.is_Pow and p.exp == 3,
        lambda p: UnevaluatedExpr(Mul(Mul(p.base, p.base, evaluate=False), p.base, evaluate=False))
    )
    eq = pow3(eq)
    
    # Get the equivalent C code
    eq = sp.ccode(
        eq, 
    )
    
    # Remove the extralines of Piecewise
    return " ".join(eq.replace('\n', ' ').split())


def code_generation(eq, correspondance:dict = {}) -> str:
    """Gets a dictionary of correspondances and changes all symbols in the sympy expression.

    Calls `eq.subs()` and `ccode`.

    Args:

        eq (sympy expression): expression.
        correspondance (dict): dictionary of correspondances.

    Returns:

        a string representing the C code.

    Example:

        >>> code_generation(
            sp.Symbol(tau) * sp.Symbol(r), 
            {'tau': 'this->tau', 'r': 'this->r[i]'})
        this->tau*this->r[i]

    """
    # If the rhs is a int or float (v = 0.0), cast it to a symbol to avoid numerical errors.
    if isinstance(eq, (float)):
        eq = sp.Symbol(str(float(eq))) 
    elif isinstance(eq, (int)):
        eq = sp.Symbol(str(int(eq))) 

    # Build a dictionary of sp.Symbols()
    replacements = {}
    for pre, post in correspondance.items():
        replacements[sp.Symbol(pre)] = sp.Symbol(post)

    # Replace the symbols
    new_eq = eq.subs(replacements)

    return ccode(new_eq)
