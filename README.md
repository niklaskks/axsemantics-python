# axsemantics-python

Use the AX Semantics Data Exchange API from python3 - you can find the API documentation with example calls  [here](http://apidocs.ax-semantics.com).


### Excel Upload Quickstart

If you want to import a manually created xlsx file, there is a helper script to extract that data into the proper JSON format
* see /bin/excel_upload.py
* edit the file and make the proper configuration:
 * change username & password
 * edit the content project ID, where the things should be created
 * set the 'MAPPING' variables, to extract the proper data: map xslx columns to proper names for AX
  * a 'uid' and a 'name' property is required
    * 'a_uid_column_in_your_table': 'uid',
    * 'name_column_in_your_table': 'name',
  * extract Lists or key:value pairs into JSON dicts
    * 'Sizes': [splitlist, {'separator': '~'}],
    * 'Specification': [splitdata, {'row_separator': '~',
                                  'value_separator': ':'}]

run with ./excel_upload.py $yourfilename.xlsx

### How to install

Please work in a virtualenv. 

    virtualenv -p /usr/bin/python3 axsemantics
    source axsemantics/bin/activate
    pip install axsemantics

* requires: `python3`.

When you are done with your work with the client you can deactivate the virtualenv with the command `deactivate`.


### On Error Handling

Since this topic is very specific to Python, it isn't discussed in the [API
documentation](https://apidocs.ax-semantics.com).

This Python library has three exception classes:

 * `axsemantics.AuthenticationError`: Will be raised when the wrong credentials are supplied in the `login` method.
 * `axsemantics.APIConnectionError`: Will be raised on connection timeouts and otherwise failed connections.
 * `axsemantics.APIError`: Will be raised when the server responds with a `4xx` or `5xx` HTTP response code.

The `APIConnectionError` and the `APIError` can be raised on any action involving the server, primarily `save()`, `create()`,
`delete()` and `refresh()` calls.

## Maintainer Commands

    rm -rf axsemantics.egg-info build dist
    python setup.py sdist
    python setup.py bdist_wheel
    twine upload -r pypi dist/*
