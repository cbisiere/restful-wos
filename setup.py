#! /usr/bin/env python
from setuptools import setup

if __name__ == "__main__":
    setup(
        name='restful-wos',
        version='0.0.1',
        description='Python package simplifies access to the WoS RESTful API',
        long_description=open('README.md').read(),
        url='',
        author='Takuya Iwanaga',
        author_email='iwanaga.takuya@anu.edu.au',
        license='(c) 2018 Takuya Iwanaga',
        packages=['restful_wos'],
        install_requires=[
            'pyyaml',
            'tqdm',
            'pebble',
        ]
    )
