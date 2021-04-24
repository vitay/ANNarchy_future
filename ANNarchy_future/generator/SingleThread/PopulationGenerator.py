import sys
import logging
import importlib
from string import Template

import sympy as sp

import ANNarchy_future
import ANNarchy_future.parser as parser


class PopulationGenerator(object):

    """Generates a C++ file corresponding to a Neuron description.

    Attributes:

        name: name of the class.
        parser: instance of NeuronParser.
        correspondences: dictionary of pairs (symbol -> implementation).

    """

    def __init__(self, name:str, parser:'parser.NeuronParser'):
        
        """
        Args:

            name (str): name of the class.
            parser (parser.NeuronParser): parser for the neuron.
        """

        self.name:str = name
        self.parser:'parser.NeuronParser' = parser

        # Build a correspondance dictionary
        self.correspondences = {
            't': 'this->net->t',
            'dt': 'this->net->dt',
        }
        for attr in self.parser.attributes:
            if attr in self.parser.shared:
                self.correspondences[attr] = "this->" + attr
            else:
                self.correspondences[attr] = "this->" + attr + "[i]"
        
        for name, _ in self.parser.random_variables.items():
            self.correspondences[name] = "this->" + name + "[i]"

    def generate(self) -> str:
        
        """Generates the C++ code. 

        Calls:

            `self.rng()`
            `self.update()`
            `self.spike()`
            `self.reset()`
        
        Returns:
        
            a multiline string for the .h header file.
        """

        # Get the Population.h template
        tpl = str(ANNarchy_future.__path__[0]) +  '/generator/SingleThread/Population.hpp'
        with open(tpl, 'r') as f:
            template = f.readlines()
        template_h = Template("".join(template))

        # Initialize arrays
        initialize_arrays = ""

        # Attributes
        declared_attributes = ""
        for attr in self.parser.attributes:
            if attr in self.parser.shared:
                declared_attributes += Template(
                    "    double $attr;\n").substitute(attr=attr)
            else:
                declared_attributes += Template(
                    "    std::vector<double> $attr;\n").substitute(attr=attr)
                initialize_arrays += Template(
                    "        this->$attr = std::vector<double>(size, 0.0);\n").substitute(attr=attr)

        # RNG
        declared_rng, initialize_rng, rng_method = self.rng()


        # Update method
        update_method = self.update()

        # Spiking specifics
        initialize_spiking = ""
        declared_spiking = ""
        spike_method = ""
        reset_method = ""

        if self.parser.is_spiking():

            # Declare spike arrays
            declared_spiking = """
    // Spiking neuron
    std::vector<int> spikes;"""

            initialize_spiking = """
        // Spiking neuron
        this->spikes = std::vector<int>(0);"""

            # Spike method
            spike_method = self.spike()
        
            # Reset method
            reset_method = self.reset()



        # Generate code
        code = template_h.substitute(
            class_name = self.name,
            declared_attributes = declared_attributes,
            declared_spiking = declared_spiking,
            declared_rng = declared_rng,
            initialize_arrays = initialize_arrays,
            initialize_spiking = initialize_spiking,
            initialize_rng = initialize_rng,
            update_method = update_method,
            spike_method = spike_method,  
            reset_method = reset_method,  
            rng_method = rng_method, 
        )
        
        return code

    def rng(self) -> tuple:
        """Gathers all random variables.

        Returns:
            declared_rng, initialize_rng, rng_method
        """
        declared_rng = """
    // Random variables"""
        initialize_rng = """
        // Random Variables"""
        
        rng_tpl = Template("""
$init
        for(unsigned int i = 0; i < this->size; i++) {
$draw
        }
        """)
        rng_init = ""
        rng_update = ""

        for name, var in self.parser.random_variables.items():

            if isinstance(var, parser.RandomDistributions.Uniform):
                dist = "uniform_real_distribution< double >"
                # If the arguments are fixed throughout the simulation, no need to redraw 
                fixed = isinstance(var.min, (float, int)) and isinstance(var.max, (float, int))
                arg1 = parser.code_generation(var.min, self.correspondences)
                arg2 = parser.code_generation(var.max, self.correspondences)

            if isinstance(var, parser.RandomDistributions.Normal):
                dist = "normal_distribution< double >"
                # If the arguments are fixed throughout the simulation, no need to redraw 
                fixed = isinstance(var.mu, (float, int)) and isinstance(var.sigma, (float, int))
                arg1 = parser.code_generation(var.mu, self.correspondences)
                arg2 = parser.code_generation(var.sigma, self.correspondences)

            declared_rng += Template("""
    std::vector<double> $name;
    std::$dist dist$name;
            """).substitute(name=name, dist=dist)

            initialize_rng += Template("""
        this->$name = std::vector<double>(size, 0.0);
        this->dist$name = std::$dist($arg1, $arg2);
            """).substitute(name=name, dist=dist, arg1=arg1, arg2=arg2)

            if not fixed:
                rng_init += Template("""
        this->dist$name = std::$dist($arg1, $arg2);
            """).substitute(name=name, dist=dist, arg1=arg1, arg2=arg2)

            rng_update += Template("""
            this->$name[i] = this->dist$name(this->net->rng);
            """).substitute(name=name, dist=dist)

        rng_method = rng_tpl.substitute(init=rng_init, draw=rng_update)

        return declared_rng, initialize_rng, rng_method


    def update(self) -> str:

        """Processes the Neuron.update() field.
        
        Returns:

            the content of the `update()` C++ method.

        """

        # Block template
        tlp_block = Template("""
        for(unsigned int i = 0; i< this->size; i++){
$update
        }
        """)

        # Equation template
        tpl_eq = Template("""
            // $hr
            $lhs $op $rhs;
        """)

        # Iterate over all blocks of equations
        code = ""
        for block in self.parser.update_equations:
            for eq in block.equations:

                # Temporary variables
                if eq['type'] == 'tmp':
                    code += tpl_eq.substitute(
                        lhs = "double " + eq['name'],
                        op = eq['op'],
                        rhs = parser.code_generation(eq['rhs'], self.correspondences),
                        hr = eq['human-readable']
                    )
                else:
                    code += tpl_eq.substitute(
                        lhs = "this->"+eq['name'] if eq['name'] in self.parser.shared else "this->"+eq['name'] + "[i]",
                        op = eq['op'],
                        rhs = parser.code_generation(eq['rhs'], self.correspondences),
                        hr = eq['human-readable']
                    )

        return tlp_block.substitute(update=code)

    def spike(self) -> str:

        """Processes the Neuron.spike() field.
        
        Returns:

            the content of the `spike()` C++ method.

        """

        tpl_spike = Template("""
        this->spikes.clear();
        for(unsigned int i = 0; i< this->size; i++){
            if ($condition){
                this->spikes.push_back(i);
            }
        }
        """)

        cond = parser.code_generation(self.parser.spike_condition.equation['eq'], self.correspondences)

        return tpl_spike.substitute(condition=cond)

    def reset(self) -> str:

        """Processes the Neuron.reset() field.
        
        Returns:

            the content of the `reset()` C++ method.

        """

        tpl_reset = Template("""
        for(unsigned int idx = 0; idx< this->spikes.size(); idx++){
                int i = this->spikes[idx];
$reset
        }
        """)

        # Equation template
        tpl_eq = Template("""
            // $hr
            $lhs $op $rhs;
        """)

        # Iterate over all blocks of equations
        code = ""
        for block in self.parser.reset_equations:
            for eq in block.equations:
                code += tpl_eq.substitute(
                    lhs = "this->"+eq['name'] if eq['name'] in self.parser.shared else "this->"+eq['name'] + "[i]",
                    op = eq['op'],
                    rhs = parser.code_generation(eq['rhs'], self.correspondences),
                    hr = eq['human-readable']
                )

        return tpl_reset.substitute(reset=code)


    def cython_export(self):
        """Generates declaration of the C++ class for Cython.

        """
        
        # Parameters
        attributes = ""
        for attr in self.parser.attributes:
            if attr in self.parser.shared:
                attributes += Template(
                    "        double $attr\n").substitute(attr=attr)
            else:
                attributes += Template(
                    "        vector[double] $attr\n").substitute(attr=attr)


        code = Template("""
    # $name
    cdef cppclass $name :
        # Constructor
        $name(Network*, int) except +
        # Number of neurons
        int size
        # Methods
        void update()
        void spike()
        void reset()
        void rng()
        # Attributes
$attributes
""").substitute(
        name=self.name,
        attributes=attributes,
        )

        return code

    def cython_wrapper(self):

        tpl = Template("""
    property $attr:
        def __get__(self):
            return self.instance.$attr
        def __set__(self, vector[double] value): 
            self.instance.$attr = value
""")
       
        tpl_shared = Template("""
    property $attr:
        def __get__(self):
            return self.instance.$attr
        def __set__(self, double value): 
            self.instance.$attr = value
""")
        
        # Attributes
        attributes = ""
        for attr in self.parser.attributes:
            if attr in self.parser.shared:
                attributes += tpl_shared.substitute(attr=attr)
            else:
                attributes += tpl.substitute(attr=attr)

        code = Template("""
cdef class py$name(object):

    cdef $name* instance

    def __cinit__(self, pyNetwork net, int size):
        self.instance = new $name(net.instance, size)
    
    def __dealloc__(self):
        del self.instance

    property size:
        def __get__(self):
            return self.instance.size
        def __set__(self, int value): 
            self.instance.size = value

    # Methods
    def update(self):
        self.instance.update()
    def reset(self):
        self.instance.reset()
    def spike(self):
        self.instance.spike()
    def rng(self):
        self.instance.rng()
            
    # Attributes
$attributes
""")
        return code.substitute(
            name=self.name,
            attributes=attributes,
        )