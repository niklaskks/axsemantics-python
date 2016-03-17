from codecs import open
from os import path
from setuptools import setup

setup(
    name = 'axsemantics',
    version = '0.1-1',

    description = 'AXSemantics API client',

    url = 'https://github.com/axsemantics/axsemantics-python',

    author = 'Tobias Kunze',
    author_email = 'tobias.kunze@ax-semantics.com',

    license = 'MIT',

    classifiers = [
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages = ['axsemantics'],

    install_requires = [
        'requests==2.9.1',
    ],
)
