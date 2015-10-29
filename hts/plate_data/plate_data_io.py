# (C) 2015 Elke Schaper

"""
    :synopsis: Input/output for plate data.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import csv
import logging
import os
import re

LOG = logging.getLogger(__name__)

################################## READ SCREEN DATA  #########################


def read_csv(file, delimiter=",", remove_empty_row=True):
    """Read plate layout file in csv format.

    The arrangement in the .csv file corresponds exactly to the plate layout.
    Vocabulary:
    neg_k: negative control k
    pos_k: positive control k
    s_k: sample k
    All other names may be used, but are not interpreted at current.


    """

    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        if remove_empty_row:
            data = [line for line in reader if line != [] and set(line) != {''}]
        else:
            data = [[datum if datum != "" else None for datum in line] for line in reader]
        if len(set([len(row) for row in data])) != 1:
            raise Exception('Rows in input file {} differ in lengths: {}'.format(file, [len(row) for row in data]))

        return data
