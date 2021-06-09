#pragma once

#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <iostream>

template<typename INT_t, typename FLOAT_t>
class cLIL {
    public:

    cLIL(INT_t nb_post, INT_t nb_pre) : nb_post(nb_post), nb_pre(nb_pre) {

        this->nnz = 0;

        this->values = std::vector<std::map<INT_t, FLOAT_t>>(this->nb_post, std::map<INT_t, FLOAT_t>());

    };

    // Attributes
    INT_t nb_post;
    INT_t nb_pre;

    size_t nnz;

    std::vector<std::map<INT_t, FLOAT_t>> values;

    cLIL transpose(){

        cLIL res = new cLIL(this->nb_pre, this->nb_post);

        // TODO: tranpose

        return res;
    }

    // Add a single element
    void add_single(INT_t rk_post, INT_t rk_pre, FLOAT_t val){

        // Increment the number of non-zeros
        this->nnz++;
        
        // Insert at the right place
        this->values[rk_post][rk_pre] = val;
    };


    // Add elements in a row, with a single value
    void add_row_single(INT_t rk_post, std::vector<INT_t> rks_pre, FLOAT_t val){

        // Increment the number of non-zeros
        this->nnz += rks_pre.size();
        
        // Insert at the right place
        for (const auto& rk_pre : rks_pre) {
            this->values[rk_post][rk_pre] = val;
        }
    };

    // Add elements in a row, with different values
    void add_row_multiple(INT_t rk_post, std::vector<INT_t> rks_pre, std::vector<FLOAT_t> val){

        // Increment the number of non-zeros
        this->nnz += rks_pre.size();
        
        // Insert at the right place
        for (size_t i=0; i < rks_pre.size(); i++) {
            this->values[rk_post][rks_pre[i]] = val[i];
        }
    };

    // Add elements in a column, with a single value
    void add_column_single(std::vector<INT_t> rks_post, INT_t rk_pre, FLOAT_t val){

        // Increment the number of non-zeros
        this->nnz += rks_post.size();
        
        // Insert at the right place
        for (const auto& rk_post : rks_post) {
            this->values[rk_post][rk_pre] = val;
        }
    };

    // Add elements in a column, with different values
    void add_column_multiple(std::vector<INT_t> rks_post, INT_t rk_pre, std::vector<FLOAT_t> val){

        // Increment the number of non-zeros
        this->nnz += rks_post.size();
        
        // Insert at the right place
        for (size_t i=0; i < rks_post.size(); i++) {
            this->values[rks_post[i]][rk_pre] = val[i];
        }
    };

    // Add elements in a block, with a single value
    void add_block_single(std::vector<INT_t> rks_post, std::vector<INT_t> rks_pre, FLOAT_t val){

        // Increment the number of non-zeros
        this->nnz += rks_pre.size() * rks_post.size();
        
        // Insert at the right place
        for (size_t i=0; i < rks_post.size(); i++) {
            for (size_t j=0; j < rks_pre.size(); j++) {
                this->values[rks_post[i]][rks_pre[j]] = val;
            }
        }
    };

    // Add elements in a block, with different values
    void add_block_multiple(std::vector<INT_t> rks_post, std::vector<INT_t> rks_pre, std::vector<std::vector<FLOAT_t>> val){

        // Increment the number of non-zeros
        this->nnz += rks_pre.size() * rks_post.size();
        
        // Insert at the right place
        for (size_t i=0; i < rks_post.size(); i++) {
            for (size_t j=0; j < rks_pre.size(); j++) {
                this->values[rks_post[i]][rks_pre[j]] = val[i][j];
            }
        }
    };

    std::string print(){

        std::ostringstream stream;

        stream << "Shape: (" << this->nb_post << ", " << this->nb_pre << ")" << std::endl;

        stream << "Non-zeros: " << this->nnz << std::endl;

        for(size_t rk_post=0; rk_post < this->nb_post; rk_post++){
            for (const auto& [rk_pre, value] : this->values[rk_post]) {
                stream << "(" << rk_post << ", " << rk_pre << ") = " << value << std::endl;
            }
        }

        return stream.str();
    };

    std::vector<std::vector<FLOAT_t>> to_array(){
        std::vector<std::vector<FLOAT_t>> res = std::vector<std::vector<FLOAT_t>>(
            this->nb_post, 
            std::vector<FLOAT_t>(this->nb_pre, 0.0));

        for(size_t rk_post=0; rk_post < nb_post; rk_post++){
            for (const auto& [rk_pre, value] : this->values[rk_post]) {
                res[rk_post][rk_pre] = value;
            }
        }

        return res;
    };

};