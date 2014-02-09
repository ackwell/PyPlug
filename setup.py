import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "PyPlug",
    version = "0.0.1",
    author = "Saxon Landers",
    author_email = "saxon@ackwell.com.au",
    description = "Component decoupling pattern for python",
    license = "MIT",
    keywords = "component decouple pattern",
    url = "http://ackwell.github.io/PyPlug/",
    packages = find_packages(),
    long_description = read('README.md')
)
