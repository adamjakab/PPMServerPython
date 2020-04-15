#  Copyright: Copyright (c) 2020., Adam Jakab
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: See LICENSE.txt

import pathlib
from distutils.util import convert_path

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# About
plg_ns = {}
about_path = convert_path('about.py')
with open(about_path) as about_file:
    exec(about_file.read(), plg_ns)

# Test requirements
_test_requirements = ['pytest', 'nose', 'coverage', 'requests']

# Setup
setup(
    name=plg_ns['__PACKAGE_NAME__'],
    version=plg_ns['__version__'],
    description=plg_ns['__PACKAGE_DESCRIPTION__'],
    author=plg_ns['__author__'],
    author_email=plg_ns['__email__'],
    url=plg_ns['__PACKAGE_URL__'],
    license='MIT',
    long_description=README,
    long_description_content_type='text/markdown',
    platforms='ALL',

    include_package_data=True,
    test_suite='test',
    packages=[],

    python_requires='>=3.6',

    install_requires=[
        'Flask'
    ],

    tests_require=_test_requirements,

    # Extras needed during testing
    extras_require={
        'tests': _test_requirements,
    },

    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
