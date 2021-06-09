#pragma once

#include "ANNarchy.hpp"

class Network;

class cppNeuron_$class_name {
    public:

    cppNeuron_$class_name(Network* net, int size){

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

    // Reset inputs method
    void reset_inputs(){
$reset_inputs
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