import sys
import logging
from string import Template

import sympy as sp

from ANNarchy_future.parser.CodeGeneration import code_generation
from ANNarchy_future.parser.NeuronParser import NeuronParser


class PopulationGenerator(object):


    def __init__(self, name:str, parser:NeuronParser):
        
        self.name:str = name
        self.parser:NeuronParser = parser

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

    def generate(self):

        # Hack: get the template
        tpl = __file__.replace('PopulationGenerator.py', 'Population.h')

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
    std::vector<int> spike;"""
            initialize_spiking = """
        // Spiking neuron
        this->spike = std::vector<int>(0)"""
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
                        rhs = code_generation(eq['rhs'], self.correspondences),
                        hr = eq['human-readable']
                    )
                else:
                    code += tpl_eq.substitute(
                        lhs = eq['name'] if eq['name'] in self.parser.shared else eq['name'] + "[i]",
                        op = eq['op'],
                        rhs = code_generation(eq['rhs'], self.correspondences),
                        hr = eq['human-readable']
                    )

        return tlp_block.substitute(update=code)

    def spike(self) -> str:

        tpl_spike = Template("""
    // Spike emission
    void spike(){
        for(unsigned int i = 0; i< this->size; i++){
            if ($condition){
                this->spike.push_back(i);
            }
        }
    }
        """)

        cond = code_generation(self.parser.spike_condition.equation['eq'], self.correspondences)

        return tpl_spike.substitute(condition=cond)

    def reset(self) -> str:

        tpl_reset = Template("""
    // Reset
    void reset(){
        for(unsigned int idx = 0; idx< this->spike.size(); idx++){
            int i = this->spike[idx];
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
                    rhs = code_generation(eq['rhs'], self.correspondences),
                    hr = eq['human-readable']
                )

        return tpl_reset.substitute(reset=code)