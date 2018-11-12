#!/usr/bin/env python

from setuptools import setup

setup(
    setup_requires=['pbr', 'pytest-runner'],
    tests_require=['django>=1.11', 'pytest', 'pytest-django', 'pytest-rerunfailures'],
    pbr=True,
)
