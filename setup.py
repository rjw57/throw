from setuptools import setup, find_packages

import version

setup(
    name = "throw",
    version = version.get_git_version(),
    packages = find_packages(),

    entry_points = {
        'console_scripts': ['throw=throw.throw:main'],
    },

    install_requires = ['argparse'],

    # metadata for upload to PyPI
    author = "Rich Wareham",
    author_email = "rjw57@cam.ac.uk",
    description = "Simply share files from the command line",
    license = "Apache 2.0",
    keywords = "file sharing throw email",
    url = "http://github.com/rjw57/throw",

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

        # make sure to use :: Python *and* :: Python :: 3 so
        # that pypi can list the package on the python 3 page
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)
