[![ax logo](docs/AX_Logo.png)](https://www.ax-semantics.com/)

# axsemantics-python

Use the AX Semantics API from python3 - documentation is [here](https://apidocs.ax-semantics.com).

# On Error-Handling

Since this topic is very specific to Python, it isn't discussed in the [API
documentation](https://apidocs.ax-semantics.com).

This Python library has three exception classes:

 * `axsemantics.AuthenticationError`: Will be raised when the wrong credentials are supplied in the `login` method.
 * `axsemantics.APIConnectionError`: Will be raised on connection timeouts and otherwise failed connections.
 * `axsemantics.APIError`: Will be raised when the server responds with a `4xx` or `5xx` HTTP response code.

The `APIConnectionError` and the `APIError` can be raised on any action involving the server, primarily `save()`, `create()`,
`delete()` and `refresh()` calls.

# How to install

    pip install axsemantics

# How to contribute

Fork it, fix it, PR it! :)

# Maintainer Commands

    rm -rf axsemantics.egg-info build dist
    python setup.py sdist
    python setup.py bdist_wheel
    twine upload -r pypi dist/*
