import sys, os
import logging
import subprocess
import shutil
import imp
from string import Template

import ANNarchy_future.api as api
import ANNarchy_future.generator as generator
import ANNarchy_future.communicator as communicator

class Compiler(object):

    """Generates code, compiles it and instantiate the network.

    The Network instance should call `Compiler.build()`.

    The code generators should call `Compiler.write_file(filename, content)` to write a file.

    Compiler manages everything related to the compilation folder.
    """

    def __init__(self, 
        net: 'api.Network',
        backend:str,
        clean:bool = False,
        ):
        
        """
        Initializes the code generators.

        Args:
            net: Python Network instance.
            backend: 'single', 'openmp', 'cuda' or 'mpi'.
            clean: forces complete code generation.
        """
        self.net = net
        self.backend:str = backend
        self.annarchy_dir = self.net._annarchy_dir
        self.build_dir = self.annarchy_dir + "/build/"
        self.clean = clean

        self.library = "ANNarchyCore"
        self.library_path = self.build_dir + self.library + ".so"

        self._has_changed = clean

        # Logging
        self._logger = logging.getLogger(__name__)

        # Hardware check
        self.hardware_check()

        if backend == "single":
            self._generator = generator.SingleThread.SingleThreadGenerator(
                compiler=self,
                description=self.net._description,
                backend=self.backend,
                library=self.library,
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

    def build(self) -> 'communicator.SimulationInterface':
        """
        Compiles the generated code.

        Returns:

            a `SimulationInterface` instance allowing Python to communicate with the C++ kernel.
        """

        # Call the generator generator() method
        self._generator.generate()

        # Create the compilation folder
        self.compilation_folder()

        # Generate files
        self.generated_files = []
        self._generator.copy_files()

        # Clean files from a previous compilation
        self.clean_generated_files()

        # Compile the code
        if self._has_changed:
            self.compile()

        # Instantiate an interface (Cython or gRPC)
        if self.backend == "single":
            interface = communicator.CythonInterface(self.net, self.library, self.library_path)
        else:
            raise NotImplementedError

        return interface

    def compilation_folder(self):
        """Creates the compilation folder.

        TODO: completely erases the current directory for now.

        """
        if self.clean:
            shutil.rmtree(self.annarchy_dir, True)

        if not os.path.exists(self.annarchy_dir):
            os.mkdir(self.annarchy_dir)
            self._has_changed = True

        if not os.path.exists(self.build_dir):
            os.mkdir(self.build_dir)
            self._has_changed = True

    def write_file(self, filename:str, content:str):
        """Writes the file in the compilation folder if needed.

        Called by `self._generator.copy_files()` for each file.

        Args:
            filename: filename.
            content: content of the file.
        """
        self.generated_files.append(filename)

        complete_path = self.build_dir + filename

        # If it does not exist, write and exit
        if not os.path.exists(complete_path):
            self._has_changed = True
            with open(complete_path, 'w') as f:
                f.write(content)
            return

        # If it exists, load its content
        old_content = ""
        with open(complete_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            old_content += line

        if old_content != content:
            self._logger.info(filename + " has changed.")
            self._has_changed = True
            # Write the content
            with open(complete_path, 'w') as f:
                f.write(content)

    def clean_generated_files(self):
        """Removes generated files in the generated folder that were not recently written.
        """

        current_files = os.listdir(self.build_dir)
        diff = list(set(current_files) - set(self.generated_files))
        for f in diff:
            if f.endswith(".hpp"):
                os.remove(self.build_dir + f)
                self._has_changed = True


    def compile(self):
        """Compiles the source code to produce the shared library.

        Calls `make -j4` in a subprocess.
        """
        self._logger.info("Compiling.")

        # Current directory
        cwd = os.getcwd()

        # Switch to the build directory
        os.chdir(self.build_dir)

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


def fetch_template(filename:str) -> Template:
    """Retrieves a template file.

    Args: 

        filename: relative to ANNarchy/future (e.g. '/generator/SingleThread/templates/Population.hpp')

    Returns:

        a `string.Template` object.
    """

    import ANNarchy_future

    file_path = str(ANNarchy_future.__path__[0]) +  filename

    with open(file_path, 'r') as f:
        template = f.readlines()
    
    template = Template("".join(template))

    return template