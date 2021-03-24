import sys
import logging

import ANNarchy_future.api as api

from ..parser.SynapseParser import SynapseParser

class Projection(object):
    """
    Projection between two populations.

    """
    def __init__(self, 
        pre : 'api.Population', 
        post : 'api.Population', 
        target : str, 
        synapse : 'api.Synapse', 
        name : str):

        self.pre = pre
        self.post = post
        self.target = target
        self.name = name

        # Synapse instance
        self._synapse_type = synapse
        self.synapse_class : str = synapse.__class__.__name__

        # Internal stuff
        self._net = None
        self._attributes = {}

        self._logger = logging.getLogger(__name__)
        self._logger.info("Projection created between " + self.pre.name + " and " + self.post.name)

    ###########################################################################
    # Internal methods
    ###########################################################################
    def _register(self, net:api.Network, id_proj:int):
        "Called by Network with the ID of the projection."

        self._logger.debug("Registering projection with ID " + str(id_proj))

        self._net = net
        self.id_proj = id_proj

        if self.name is None:
            self.name = "Projection " + str(self.id_proj)
        self._logger.debug("Projection's name is set to " + str(self.name))


    def _analyse(self):
        """Creates a SynapseParser and calls:

        * `parser.extract_variables()`
        * `parser.analyse_equations()`

        """

        # Create the projection parser
        self._logger.debug("Creating synapse parser.")
        self._parser = SynapseParser(self._synapse_type, self.pre._neuron_type, self.post._neuron_type)
        
        # Retrieve attributes
        self._parser.extract_variables()
        self.attributes = self._parser.attributes

        # Instantiate the attributes
        for attr in self._parser.attributes:
            self._attributes[attr] = getattr(self._synapse_type, attr)._copy()
            self._attributes[attr]._instantiate((10,))
        
        # Analyse the equations
        self._parser.analyse_equations()
