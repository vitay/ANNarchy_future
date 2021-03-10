from .SimCoreInterface import SimCoreInterface
from .SingleThread import SingleThreadGenerator

class Compiler(object):

    def __init__(self, populations, backend):
        """
        Initilize the code generators.
        """
        if backend == "single":
            self._generator = SingleThreadGenerator(
                populations
            )
        else:
            raise NotImplementedError

    def sanity_check(self):
        """
        Verify if the provided network can be compiled, e. g.

        * projection formats available
        * fitting hardware?
            * MPI: host available?
            * CUDA: GPU available?
        """
        pass

    def compile(self):
        # call the generator
        self._generator.generate()

        # compilation
        
        # import lib
        library = None

        return SimCoreInterface(library)