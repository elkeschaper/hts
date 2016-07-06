import os
import sys

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), "r") as f:
        return f.read()


# Set the home variable with user argument:
# This is only needed if you have configs in local ~/.hts
# Prettier solutions might be possible: http://stackoverflow.com/questions/677577/distutils-how-to-pass-a-user-defined-parameter-to-setup-py
# try:
#     i = sys.argv.index("--home")
#     HOME = sys.argv[i + 1]
#     del sys.argv[i+1]
#     del sys.argv[i]
#     if not os.path.exists(HOME):
#         raise ValueError("The argument supplied in --home is not a valid path: {}".format(HOME))
# except:
#     HOME=os.path.expanduser("~")

#SCRIPTS1 = [os.path.join("hts", "examples", i) for i in ["example_workflow.py"]]


setup(
    name="hts",
    version="0.0.1",
    author="HTS developers",
    author_email="elke.schaper@sib.swiss",
    packages=["hts", "hts.data_tasks", "hts.data_tasks.test", "hts.plate", "hts.plate.test", "hts.plate_data", "hts.plate_data.test", "hts.protocol", "hts.protocol.test", "hts.run", "hts.run.test"],
    url="http://pypi.python.org/pypi/hts/",
    license="LICENSE.txt",
    description="High throughput screening data I/O, normalization, analysis",
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
        #"docutils >= 0.12", # Uncomment if you wish to create the documentation locally.
        "GPy >= 1.0.9",  # GPy requires numpy during installation.
        "matplotlib >= 1.5.0",
        "numpy >= 1.6.1",
        "pandas >= 0.18.0",
        #"pypandoc >= 1.1.3" # Uncomment if you wish to convert the markdown readme to a rest readme for upload on Pypi.
        #"pytest >= 2.8.3", # Uncomment if you wish to run the tests locally.
        "scipy >= 0.17.1",
        #"Sphinx >= 1.3.3", # Uncomment if you wish to create the documentation locally.
        "xlrd >= 0.9.4",
    ],
    # package_data: None-module files, which should still be distributed are mentioned here:

    package_dir={"hts": "hts"},
)
