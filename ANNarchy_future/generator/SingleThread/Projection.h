#pragma once

class $class_name {
    public:

    $class_name(int size, double dt){
        this->size = size;
        this->dt = dt;

        // Initialize arrays
$initialize_arrays
    };

    // Attributes
    double dt;

    // Declared parameters
$declared_parameters

    // Declared variables
$declared_variables

    // Update method
    void update(){
$update_method
    };

};