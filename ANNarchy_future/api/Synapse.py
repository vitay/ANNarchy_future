

class Synapse:
    "Synapse."
    def __init__(self, 
                parameters= {}, 
                equations = {},
                psp = "",
                operator="sum",
                pre_spike = None,
                post_spike = None,
                name = "",
                description = ""
            ):
        self.parameters = parameters
        self.equations = equations
        self.psp = psp
        self.operator = operator
        self.pre_spike = pre_spike
        self.post_spike = post_spike
        self.name = name
        self.description = description