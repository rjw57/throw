from setuptools import setup, find_packages
setup(
    name = "throw",
    version = "0.1",
    packages = find_packages(),
    scripts = ['throw'],

    install_requires = ['argparse'],

    # metadata for upload to PyPI
    author = "Rich Wareham",
    author_email = "rjw57@cam.ac.uk",
    description = "Simply share files from the command line",
    license = "Apache 2.0",
    keywords = "file sharing throw email",
    url = "http://github.com/rjw57/throw",
)
