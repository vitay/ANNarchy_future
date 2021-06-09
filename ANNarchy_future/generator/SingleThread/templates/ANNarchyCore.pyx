# distutils: language = c++
cimport cython
from libcpp.vector cimport vector
cimport numpy as np
import numpy as np

###########################################
# Imports
###########################################
from ANNarchyBindings cimport Network
$neuron_imports
$synapse_imports

###########################################
# Population wrappers
###########################################
$neuron_wrapper

###########################################
# Projection wrappers
###########################################
$projection_wrapper

###########################################
# Monitors
###########################################
# TODO

###########################################
# Main Python network
###########################################
cdef class pyNetwork(object):

    cdef size_t nb_populations
    cdef list populations
    cdef size_t nb_projections
    cdef list projections
    
    cdef list monitors
    cdef list recorded


    cdef Network* instance

    def __cinit__(self, double dt, long seed):

        self.instance = new Network(dt, seed)

        self.populations = []
        self.nb_populations = 0
        self.projections = []
        self.nb_projections = 0

        self.monitors = []
        self.recorded = []

    def __dealloc__(self):
        # TODO
        for pop in self.populations:
            del pop
        for proj in self.projections:
            del proj

    #########################################
    # Access
    #########################################
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

    def projection(self, int idx):
        return self.projections[idx]

    #########################################
    # Simulation
    #########################################

    @cython.boundscheck(False) # turn off bounds-checking for entire function
    @cython.wraparound(False)  # turn off negative index wrapping for entire function
    def step(self):
        # RNG
        for pop in self.populations:
            pop.rng()

        # Reset conductances
        for pop in self.populations:
            pop.reset_inputs()


        # Update conductances
        for proj in self.projections:
            proj.collect_inputs()

        # Neural updates
        for pop in self.populations:
            pop.update()

        # Spike emission
        for pop in self.populations:
            pop.spike()

        # Reset
        for pop in self.populations:
            pop.reset()

        # Synaptic updates
        for proj in self.projections:
            proj.update()

        # Monitor
        self.record()


    @cython.boundscheck(False) # turn off bounds-checking for entire function
    @cython.wraparound(False)  # turn off negative index wrapping for entire function
    def simulate(self, int duration):

        cdef size_t i

        for i in range(duration):
            self.step()

    #########################################
    # Monitoring
    #########################################

    def monitor(self, monitors):

        self.monitors = monitors

        self.recorded = []

        self.clear_monitored()

    @cython.boundscheck(False) # turn off bounds-checking for entire function
    @cython.wraparound(False)  # turn off negative index wrapping for entire function
    cdef record(self):

        cdef size_t nb = len(self.monitors)
        cdef size_t i = 0

        for i in range(nb):
            self.recorded[i].append(self.populations[i].r)

    def get_monitored(self):

        return self.recorded

    def clear_monitored(self):

        self.recorded

        cdef size_t i = 0
        cdef size_t nb = len(self.monitors)

        for i in range(nb):
            self.recorded.append([])

    #########################################
    # Object management
    #########################################

$population_creator
$projection_creator