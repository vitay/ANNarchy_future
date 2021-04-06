import sys, os
import logging
import subprocess
import shutil
import imp

import ANNarchy_future.api as api
import ANNarchy_future.generator as generator
import ANNarchy_future.communicator as communicator

class Compiler(object):

    """Generates code, compiles it and instantiate the network.

    """

    def __init__(self, 
        net: 'api.Network',
        backend:str,
        ):
        
        """
        Initializes the code generators.

        Args:
            net: Python Network instance.
            backend: 'single', 'openmp', 'cuda' or 'mpi'.
        """
        self.net = net
        self.backend:str = backend
        self.annarchy_dir = self.net._annarchy_dir

        # Logging
        self._logger = logging.getLogger(__name__)
        self._logger.info("Compiling.")

        if backend == "single":
            self._generator = generator.SingleThread.SingleThreadGenerator(
                self.net._description,
                backend
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

        # Call the generator generator() method
        self._generator.generate()

        # Create the compilation folder
        self._compilation_folder()

        # Generate files
        self._generator.copy_files(self.annarchy_dir)

        # Compile the code
        self._compile()

        # Import shared library
        library = "ANNarchyCore"

        if self.backend == "single":
            interface = communicator.CythonInterface(self.net, library)
        else:
            raise NotImplementedError

        return interface

    def _compilation_folder(self):
        """Creates the compilation folder.

        TODO: completely erases the current directory for now.

        """

        shutil.rmtree(self.annarchy_dir, True)

        os.mkdir(self.annarchy_dir)

        sys.path.append(self.annarchy_dir)


    def _compile(self):
        """Compiles the source code to produce the shared library.

        Calls `make -j4` in a subprocess.
        """
        # Current directory
        cwd = os.getcwd()

        # Switch to the build directory
        os.chdir(self.annarchy_dir)

        # Start the compilation process
        make_process = subprocess.Popen("make all -j4 > compile_stdout.log 2> compile_stderr.log", shell=True)


        # Check for errors
        if make_process.wait() != 0:
            with open('./compile_stdout.log', 'r') as rfile:
                msg = rfile.read()
            self._logger.info(msg)
            with open('./compile_stderr.log', 'r') as rfile:
                msg = rfile.read()
            self._logger.error(msg)
            sys.exit(1)
        else:
            with open('./compile_stdout.log', 'r') as rfile:
                msg = rfile.read()
            self._logger.info(msg)

        # Return to the current directory
        os.chdir(cwd)