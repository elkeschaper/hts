# (C) 2015 Elke Schaper

"""
    :synopsis: Input/output for runs.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import csv
import logging
import os
import re

LOG = logging.getLogger(__name__)

################################## WRITE RUN DATA  #########################


def serialize_screen_data_for_r(screen_data, delimiter = ","):
    ''' Serialize run data for easy read-in as a data.frame in R.

    Serialize run data for easy read-in as a data.frame in R, in e.g. csv or
    tsv format.

    Attributes:
        run (Run): A ``Run`` instance.
        delimiter (str): A String instance. Defines the delimiter in the output
            file (e.g. "," for csv or "\t" for tsv)

    Returns:
        str: The serialized screen_data as a string.

    ..ToDo: Update to fit current Run class.
    '''

    all_data = [["plate_tag", "channel_tag", "x1", "x2", "x3", "y", "type"]]
    for iPlate, iPlate_data in screen_data.plate_reads.items():
        for iChannel, iChannel_data in iPlate_data['channels'].items():
            data = iChannel_data['data']
            for i_row, i_data_row, i_layout_row in zip(range(1, len(data) + 1), data, screen_data.plate_layout):
                for i_col, i_data, i_layout in zip(range(1, len(i_data_row) + 1), i_data_row, i_layout_row):
                    all_data.append([iPlate, iChannel, i_col, i_row, iPlate_data['info']['x3'],i_data, i_layout])

    return "\n".join([delimiter.join([str(j) for j in i]) for i in all_data])