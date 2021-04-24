import sys
import logging
from string import Template

import numpy as np

import ANNarchy_future.generator as generator


class SingleThreadGenerator(object):

    """Generates the C++ code for single-threaded simulation.

    """

    def __init__(self, description:dict, backend:str):

        """
        Args:

            description: dictionary passed by `Network`.
            backend: 'single', 'openmp', 'cuda' or 'mpi'.
        """
        
        self.description:dict = description
        self.backend = backend

        self.neuron_classes:dict = {}
        self.neuron_exports:dict = {}
        self.neuron_wrappers:dict = {}

        self.synapse_classes:dict = {}
        self.synapse_exports:dict = {}
        self.synapse_wrappers:dict = {}

    def generate(self):
        """Generates the necessary C++ classes.

        * Neuron classes.
        * Synapse classes.
        * Main class.
        * Bindings (Cython or gRPC) depending on the backend.
        """

        # Generate Neuron classes 
        self.generate_neurons() 

        # Generate Synapse classes 
        self.generate_synapses() 

        # Generate ANNarchy.h
        self.generate_header()

        # Generate Network.h and Network.cpp
        self.generate_network()

        # Generate ANNarchyCore.pyx
        self.generate_cython()

        # Generate Makefile
        self.generate_makefile()



    def copy_files(self, annarchy_dir):
        """
        Puts the files in the compilation folder.
        """

        # Makefile
        with open(annarchy_dir +"Makefile", 'w') as f:
            f.write(self.makefile)

        # ANNarchy.h
        with open(annarchy_dir +"ANNarchy.hpp", 'w') as f:
            f.write(self.annarchy_h)

        # Network.h
        with open(annarchy_dir +"Network.hpp", 'w') as f:
            f.write(self.network_h)

        # ANNarchyBindings.pxd
        with open(annarchy_dir +"ANNarchyBindings.pxd", 'w') as f:
            f.write(self.cython_bindings)

        # ANNarchyCore.pyx
        with open(annarchy_dir +"ANNarchyCore.pyx", 'w') as f:
            f.write(self.cython_network)

        # Neuron classes
        for name, code in  self.neuron_classes.items():
            with open(annarchy_dir + name+".hpp", 'w') as f:
                f.write(code)

        # Synapse classes
        for name, code in  self.synapse_classes.items():
            with open(annarchy_dir + name+".hpp", 'w') as f:
                f.write(code)

    def generate_neurons(self):
        """Generates one C++ class per neuron definition by calling `SingleThread.PopulationGenerator`.
                
        Sets:
        
            self.neuron_classes (dict)
            self.neuron_exports (dict)
            self.neuron_wrappers (dict)
        """

        # Generate Neuron classes        
        neurons = self.description['neurons']

        for name, parser in neurons.items():

            parser = generator.SingleThread.PopulationGenerator(name, parser)

            # C++ class
            code = parser.generate()
            self.neuron_classes[name] = code

            # Cython export
            code = parser.cython_export()
            self.neuron_exports[name] = code

            # Cython wrapper
            code = parser.cython_wrapper()
            self.neuron_wrappers[name] = code

    def generate_synapses(self):
        """Generates one C++ class per synapse definition by calling `SingleThread.ProjectionGenerator`.
        
        Sets:
        
            self.synapse_classes (dict)
        """

        # Generate Synapse classes        
        synapses = self.description['synapses']

        for name, parser in synapses.items():

            parser = generator.SingleThread.ProjectionGenerator(name, parser)
            
            # C++ code
            code = parser.generate()
            self.synapse_classes[name] = code

            # Cython export
            code = parser.cython_export()
            self.synapse_exports[name] = code

            # Cython wrapper
            code = parser.cython_wrapper()
            self.synapse_wrappers[name] = code

    def generate_header(self):
        """Generates ANNarchy.hpp

        Sets:

            self.annarchy_h

        """

        neuron_includes = ""
        for name in self.neuron_classes.keys():
            neuron_includes += Template('#include "$name.hpp"\n').substitute(name=name)

        synapse_includes = ""
        for name in self.synapse_classes.keys():
            synapse_includes += Template('#include "$name.hpp"\n').substitute(name=name)


        # Generate ANNarchy.h
        self.annarchy_h = Template("""#pragma once

#include <string>
#include <vector>
#include <algorithm>
#include <map>
#include <deque>
#include <queue>
#include <iostream>
#include <sstream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string.h>
#include <cmath>
#include <random>

// Network
#include "Network.hpp"

// Neuron definitions
$neuron_includes

// Synapse definitions
$synapse_includes
""").substitute(
            neuron_includes = neuron_includes,
            synapse_includes = synapse_includes,
        )

    def generate_network(self):
        """
        Generates the C++ Network class.
        """

        self.network_h = """#pragma once

#include "ANNarchy.hpp"

class Network {
    public:

    Network(double dt, long int seed){
        this->dt = dt;
        this->t = 0.0;
        this->seed = seed;

        this->setSeed(this->seed);
    };

    // Sets the seed for the rng
    void setSeed(long int seed){
        if(seed==-1){
            this->rng = std::mt19937(time(NULL));
        }
        else{
            this->rng = std::mt19937(seed);
        }
    };

    // Attributes
    double t;
    double dt;
    long int seed;
    std::mt19937 rng;
};
"""

    def generate_makefile(self):
        """Generates a Makefile.
        """

        # Python version
        python_version = "%(major)s.%(minor)s" % {'major': sys.version_info[0],
                                              'minor': sys.version_info[1]}

        # Include path to Numpy is not standard on all distributions
        numpy_include = np.get_include()

        makefile = Template("""# Makefile generated by ANNarchy
all:
\tcython3 -3 --cplus ANNarchyCore.pyx 
\tg++ -march=native -O3 -shared -fPIC -fpermissive -std=c++11 \\
\t\t`/usr/bin/python3-config --includes` \\
\t\t-I$numpy_include \\
\t\t*.cpp -o ANNarchyCore.so \\
\t\t-lpython$python_version \\
\t\t-L/usr/lib 

clean:
\trm -rf *.o
\trm -rf *.so
""")
        self.makefile = makefile.substitute(
            numpy_include = numpy_include,
            python_version = python_version,
        )

    def generate_cython(self):
        """Generates Cython bindings.

        """

        # Export from C++ : Neuron
        neuron_export = ""
        for _, code in self.neuron_exports.items():
            neuron_export += code

        # Export from C++ : Synapse
        synapse_export = ""
        for _, code in self.synapse_exports.items():
            synapse_export += code

        self.cython_bindings = Template("""# distutils: language = c++
from libcpp.vector cimport vector

cdef extern from "ANNarchy.hpp":

    # Network
    cdef cppclass Network :
        # Constructor
        Network(double, long) except +        
        # t
        double t
        # dt
        double dt

$neuron_export
$synapse_export

""").substitute(
            neuron_export=neuron_export,
            synapse_export=synapse_export,
        )

        # Neurons
        neuron_wrapper = ""
        population_creator = ""
        neuron_imports = ""

        for name, code in self.neuron_wrappers.items():
            # Wrapper
            neuron_wrapper += code
            
            # Population creator
            population_creator += Template("""
    def _add_$name(self, int size):

        pop = py$name(self, size)
        self.populations.append(pop)""").substitute(
            name=name,
        )
            # Imports
            neuron_imports += Template("""
from ANNarchyBindings cimport $name""").substitute(name=name)

        # Synapses
        synapse_wrapper = ""
        projection_creator = ""
        synapse_imports = ""

        for name, code in self.synapse_wrappers.items():
            # Wrapper
            synapse_wrapper += code
            
            # Projection creator
            projection_creator += Template("""
    def _add_$name(self):

        proj = Init_$name(self.instance, self.populations[0], self.populations[0])
        self.projections.append(proj)
        """).substitute(
            name=name,
        )
            # Imports
            synapse_imports += Template("""
from ANNarchyBindings cimport $name""").substitute(name=name)


        # Main template
        self.cython_network = Template("""# distutils: language = c++
cimport cython
from libcpp.vector cimport vector
cimport numpy as np
import numpy as np

# Imports
from ANNarchyBindings cimport Network
$neuron_imports
$synapse_imports

# Wrappers
$neuron_wrapper
$synapse_wrapper

# Main Python network
cdef class pyNetwork(object):

    cdef list populations
    cdef list projections

    cdef Network* instance

    def __cinit__(self, double dt, long seed):

        self.instance = new Network(dt, seed)

        self.populations = []
        self.projections = []

    def __dealloc__(self):
        # TODO
        del self.populations[0]
        del self.projections[0]

    property t:
        "Current time (ms)."
        def __get__(self):
            return self.instance.t
        def __set__(self, double value):
            self.instance.t = value

    property dt:
        "Step size (ms)."
        def __get__(self):
            return self.instance.dt
        def __set__(self, double value):
            self.instance.dt = value

    def population(self, int idx):
        return self.populations[idx]

    @cython.boundscheck(False) # turn off bounds-checking for entire function
    @cython.wraparound(False)  # turn off negative index wrapping for entire function
    def step(self):
        # RNG
        for pop in self.populations:
            pop.rng()
        # Neural updates
        for pop in self.populations:
            pop.update()
        # Spike emission
        for pop in self.populations:
            pop.spike()
        # Reset
        for pop in self.populations:
            pop.reset()

$population_creator
$projection_creator

""").substitute(
    neuron_wrapper = neuron_wrapper,
    population_creator = population_creator,
    neuron_imports = neuron_imports,
    synapse_wrapper = synapse_wrapper,
    projection_creator = projection_creator,
    synapse_imports = synapse_imports,
)