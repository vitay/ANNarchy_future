#pragma once

#include "ANNarchy.h"

class $class_name {
    public:

    $class_name(int size, double dt){
        this->size = size;
        this->dt = dt;

        // Initialize arrays
$initialize_arrays

$initialize_spiking
    };

    // Size of the population
    int size;
    double dt;

    // Declared parameters
$declared_parameters

    // Declared variables
$declared_variables

$declared_spiking

    // Update method
    void update(){
$update_method
    };

$spike_method
$reset_method

};