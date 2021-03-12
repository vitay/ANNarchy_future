from .SimCoreInterface import SimCoreInterface
from .SingleThread import SingleThreadGenerator

class Compiler(object):

    """Generates code and compiles it.

    """

    def __init__(self, description, backend):
        """
        Initializes the code generators.
        """
        self.backend = backend
        self.description = description

        if backend == "single":
            self._generator = SingleThreadGenerator(
                description
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

        # If needed: https://github.com/workhorsy/py-cpuinfo

        pass

    def compile(self) -> SimCoreInterface:
        """
        Compiles the generated code.
        """

        # Calls the generator generator() method
        self._generator.generate()

        # compilation
        
        # import lib
        library = None

        return SimCoreInterface(library)