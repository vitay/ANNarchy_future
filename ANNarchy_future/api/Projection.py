

class Projection:
    """
    Projection
    """
    def __init__(self, net, pre, post, target, synapse, name):

        self.net = net

        self.pre = pre
        self.post = post
        self.target = target
        self.synapse = synapse
        self.name = name

        # Initialize the Value and Array objects
        self._init()

    def _init(self):
        for param, val in self.synapse.parameters.items():
            setattr(self, param, val.value)
        for var, val in self.synapse.equations.items():
            setattr(self, var, val.value)


    def fill(self, w=0.0, d=0.0, connector=None, format='lil'):
        self.w = w
        self.d = d
        self.connector = connector
        self.format = format