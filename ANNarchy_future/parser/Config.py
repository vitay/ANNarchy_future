import sympy as sp

# Built-in symbols
symbols_dict = {
    't': sp.Symbol("t"),
    'dt': sp.Symbol("dt"),
    'spike': sp.Symbol("spike"),
}

# List of names that should not be used as attributes of a Neuron or Synapse
reserved_attributes = [
    't',
    'dt',
    'spike',
    'ite',
    'cast',
    'clip',
    'pre',
    'post',
]

# Empty parsing dict to retrieve variable names
empty_dict = {
    'pop_prefix_parameter': "",
    'pop_suffix_parameter': "",
    'pop_prefix_variable': "",
    'pop_suffix_variable': "",
}

# Simple parsing dict for human-readable equations
default_dict = {
    'pop_prefix_parameter': "",
    'pop_suffix_parameter': "",
    'pop_prefix_variable': "",
    'pop_suffix_variable': "[i]",
}
