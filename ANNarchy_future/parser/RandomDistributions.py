

class Uniform(object):

    def __init__(self, name, min, max):

        self.name = name
        self.min = min
        self.max = max

    def human_readable(self):

        return "Uniform(" + str(self.min) + ", " + str(self.max) + ")"

class Normal(object):

    def __init__(self, name, mu, sigma):

        self.name = name
        self.mu = mu
        self.sigma = sigma

    def human_readable(self):

        return "Normal(" + str(self.mu) + ", " + str(self.sigma) + ")"