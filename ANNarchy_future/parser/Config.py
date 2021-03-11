# Simple parsing dict for readable equations
default_dict = {
    'pop_prefix_value': "",
    'pop_suffix_value': "",
    'pop_prefix_array': "",
    'pop_suffix_array': "[i]",
    'proj_prefix_value': "",
    'proj_suffix_value': "",
    'proj_prefix_array': "",
    'proj_suffix_array': "[i, j]",
}

# List of names that should not be used as attributes of a Neuron or Synapse
reserved_attributes = [
    't',
    'dt',
    'spike',
    'ite',
    'cast',
]
