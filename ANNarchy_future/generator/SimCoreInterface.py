class SimCoreInterface(object):

    def __init__(self, library):
        pass

    def _instantiate(self, ip_address="127.0.0.1"):
        """
        Create the CPP simulation core instance and retrieve the
        object IDs and match them to the Python object names.
        """
        self._network_instance = 0
        self._population_instances = {
            "pop0": 0
        }
