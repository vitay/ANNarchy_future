# Overview

## Contributing

Some words on how to contribute on github.

## Style

Attributes and methods must be typed according to PEP 484:

```python
def method(a:int, b:float = 1.0) -> str:
    """Dummy method.
    
    Args:
        a: first parameter.
        b: second parameter.

    Returns:
        a string.
    """

    c:float = pow(b, a)

    return str(c) 
```

To facilitate documentation with `mkdocstrings`, all comments and docstrings must follow the Google style:

<https://google.github.io/styleguide/pyguide.html>

Example:

<https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>

Pylint should never have to complain ;)

## Unit tests

Find a strategy for consistent unit testing.


## Overview of ANNarchy's structure

Overview of the architecture:

* api
* parser
* generator