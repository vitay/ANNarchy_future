#include "$class_name.h"

$class_name::$class_name(Network* net, int size){

    this->net = net;

    this->size = size;

    // Initialize arrays
$initialize_arrays
$initialize_spiking
$initialize_rng
}


// Update RNG method
void $class_name::rng(){
$rng_method
}

// Update method
void $class_name::update(){
$update_method
}

// Spike emission
void $class_name::spike(){
$spike_method
}

// Reset after spike
void $class_name::reset(){
$reset_method
}