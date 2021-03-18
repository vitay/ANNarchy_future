import sys
import logging

from .Array import Parameter, Variable
from .Synapse import Synapse
from ..parser.SynapseParser import SynapseParser

class Projection(object):
    """
    Projection.
    """
    def __init__(self, pre, post, target, synapse, name):

        self.pre = pre
        self.post = post
        self.target = target
        self._synapse_type = synapse
        self.name = name


        # Internal stuff
        self._net = None
        self._attributes = {}

        self.logger = logging.getLogger(__name__)
        self.logger.info("Projection created between " + self.pre.name + " and " + self.post.name)

    ###########################################################################
    # Internal methods
    ###########################################################################
    def _register(self, net, id_proj):
        "Called by Network."

        self.logger.debug("Registering projection with ID " + str(id_proj))

        self._net = net
        self.id_proj = id_proj

        if self.name is None:
            self.name = "Projection " + str(self.id_proj)
        self.logger.debug("Projection's name is set to " + str(self.name))


    def _analyse(self):

        # Create the projection parser
        self.logger.debug("Creating synapse parser.")
        self._parser = SynapseParser(self._synapse_type, self.pre._neuron_type, self.post._neuron_type)
        
        # Retrieve attributes
        self._parser.extract_variables()
        self.attributes = self._parser.attributes

        # Synapse class name
        self.synapse_class : str = self._parser.name

        # Instantiate the attributes
        for attr in self._parser.attributes:
            self._attributes[attr] = getattr(self._synapse_type, attr)._copy()
            self._attributes[attr]._instantiate((10,))
        
        # Analyse the equations
        self._parser.analyse_equations()
