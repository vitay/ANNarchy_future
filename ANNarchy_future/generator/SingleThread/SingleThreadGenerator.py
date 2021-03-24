import sys
import logging

import sympy as sp

import ANNarchy_future.generator as generator


class SingleThreadGenerator(object):

    def __init__(self, description:dict):
        
        self.description:dict = description

    def generate(self):

        # Generate Populations        
        neurons = self.description['neurons']

        for name, parser in neurons.items():

            parser = generator.SingleThread.PopulationGenerator(name, parser)
            code = parser.generate()

            print(code)

        # Generate Projections        
        synapses = self.description['synapses']

        for name, parser in synapses.items():

            parser = generator.SingleThread.ProjectionGenerator(name, parser)
            code = parser.generate()

            print(code)

