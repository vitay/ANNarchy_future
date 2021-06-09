#pragma once

#include "ANNarchy.hpp"

class Network;

template<typename PrePopulation, typename PostPopulation>
class cppSynapse_$class_name {
    public:

    cppSynapse_$class_name(Network* net, PrePopulation* pre, PostPopulation* post){

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

    // Collect inputs (weighted sum or spike transmission)
    void collect_inputs(){
$collect_inputs_method
    };

    // Update method
    void update(){
$update_method
    };

};