#pragma once

#include "ANNarchy.h"

class Network;

class $class_name {
    public:

    $class_name(Network* net, int size);

    // Network
    Network* net;

    // Size of the population
    int size;

    // Attributes
$declared_attributes
$declared_spiking
$declared_rng

    // Update RNG method
    void rng();

    // Update method
    void update();

    // Spike emission
    void spike();

    // Reset after spike
    void reset();

};