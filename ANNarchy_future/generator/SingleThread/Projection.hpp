#pragma once

#include "ANNarchy.hpp"

class Network;

template<typename PrePopulation, typename PostPopulation>
class $class_name {
    public:

    $class_name(Network* net, PrePopulation* pre, PostPopulation* post){

        this->net = net;

        this->post = post;
        this->pre = pre;

        // Initialize arrays
$initialize_arrays
    };

    // Network
    Network* net;

    // Populations
    PrePopulation* pre;
    PostPopulation* post;

    // Attributes
$declared_attributes

    // Update method
    void update(){
$update_method
    };

};