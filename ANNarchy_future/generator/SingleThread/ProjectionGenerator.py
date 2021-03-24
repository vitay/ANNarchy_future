import sys
import logging
from string import Template

import sympy as sp

import ANNarchy_future
import ANNarchy_future.parser as parser


class ProjectionGenerator(object):

    """Generates a C++ file corresponding to a Synapse description.

    Attributes:

        name: name of the class.
        parser: instance of SynapseParser.
        correspondences: dictionary of pairs (symbol -> implementation).

    """


    def __init__(self, 
        name : str, 
        parser : 'parser.SynapseParser'):

        """
        Args:

            name (str): name of the class.
            parser (parser.SynapseParser): parser for the synapse.
        """
        
        self.name:str = name
        self.parser:'parser.SynapseParser' = parser

        # Build a correspondance dictionary
        self.correspondences = {
            't': 'this->t',
            'dt': 'this->dt',
        }

        for attr in self.parser.attributes:
            if attr in self.parser.shared:
                self.correspondences[attr] = "this->" + attr
            else:
                self.correspondences[attr] = "this->" + attr + "[i][j]"

        for attr in self.parser.synapse.pre_attributes:
            if attr in self.parser.pre._parser.shared:
                self.correspondences["pre."+attr] = "this->pre->" + attr
            else:
                self.correspondences["pre."+attr] = "this->pre->" + attr + "[i]"

        for attr in self.parser.synapse.post_attributes:
            if attr in self.parser.post._parser.shared:
                self.correspondences["post."+attr] = "this->post->" + attr
            else:
                self.correspondences["post."+attr] = "this->post->" + attr + "[j]"

    def generate(self) -> str:

        """Generates the C++ code. 

        Calls:

            `self.update()`
        
        Returns:
        
            a multiline string for the .h header file.
        """

        # Get the template
        tpl = str(ANNarchy_future.__path__[0]) +  '/generator/SingleThread/Projection.h'

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


        # Generate code
        code = template.substitute(
            class_name = self.name,
            initialize_arrays = initialize_arrays,
            declared_parameters = declared_parameters,
            declared_variables = declared_variables,
            update_method = update_method,
        )
        
        return code

    def update(self) -> str:

        """Processes the Synapse.update() field.
        
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

