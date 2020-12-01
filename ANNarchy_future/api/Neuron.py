

class Neuron:
    "Neuron."
    def __init__(self, 
                parameters= {}, 
                equations = {},
                spike = "",
                reset = [],
                refractory = None,
                name = "",
                description = ""
            ):
        self.parameters = parameters
        self.equations = equations
        self.spike = spike
        self.reset = reset
        self.refractory = refractory
        self.name = name
        self.description = description