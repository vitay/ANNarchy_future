#pragma once

#include "ANNarchy.hpp"

class Network;

class $class_name {
    public:

    $class_name(Network* net, int size){

        this->net = net;

        this->size = size;

        // Initialize arrays
$initialize_arrays
$initialize_spiking
$initialize_rng
    };

    // Network
    Network* net;

    // Size of the population
    int size;

    // Attributes
$declared_attributes
$declared_spiking
$declared_rng

    // Update RNG method
    void rng(){
$rng_method
    };

    // Update method
    void update(){
$update_method
    };

    // Spike emission
    void spike(){
$spike_method
    };

    // Reset after spike
    void reset(){
$reset_method
    };

};