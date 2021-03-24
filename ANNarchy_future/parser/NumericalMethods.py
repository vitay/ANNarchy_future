import sympy as sp

import ANNarchy_future.parser as parser

def euler(equations):

    gradients = []
    updates = []

    if len(equations) == 0:
        pass

    elif len(equations) == 1:

        name, eq = equations[0]

        # Update the variable
        update = sp.Symbol('dt') * eq 
        update_hr = name + " += " + parser.ccode(update)

        updates.append(
            {
            'type': 'assignment',
            'name': name,
            'op': "+=",
            'rhs': update,
            'human-readable': update_hr,

            }
        )
    
    else: # More than one equation

        for name, eq in equations:

            # Compute the gradient
            gradient_var = "__k__" + name
            gradient_hr = gradient_var + " = " + parser.ccode(eq)

            # Update the variable
            update = sp.Symbol('dt') * sp.Symbol(gradient_var) 
            update_hr = name + " += " + parser.ccode(update)

            gradients.append(
                {
                'type': 'tmp',
                'name': gradient_var,
                'op': "=",
                'rhs': eq,
                'human-readable': gradient_hr,

                }
            )
            updates.append(
                {
                'type': 'assignment',
                'name': name,
                'op': "+=",
                'rhs': update,
                'human-readable': update_hr,

                }
            )

    # Gather equations in the right order
    processed_equations = []

    for gradient in gradients:
        processed_equations.append(gradient)

    for update in updates:
        processed_equations.append(update)

    return processed_equations


def exponential(equations):

    gradients = []
    updates = []

    for name, eq in equations:

        # Gradient is of the form v' = (A - v)/tau

        # Expand the equation to better find the time constant:
        # v' = A/tau - v/tau
        expanded = eq.expand(
            modulus=None, power_base=False, power_exp=False,
            mul=True, log=False, multinomial=False
        )

        # Current variable v
        var = sp.Symbol(name)
        
        # Gradient name
        gradient_var = "__k__" + name

        # Factorize over the variable v: X*1 - v/tau
        collected_var = sp.collect(expanded, var, evaluate=False, exact=False)

        # Inverse the factor multiplying v to get tau
        tau = -1/collected_var[var]

        # Step size is (1 - exp(-dt/tau))
        step_size = sp.simplify(1. - sp.exp(-sp.Symbol('dt')/tau))

        # Multiply the gradient by tau to get (A - v)
        steady = sp.simplify(tau * expanded)
        
        # Compute the gradient v' = (1- exp(-dt/tau))*(A - v)
        gradient = step_size * steady 
        gradient_hr = gradient_var + " = " + parser.ccode(gradient)

        # Update the variable r += v'
        update_hr = name + " += " + gradient_var
            

        gradients.append(
            {
            'type': 'tmp',
            'name': gradient_var,
            'op': "=",
            'rhs': gradient,
            'human-readable': gradient_hr,
            }
        )
        updates.append(
            {
            'type': 'assignment',
            'name': name,
            'op': "+=",
            'rhs': sp.Symbol(gradient_var),
            'human-readable': update_hr,

            }
        )

    # Gather equations in the right order
    processed_equations = []
    
    for gradient in gradients:
        processed_equations.append(gradient)

    for update in updates:
        processed_equations.append(update)

    return processed_equations


def midpoint(equations):


    midpoints = []
    midpoint_vars = {}

    updates = []

    for name, eq in equations:

        # Current symbol v
        var = sp.Symbol(name)

        # Midpoint name
        midpoint_var = "__k1__" + name
        midpoint_vars[var] = sp.Symbol(midpoint_var)

        # Compute v + dt/2*v'
        midpoint = var + sp.Symbol('dt') * eq / 2.0

        midpoint_hr = midpoint_var + " = " + parser.ccode(midpoint)

        midpoints.append(
            {
            'type': 'tmp',
            'name': midpoint_var,
            'op': "=",
            'rhs': midpoint,
            'human-readable': midpoint_hr,
            }
        )
    
    for name, eq in equations:

        # Evaluate gradient in v + dt/2*v'
        new_eq = sp.Symbol('dt') * eq.subs(midpoint_vars)

        # Human readable
        update_hr = name + " += " + parser.ccode(new_eq)

        updates.append(
            {
            'type': 'assignment',
            'name': name,
            'op': "+=",
            'rhs': new_eq,
            'human-readable': update_hr,

            }
        )

    # Gather equations in the right order
    processed_equations = []

    for midpoint in midpoints:
        processed_equations.append(midpoint)

    for update in updates:
        processed_equations.append(update)

    return processed_equations

def rk4(equations):

    k1s = []
    k2s = []
    k3s = []
    k4s = []

    p2s = []
    p3s = []
    p4s = []

    k2_vars = {}
    k3_vars = {}
    k4_vars = {}

    updates = []

    # k1 = f'(x, y)
    for name, eq in equations:

        # Current symbol v
        var = sp.Symbol(name)

        # k1
        k1_var = "__k1__" + name
        p2_var = "__p2__" + name
        k2_vars[var] = sp.Symbol(p2_var)
        p2 = var + sp.Symbol('dt') * sp.Symbol(k1_var) / 2.0

        k1_hr = k1_var + " = " + parser.ccode(eq)
        p2_hr = p2_var + " = " + parser.ccode(p2)

        k1s.append(
            {
            'type': 'tmp',
            'name': k1_var,
            'op': "=",
            'rhs': eq,
            'human-readable': k1_hr,
            }
        )
        p2s.append(
            {
            'type': 'tmp',
            'name': p2_var,
            'op': "=",
            'rhs': p2,
            'human-readable': p2_hr,
            }
        )


    # k2 = f'(x + dt*k1/2, y + dt*k1/2)
    for name, eq in equations:

        # Current symbol v
        var = sp.Symbol(name)

        # Compute v + dt/2*v'
        k2 = sp.simplify(eq.subs(k2_vars))

        # k1
        k2_var = "__k2__" + name
        p3_var = "__p3__" + name
        k3_vars[var] = sp.Symbol(p3_var)
        p3 = var + sp.Symbol('dt') * sp.Symbol(k2_var) / 2.0

        k2_hr = k2_var + " = " + parser.ccode(k2)
        p3_hr = p3_var + " = " + parser.ccode(p3)

        k2s.append(
            {
            'type': 'tmp',
            'name': k2_var,
            'op': "=",
            'rhs': k2,
            'human-readable': k2_hr,
            }
        )
        p3s.append(
            {
            'type': 'tmp',
            'name': p3_var,
            'op': "=",
            'rhs': p3,
            'human-readable': p3_hr,
            }
        )


    # k3 = f'(x + dt*k2/2, y + dt*k2/2)
    for name, eq in equations:

        # Current symbol v
        var = sp.Symbol(name)

        # Substitute
        k3 = sp.simplify(eq.subs(k3_vars))

        # k3
        k3_var = "__k3__" + name

        p4_var = "__p4__" + name
        k4_vars[var] = sp.Symbol(p4_var)
        p4 = var + sp.Symbol('dt') * sp.Symbol(k3_var)


        k3_hr = k3_var + " = " + parser.ccode(k3)
        p4_hr = p4_var + " = " + parser.ccode(p4)

        k3s.append(
            {
            'type': 'tmp',
            'name': k3_var,
            'op': "=",
            'rhs': k3,
            'human-readable': k3_hr,
            }
        )
        p4s.append(
            {
            'type': 'tmp',
            'name': p4_var,
            'op': "=",
            'rhs': p4,
            'human-readable': p4_hr,
            }
        )

    # k4 = f'(x + dt*k3, y + dt*k3)
    for name, eq in equations:

        # Current symbol v
        var = sp.Symbol(name)

        # Substitute
        k4 = sp.simplify(eq.subs(k4_vars))

        # k4
        k4_var = "__k4__" + name

        k4_hr = k4_var + " = " + parser.ccode(k4)

        k4s.append(
            {
            'type': 'tmp',
            'name': k4_var,
            'op': "=",
            'rhs': k4,
            'human-readable': k4_hr,
            }
        )

    for name, eq in equations:

        # tmp vars
        var = sp.Symbol(name)
        k1 = sp.Symbol("__k1__" + name)
        k2 = sp.Symbol("__k2__" + name)
        k3 = sp.Symbol("__k3__" + name)
        k4 = sp.Symbol("__k4__" + name)

        # Evaluate gradient in v + dt/2*v'
        new_eq = sp.Symbol('dt') * (k1 + 2*k2 + 2*k3 + k4)/sp.Symbol("6.0")

        # Human readable
        update_hr = name + " += " + parser.ccode(new_eq)

        updates.append(
            {
            'type': 'assignment',
            'name': name,
            'op': "+=",
            'rhs': new_eq,
            'human-readable': update_hr,

            }
        )

    # Gather equations in the right order
    processed_equations = []

    for k1 in k1s:
        processed_equations.append(k1)
    for p2 in p2s:
        processed_equations.append(p2)
    for k2 in k2s:
        processed_equations.append(k2)
    for p3 in p3s:
        processed_equations.append(p3)
    for k3 in k3s:
        processed_equations.append(k3)
    for p4 in p4s:
        processed_equations.append(p4)
    for k4 in k4s:
        processed_equations.append(k4)

    for update in updates:
        processed_equations.append(update)


    return processed_equations