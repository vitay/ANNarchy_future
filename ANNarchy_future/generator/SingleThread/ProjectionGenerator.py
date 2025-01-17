import sys
import logging
from string import Template

import sympy as sp

import ANNarchy_future.parser as parser
import ANNarchy_future.generator as generator


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

        self.correspondences = self.get_correspondences()

    def get_correspondences(self):

        # Build a correspondance dictionary
        correspondences = {
            't': 'this->t',
            'dt': 'this->dt',
        }

        for attr in self.parser.attributes:
            if attr in self.parser.shared:
                correspondences[attr] = "this->" + attr
            else:
                correspondences[attr] = "this->" + attr + "[i][j]"

        for attr in self.parser.synapse.pre_attributes:
            if attr in self.parser.pre._parser.shared:
                correspondences["pre."+attr] = "this->pre->" + attr
            else:
                correspondences["pre."+attr] = "this->pre->" + attr + "[i]"

        for attr in self.parser.synapse.post_attributes:
            if attr in self.parser.post._parser.shared:
                correspondences["post."+attr] = "this->post->" + attr
            else:
                correspondences["post."+attr] = "this->post->" + attr + "[j]"

        return correspondences


    def generate(self) -> str:

        """Generates the C++ code. 

        Calls:

            `self.update()`
        
        Returns:
        
            a multiline string for the .h header file and .cpp body file.
        """

        # Get the Projection.hpp template
        template_h = generator.fetch_template('/generator/SingleThread/templates/Projection.hpp')

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
                    "    std::vector< std::vector<double> > $attr;\n").substitute(attr=attr)
                initialize_arrays += Template("""
        this->$attr = std::vector< std::vector<double> >(this->post->size, std::vector<double>(this->pre->size, 0.0));
                """).substitute(attr=attr) # TODO

        # Update method
        update_method = self.update()

        # Weighted sum or spike transmission
        collect_inputs_method = self.collect_inputs()


        # Generate code
        code = template_h.substitute(
            class_name = self.name,
            declared_attributes = declared_attributes,
            initialize_arrays = initialize_arrays,
            update_method = update_method,
            collect_inputs_method = collect_inputs_method,
        )
        
        return code

    def update(self) -> str:

        """Processes the Synapse.update() field.
        
        Returns:

            the content of the `update()` C++ method.

        """
        # Block template
        tlp_block = Template("""
        for(unsigned int i = 0; i< this->post->size; i++){
            for(unsigned int j = 0; i< this->pre->size; i++){
$update
            }
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
                        lhs = "this->"+eq['name'] if eq['name'] in self.parser.shared 
                                else "this->"+eq['name'] + "[i][j]",
                        op = eq['op'],
                        rhs = parser.code_generation(eq['rhs'], self.correspondences),
                        hr = eq['human-readable']
                    )

        return tlp_block.substitute(update=code)

    def collect_inputs(self) -> str:

        code = """
        std::vector<double> res = std::vector<double>(this->post->size, 0.0);

        for(unsigned int i=0; i<this->post->size; i++){
            res[i] = this->pre->r[i];
        }

        this->post->ge = res; 
        """

        return code

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
                    "        vector[vector[double]] $attr\n").substitute(attr=attr)


        code = Template("""
    # $name synapse
    cdef cppclass cppSynapse_$name[PrePopulation, PostPopulation] :
        # Constructor
        cppSynapse_$name(Network*, PrePopulation*, PostPopulation*) except +

        # Methods
        void collect_inputs()
        void update()

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
        def __set__(self, vector[vector[double]] value): 
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

# $name synapse, pre = $pre, post = $post
cdef class pySynapse_${name}_${pre}_${post}(object):

    cdef cppSynapse_${name}[cppNeuron_${pre}, cppNeuron_${post}] *instance

    def __cinit__(self, pyNetwork net, pyNeuron_$pre pre, pyNeuron_$post post):
        
        self.instance = new cppSynapse_$name[cppNeuron_${pre}, cppNeuron_${post}](net.instance, pre.instance, post.instance)

    def __dealloc__(self):
        del self.instance  

    # Methods
    def update(self):
        self.instance.update()

    def collect_inputs(self):
        self.instance.collect_inputs()

    # Attributes      
$attributes

""")
        return code.substitute(
            name=self.name,
            attributes=attributes,
            pre="${pre}",
            post="${post}",
        )