# distutils: language = c++
cimport cython
from libcpp.vector cimport vector
from libcpp.string cimport string

import numpy as np
INT_TYPES = (int, np.integer)
FLOAT_TYPES = (float, np.floating)

###########################################
# Imports
###########################################
cdef extern from "LIL.hpp":


    # Network
    cdef cppclass cLIL[INT_t, FLOAT_t] :
        # Constructor
        cLIL(unsigned int, unsigned int) except +

        # Attributes
        unsigned int nb_post
        unsigned int nb_pre   
        unsigned int nnz  

        # Access
        void add_single(unsigned int rk_post, unsigned int rk_pre, FLOAT_t val)
        void add_row_single(unsigned int rk_post, vector[unsigned int] rk_pre, FLOAT_t val)
        void add_row_multiple(unsigned int rk_post, vector[unsigned int] rk_pre, vector[FLOAT_t] val)
        void add_column_single(vector[unsigned int] rk_post, unsigned int rk_pre, FLOAT_t val)
        void add_column_multiple(vector[unsigned int] rk_post, unsigned int rk_pre, vector[FLOAT_t] val)
        void add_block_single(vector[unsigned int] rk_post, vector[unsigned int] rk_pre, FLOAT_t val)
        void add_block_multiple(vector[unsigned int] rk_post, vector[unsigned int] rk_pre, vector[vector[FLOAT_t]] val)

        # Export
        string print()
        vector[vector[FLOAT_t]] to_array()

###########################################
# LIL
###########################################

cdef class LIL(object):

    cdef cLIL[unsigned int, double]* instance

    def __cinit__(self, tuple shape):
        
        self.instance = new cLIL[unsigned int, double](shape[0], shape[1])

    property shape:
        def __get__(self):
            return (self.instance.nb_post, self.instance.nb_pre)

    property nnz:
        def __get__(self):
            return self.instance.nnz
        
    def __setitem__(self, key, val):

        if not isinstance(key, tuple) or not len(key) == 2:
            print("Unable to index the matrix with", key)
            return

        # Simple renaming
        post = key[0]
        pre = key[1]
        
        # Simple [i, j]
        if isinstance(post, INT_TYPES) and isinstance(pre, INT_TYPES):

            val = float(val)
            self.instance.add_single(int(post), int(pre), val)

        # Horizontal slice [i, :]
        elif isinstance(post, INT_TYPES) and isinstance(pre, slice):

            pre_indices = self.iter_slices(pre, dim=1)
            
            nb_pre = len(pre_indices)

            if isinstance(val, FLOAT_TYPES):
                val = float(val)
                self.instance.add_row_single(int(post), list(pre_indices), val)

            elif isinstance(val, (list, np.ndarray)):
                try:
                    val = np.array(val).reshape(nb_pre)
                except:
                    print("The provided values of size", len(val), "do not match the shape of the slice", nb_pre)
                    return

                self.instance.add_row_multiple(int(post), list(pre_indices), val)
            
            
        
        # Vertical slice [:, j]
        elif isinstance(post, slice) and isinstance(pre, INT_TYPES):
            
            post_indices = self.iter_slices(post, dim=0)
            
            nb_post = len(post_indices)

            if isinstance(val, FLOAT_TYPES):
                val = float(val)
                self.instance.add_column_single(list(post_indices), int(pre), val)

            elif isinstance(val, (list, np.ndarray)):
                try:
                    val = np.array(val).reshape(nb_post)
                except:
                    print("The provided values of size", len(val), "do not match the shape of the slice", nb_post)
                    return

                self.instance.add_column_multiple(list(post_indices), int(pre), val)

        # Block slice [:, :]
        elif isinstance(post, slice) and isinstance(pre, slice):

            post_indices = self.iter_slices(post, dim=0)
            pre_indices = self.iter_slices(pre, dim=1)

            nb_post = len(post_indices)
            nb_pre = len(pre_indices)

            val = np.array(val)

            if val.size == 1:
                self.instance.add_block_single(post_indices, pre_indices, float(val))
            elif val.shape == (nb_post, nb_pre):
                self.instance.add_block_multiple(post_indices, pre_indices, val)
            else:
                print("The provided values of size", val.shape, "do not match the shape of the slice", (nb_post, nb_pre))
            

    def to_array(self):
        return np.array(self.instance.to_array())

    def __str__(self):
        return str(self.instance.print().decode('UTF-8'))


    def iter_slices(self, slice, dim):

        start = int(slice.start) if slice.start is not None else 0
        stop = int(slice.stop) if slice.stop is not None else self.shape[dim]
        step = int(slice.step) if slice.step is not None else 1

        return range(start, stop, step)


