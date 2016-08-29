#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read().replace('.. :changelog:', '')
PACKAGE = 'closeio'
NAME = 'faster_closeio'
VERSION = __import__(PACKAGE).__version__


setup(
    name=NAME,
    version=VERSION,
    description='Slim API wrapper to access close.io CRM',
    long_description=readme + '\n\n' + history,
    author='Denis Cornehl',
    author_email='denis.cornehl@gmail.com',
    download_url='https://github.com/Thermondo/closeio',
    url='https://github.com/fasterweb/closeio',
    packages=[
        'closeio',
        'closeio.contrib',
        'closeio.contrib.django',
    ],
    package_dir={'closeio': 'closeio'},
    include_package_data=True,
    install_requires=[
        'requests',
        'slumber',
        'python-dateutil',
        'six',
    ],
    license="BSD",
    zip_safe=False,
    keywords='closeio',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={'pytest11': ['closeio = closeio.contrib.pytest_plugin']},
)
