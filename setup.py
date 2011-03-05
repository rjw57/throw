from setuptools import setup, find_packages

import version

setup(
    name = "throw",
    version = version.get_git_version(),
    packages = find_packages(),
    scripts = ['throw.py'],

    install_requires = ['argparse'],

    # metadata for upload to PyPI
    author = "Rich Wareham",
    author_email = "rjw57@cam.ac.uk",
    description = "Simply share files from the command line",
    license = "Apache 2.0",
    keywords = "file sharing throw email",
    url = "http://github.com/rjw57/throw",
)
