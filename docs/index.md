# ANNarchy

## About ANNarchy

ANNarchy (Artificial Neural Networks architect) is a neural simulator designed for distributed rate-coded or spiking neural networks. The core of the library is written in C++ and distributed using openMP, CUDA and MPI. It provides an interface in Python for the definition of the networks. It is released under the [GNU GPL v2 or later](http://www.gnu.org/licenses/gpl.html).

* Source code: <http://bitbucket.org/annarchy/annarchy>

* Documentation: <http://annarchy.readthedocs.io>

* Forum: <https://groups.google.com/forum/#!forum/annarchy>

* Bug reports: <https://bitbucket.org/annarchy/annarchy/issues>

**Citation**

If you use ANNarchy for your research, we would appreciate if you cite the following paper:

> Vitay J, Dinkelbach HÜ and Hamker FH (2015). ANNarchy: a code generation approach to neural simulations on parallel hardware. *Frontiers in Neuroinformatics* 9:19. <http://dx.doi.org/10.3389/fninf.2015.00019>


## Dependencies

ANNarchy can be used on any GNU/Linux system, as well as MacOS X.

## Installation

To install the latest stable release of ANNarchy, `pip` is recommended:

```bash
pip install ANNarchy
```

To install the latest developement release of ANNarchy, install it from source:

```bash
git clone http://bitbucket.org/annarchy/annarchy.git
cd annarchy/
python setup.py install
```