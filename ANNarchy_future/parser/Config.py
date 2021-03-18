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
