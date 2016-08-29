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
PACKAGE = __import__('closeio')
NAME = 'faster_closeio'

URL = 'https://github.com/Thermondo/closeio'


setup(
    name=NAME,
    version=PACKAGE.__version__,
    description='Slim API wrapper to access close.io CRM',
    long_description=readme + '\n\n' + history,
    author=PACKAGE.__author__,
    author_email=PACKAGE.__email__,
    download_url=URL,
    url=URL,
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
