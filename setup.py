#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess

        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='faster_closeio',
    version='0.1.39',
    description='Slim API wrapper to access close.io CRM',
    long_description=readme + '\n\n' + history,
    author='Denis Cornehl',
    author_email='denis.cornehl@gmail.com',
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    entry_points={'pytest11': ['closeio = closeio.contrib.pytest_plugin']},
    cmdclass={'test': PyTest},
)
