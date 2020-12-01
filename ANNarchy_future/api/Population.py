

class Population:
    """
    Population of neurons.
    """

    def __init__(self, net, shape, neuron, name):
        self.attributes = {}

        self.net = net
        self.shape = shape
        self.neuron = neuron
        self.name = name

        # Geometry
        if isinstance(shape, int):
            self.size = shape
            self.ndim = 1
        elif isinstance(shape, tuple):
            self.size = 1
            self.ndim = len(shape)
            for dim in shape:
                self.size *= dim
        else:
            raise Exception("wrong size")

        # Initialize the Value and Array instances
        self.attributes = []
        self.parameters = []
        self.variables = []

    def _init(self):
        "Called from the network."
        for param, val in self.neuron.parameters.items():
            self.net._register_population_attribute(self, param, val)
            self.attributes.append(param)
            self.parameters.append(param)
        for param, val in self.neuron.equations.items():
            self.net._register_population_attribute(self, param, val)
            self.attributes.append(param)
            self.variables.append(param)


    def __getattr__(self, name):
        " Method called when accessing an attribute."
        if name == 'attributes' or not hasattr(self, 'attributes'): # Before the end of the constructor
            return object.__getattribute__(self, name)
        if hasattr(self, 'attributes'):
            if name in self.attributes:
                return self.net._population_attributes[self.name][name].value
            else:
                return object.__getattribute__(self, name)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name == 'attributes' or not hasattr(self, 'attributes'): # Before the end of the constructor
            object.__setattr__(self, name, value)
            return
        if hasattr(self, 'attributes'):
            if name in self.attributes:
                self.net._population_attributes[self.name][name].value = value
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)