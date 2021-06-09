import sys
import logging
from string import Template

import numpy as np

import ANNarchy_future.generator as generator


class SingleThreadGenerator(object):

    """Generates the C++ code for single-threaded simulation.

    """

    def __init__(self, compiler:'generator.Compiler', description:dict, backend:str, library:str):

        """
        Args:

            compiler: Compiler instance.
            description: dictionary passed by `Network`.
            backend: 'single', 'openmp', 'cuda' or 'mpi'.
            library: name of .so library.
        """
        
        self.compiler = compiler
        self.description:dict = description
        self.backend = backend
        self.library = library

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

        # Generate Network.hpp and Network.cpp
        self.generate_network()

        # Generate ANNarchyBindings.pxd
        self.generate_cython_bindings()

        # Generate ANNarchyCore.pyx
        self.generate_cython_wrapper()

        # Generate Makefile
        self.generate_makefile()



    def copy_files(self):
        """
        Puts the files in the compilation folder.
        """

        # Makefile
        self.compiler.write_file("Makefile", self.makefile)

        # ANNarchy.h
        self.compiler.write_file("ANNarchy.hpp", self.annarchy_h)

        # Network.h
        self.compiler.write_file("Network.hpp", self.network_h)

        # ANNarchyBindings.pxd
        self.compiler.write_file("ANNarchyBindings.pxd", self.cython_bindings)

        # ANNarchyCore.pyx
        self.compiler.write_file("ANNarchyCore.pyx", self.cython_network)

        # Neuron classes
        for name, code in  self.neuron_classes.items():
            self.compiler.write_file("cppNeuron_"+name+".hpp", code)

        # Synapse classes
        for name, code in  self.synapse_classes.items():
            self.compiler.write_file("cppSynapse_"+name+".hpp", code)

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
            neuron_includes += Template('#include "cppNeuron_$name.hpp"\n').substitute(name=name)

        synapse_includes = ""
        for name in self.synapse_classes.keys():
            synapse_includes += Template('#include "cppSynapse_$name.hpp"\n').substitute(name=name)


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
\tcython3 -3 --cplus *.pyx 
\tg++ -march=native -O3 -shared -fPIC -fpermissive -fopenmp -std=c++17 \\
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

    def generate_cython_bindings(self):
        """
        Generates Cython bindings to be put in ANNarchyBindings.pxd

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

    def generate_cython_wrapper(self):
        """
        Generates Cython wrappers to be put in ANNarchyCore.pyx

        """
        #######################
        # Neurons
        #######################
        neuron_wrapper = ""
        population_creator = ""
        neuron_imports = ""

        for name, code in self.neuron_wrappers.items():
            # Wrapper
            neuron_wrapper += code
            
            # Population creator
            population_creator += Template("""
    def _add_$name(self, int size):

        pop = pyNeuron_$name(self, size)
        self.populations.append(pop)
        self.nb_populations += 1
        
        """).substitute(
            name=name,
        )
            # Imports
            neuron_imports += Template("""
from ANNarchyBindings cimport cppNeuron_$name""").substitute(name=name)

        #######################
        # Synapses
        #######################
        synapse_imports = ""


        for name, code in self.synapse_wrappers.items():
            # Imports
            synapse_imports += Template("""
from ANNarchyBindings cimport cppSynapse_$name""").substitute(name=name)


        #######################
        # Projections
        #######################
        projection_wrapper = ""
        projection_creator = ""
        for name, pre, post in self.description['projection_types']:
            # Wrapper
            projection_wrapper += Template(code).substitute(
                pre = pre,
                post = post,
            )
            
            # Projection creator
            projection_creator += Template("""
    def _add_${name}_${pre}_${post}(self, id_pre, id_post):

        proj = pySynapse_${name}_${pre}_${post}(self, self.populations[id_pre], self.populations[id_post])

        self.projections.append(proj)
        self.nb_projections += 1
        """).substitute(
            name = name,
            pre = pre,
            post = post,
        )

        #######################
        # Main template
        #######################

        # Get the ANNarchyCore.pyx template        
        template = generator.fetch_template('/generator/SingleThread/templates/ANNarchyCore.pyx')


        self.cython_network = template.substitute(
    neuron_wrapper = neuron_wrapper,
    population_creator = population_creator,
    neuron_imports = neuron_imports,
    synapse_imports = synapse_imports,
    projection_wrapper = projection_wrapper,
    projection_creator = projection_creator,
)