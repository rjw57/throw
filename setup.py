from setuptools import setup, find_packages

import os
import sys
import version

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

additional_requires = []

# PyCURL is a Python 2-only module for the moment, so don't make it a 
# dependency for Python 3.
if sys.version_info[0] < 3:
    additional_requires += ['pycurl']

setup(
    name = "throw",
    version = version.get_git_version(),
    packages = find_packages(),

    entry_points = {
        'console_scripts': ['throw=throw.commandline:run'],
    },

    install_requires = ['argparse'] + additional_requires,

    test_suite = 'throw.tests.test_all',

    # metadata for upload to PyPI
    author = "Rich Wareham",
    author_email = "rjw57@cam.ac.uk",
    description = "Simply share files from the command line",
    license = "Apache 2.0",
    keywords = "file sharing throw email",
    url = "http://github.com/rjw57/throw",
    long_description = read('README.markdown'),

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Communications',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: File Sharing',
        'Topic :: Utilities',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)
