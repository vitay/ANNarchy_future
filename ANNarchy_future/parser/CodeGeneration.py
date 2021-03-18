import sympy as sp

from sympy.codegen.rewriting import optims_c99, optimize, ReplaceOptim
from sympy.core.mul import Mul
from sympy.core.expr import UnevaluatedExpr

def ccode(eq):

    # Optimize for C99
    eq = optimize(eq, optims_c99)

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
    eq = sp.ccode(eq)
    
    # Remove the extralines of Piecewise
    return " ".join(eq.replace('\n', ' ').split())


def code_generation(eq, correspondance):

    replacements = {}
    for pre, post in correspondance.items():
        replacements[sp.Symbol(pre)] = sp.Symbol(post)

    new_eq = eq.subs(replacements)

    return ccode(new_eq)