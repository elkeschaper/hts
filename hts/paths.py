# (C) 2016 Elke Schaper @ Vital-IT, SIB

"""
    :synopsis: The system paths module.
    .. moduleauthor:: Elke Schaper <elke.schaper@sib.swiss>

"""

import os

# What is the path to the package? E.g. path/to/HTS/hts
PACKAGE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_data")

TUTORIAL_DATA_NORMALIZATION_PATH = os.path.join(DATA_DIRECTORY, "Runs", "run_config_tutorial_1.txt")