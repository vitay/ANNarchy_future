
import ANNarchy_future.generator as generator
import ANNarchy_future.communicator as communicator

class Compiler(object):

    """Generates code and compiles it.

    Attributes:

        backend: 'single', 'openmp', 'cuda' or 'mpi'.
        description: network description passed by the `Network()` instance.

    """

    def __init__(self, description:dict, backend:str):
        """
        Initializes the code generators.
        """
        self.backend:str = backend
        self.description:dict = description

        if backend == "single":
            self._generator = generator.SingleThread.SingleThreadGenerator(
                description
            )
        else:
            raise NotImplementedError

    def hardware_check(self):
        """Checks whether the provided network can be compiled on the current hardware.
        
        Checks whether:

        * the projection formats are available for the backend.
        * fitting hardware?
            * MPI: host available?
            * CUDA: GPU available?
        """

        # If needed: https://github.com/workhorsy/py-cpuinfo

        pass

    def compile(self) -> 'communicator.SimulationInterface':
        """
        Compiles the generated code.

        Returns:

            a `SimulationInterface` instance allowing Python to communicate with the C++ kernel.
        """

        # Calls the generator generator() method
        self._generator.generate()

        # Compilation
        
        # Import shared library
        library = None

        if self.backend == "single":
            interface = communicator.CythonInterface(library)
        else:
            raise NotImplementedError

        return interface