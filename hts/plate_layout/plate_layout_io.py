# (C) 2015 Elke Schaper

"""
    :synopsis: Input/output for plate layouts.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import csv
import logging
import os
import re

LOG = logging.getLogger(__name__)

################################## READ SCREEN DATA  #########################


def read_csv(file):
    """Read plate layout file in csv format.

    The arrangement in the .csv file corresponds exactly to the plate layout.
    Vocabulary:
    neg_k: negative control k
    pos_k: positive control k
    s_k: sample k
    All other names may be used, but are not interpreted at current.


    """

    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        return [line for line in reader if line != []]
