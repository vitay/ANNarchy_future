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
            't': 'this->t',
            'dt': 'this->dt',
        }
        for attr in self.parser.attributes:
            if attr in self.parser.shared:
                self.correspondences[attr] = "this->" + attr
            else:
                self.correspondences[attr] = "this->" + attr + "[i]"

    def generate(self) -> str:
        
        """Generates the C++ code. 

        Calls:

            `self.update()`
            `self.spike()`
            `self.reset()`
        
        Returns:
        
            a multiline string for the .h header file.
        """

        # Get the template
        tpl = str(ANNarchy_future.__path__[0]) +  '/generator/SingleThread/Population.h'

        # Open the template
        with open(tpl, 'r') as f:
            template = f.readlines()
        template = Template("".join(template))

        # Initialize arrays
        initialize_arrays = ""

        # Parameters
        declared_parameters = ""
        for attr in self.parser.parameters:
            if attr in self.parser.shared:
                declared_parameters += Template(
                    "    double $attr;\n").substitute(attr=attr)
            else:
                declared_parameters += Template(
                    "    std::vector<double> $attr;\n").substitute(attr=attr)
                initialize_arrays += Template(
                    "        this->$attr = std::vector<double>(size, 0.0);\n").substitute(attr=attr)

        # Variables
        declared_variables = ""
        for attr in self.parser.variables:
            if attr in self.parser.shared:
                declared_variables += Template(
                    "    double $attr;\n").substitute(attr=attr)
            else:
                declared_variables += Template(
                    "    std::vector<double> $attr;\n").substitute(attr=attr)
                initialize_arrays += Template(
                    "        this->$attr = std::vector<double>(size, 0.0);\n").substitute(attr=attr)

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
        code = template.substitute(
            class_name = self.name,
            initialize_arrays = initialize_arrays,
            initialize_spiking = initialize_spiking,
            declared_parameters = declared_parameters,
            declared_variables = declared_variables,
            declared_spiking = declared_spiking,
            update_method = update_method,
            spike_method = spike_method,  
            reset_method = reset_method,  
        )
        
        return code

    def update(self) -> str:

        """Processes the Neuron.update() field.
        
        Returns:

            the content of the `update()` C++ method.

        """

        # Block template
        tlp_block = Template("""
        for(unsigned int i = 0; i< this->size; i++){
$update
        }""")

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
                        lhs = eq['name'] if eq['name'] in self.parser.shared else eq['name'] + "[i]",
                        op = eq['op'],
                        rhs = parser.code_generation(eq['rhs'], self.correspondences),
                        hr = eq['human-readable']
                    )

        return tlp_block.substitute(update=code)

    def spike(self) -> str:

        """Processes the Neuron.spike() field.
        
        Returns:

            the whole `spike()` C++ method.

        """

        tpl_spike = Template("""
    // Spike emission
    void spike(){
        for(unsigned int i = 0; i< this->size; i++){
            if ($condition){
                this->spikes.push_back(i);
            }
        }
    }
        """)

        cond = parser.code_generation(self.parser.spike_condition.equation['eq'], self.correspondences)

        return tpl_spike.substitute(condition=cond)

    def reset(self) -> str:

        """Processes the Neuron.reset() field.
        
        Returns:

            the whole `reset()` C++ method.

        """

        tpl_reset = Template("""
    // Reset
    void reset(){
        for(unsigned int idx = 0; idx< this->spikes.size(); idx++){
            int i = this->spikes[idx];
$reset
        }
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
                    lhs = eq['name'] if eq['name'] in self.parser.shared else eq['name'] + "[i]",
                    op = eq['op'],
                    rhs = parser.code_generation(eq['rhs'], self.correspondences),
                    hr = eq['human-readable']
                )

        return tpl_reset.substitute(reset=code)


    def cython_export(self):
        """Generates declaration of the C++ class for Cython.

        """
        
        # Parameters
        parameters = ""
        for attr in self.parser.parameters:
            if attr in self.parser.shared:
                parameters += Template(
                    "        double $attr\n").substitute(attr=attr)
            else:
                parameters += Template(
                    "        vector[double] $attr\n").substitute(attr=attr)

        # Variables
        variables = ""
        for attr in self.parser.variables:
            if attr in self.parser.shared:
                variables += Template(
                    "        double $attr\n").substitute(attr=attr)
            else:
                variables += Template(
                    "        vector[double] $attr\n").substitute(attr=attr)


        code = Template("""
    # $name
    cdef cppclass $name :
        # Constructor
        $name(int, double) except +
        # Number of neurons
        int size
        # Neural equations
        void update()
        # Reset the population
        void reset()
        # Parameters
$parameters
        # Variables
$variables
""").substitute(
        name=self.name,
        parameters=parameters,
        variables=variables,
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
        
        # Parameters
        parameters = ""
        for attr in self.parser.parameters:
            if attr in self.parser.shared:
                parameters += tpl_shared.substitute(attr=attr)
            else:
                parameters += tpl.substitute(attr=attr)

        # Variables
        variables = ""
        for attr in self.parser.variables:
            if attr in self.parser.shared:
                variables += tpl_shared.substitute(attr=attr)
            else:
                variables += tpl.substitute(attr=attr)



        code = Template("""
cdef class py$name(object):

    cdef $name* instance

    def __cinit__(self, int size, double dt):
        self.instance = new $name(size, dt)

    def update(self):
        self.instance.update()

    property size:
        def __get__(self):
            return self.instance.size
        def __set__(self, int value): 
            self.instance.size = value
            
$parameters
$variables
""")
        return code.substitute(
            name=self.name,
            parameters=parameters,
            variables=variables,
        )