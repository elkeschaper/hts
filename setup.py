import glob
import os
import shutil
import sys

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command


setup(
    name="hts",
    version="0.0.1",
    author="HTS developers",
    author_email="elke.schaper@isb-sib.ch",
    packages=["hts", "hts.run", "hts.run.test"],
    #packages=find_packages(exclude=["tests*"]),
    scripts= SCRIPTS1 + SCRIPTS2,
    url="http://pypi.python.org/pypi/hts_io/",
    license="LICENSE.txt",
    description="Input / output for high throughput screening data.",
    long_description=read("README.rst"),
    #include_package_data=True, # If you want files mentioned in MANIFEST.in also to be installed, i.e. copied to usr/local/bin
    classifiers = [
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: OS Independent",
        ],
    install_requires=[
        "configobj >= 5.0.6",
        #"docutils >= 0.11", # Uncomment if you wish to create the documentation locally.
        "numpy >= 1.6.1",
        #"pypandoc >= 0.9.6" # Uncomment if you wish to convert the markdown readme to a rest readme for upload on Pypi.
        #"pytest >= 2.5.2", # Uncomment if you wish to run the tests locally.
        "scipy >=0.12.0",
        #"Sphinx >= 1.2.2", # Uncomment if you wish to create the documentation locally.
    ],
    # package_data: None-module files, which should still be distributed are mentioned here:

    package_dir={"hts": "hts"},
)
