#!/usr/bin/env python

################################################
# Check if the required packages are installed
################################################
import sys, os, os.path, json, shutil
import subprocess
from pkg_resources import parse_version

# check python version
if not sys.version_info[:2] >= (3, 7):
    print('Error : ANNarchy requires at least Python 3.7.')
    exit(0)

# setuptools
try:
    from setuptools import setup, find_packages, Extension
    print('Checking for setuptools... OK')
except:
    print('Checking for setuptools... NO')
    print('Error : Python package "setuptools" is required.')
    print('You can install it from pip or: http://pypi.python.org/pypi/setuptools')
    exit(0)

dependencies = [
    'numpy',
    'scipy',
    'matplotlib',
    'cython',
    'sympy'
]

package_data = []

release = '5.0.0b'
print("Installing ANNarchy", release)

with open("README.md", 'r') as f:
    long_description = f.read()

setup(  name='ANNarchy_future',
        version=release,
        download_url = 'https://bitbucket.org/annarchy/annarchy',
        license='GPLv2+',
        platforms='GNU/Linux; MacOSX',
        description='Artificial Neural Networks architect',
        long_description=long_description,
        author='Julien Vitay, Helge Uelo Dinkelbach and Fred Hamker',
        author_email='julien.vitay@informatik.tu-chemnitz.de',
        url='http://www.tu-chemnitz.de/informatik/KI/projects/ANNarchy/index.php',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
            'Operating System :: POSIX :: Linux',
            'Operating System :: MacOS :: MacOS X',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Scientific/Engineering :: Artificial Intelligence'
        ],
        keywords='neural simulator',
        packages=find_packages(),
        package_data={'ANNarchy_future': package_data},
        install_requires=dependencies,
        #ext_modules = cythonize(extensions, language_level=int(sys.version_info[0])),
        #include_dirs = [np.get_include()],
        zip_safe = False
)
