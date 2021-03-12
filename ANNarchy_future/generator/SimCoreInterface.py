

class SimCoreInterface(object):
    """Class managing communication with the kernel.

    """

    def __init__(self, library):
        pass

    def _instantiate(self, ip_address="127.0.0.1"):
        
        """Creates the CPP simulation core instance, retrieves the
        object IDs and match them to the Python object names.
        """

        self._network_instance = 0
        self._population_instances = {
            "pop0": 0
        }

        return 0
