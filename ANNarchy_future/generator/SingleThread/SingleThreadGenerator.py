import sys
import logging

import sympy as sp

from .PopulationGenerator import PopulationGenerator
from .ProjectionGenerator import ProjectionGenerator


class SingleThreadGenerator(object):

    def __init__(self, description:dict):
        
        self.description:dict = description

    def generate(self):

        # Generate Populations        
        neurons = self.description['neurons']

        for name, parser in neurons.items():

            parser = PopulationGenerator(name, parser)
            code = parser.generate()

            print(code)

        # Generate Projections        
        synapses = self.description['synapses']

        for name, parser in synapses.items():

            parser = ProjectionGenerator(name, parser)
            code = parser.generate()

            print(code)

