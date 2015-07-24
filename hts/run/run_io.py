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


def serialize_run_for_r(run_data, delimiter = ","):
    ''' Serialize run data for easy read-in as a data.frame in R.

    Serialize run data for easy read-in as a data.frame in R, in e.g. csv or
    tsv format.

    Attributes:
        run (Run): A ``Run`` instance.
        delimiter (str): A String instance. Defines the delimiter in the output
            file (e.g. "," for csv or "\t" for tsv)

    Returns:
        str: The serialized run_data as a string.

    ..ToDo: Update to fit current Run class.
    '''


    plate_layout = run_data.plate_layout().layout
    all_data = [["x3_plate_name", "xp1", "xp2", "x1", "x2", "x3", "y", "y_type", "type"]]
    for iPlate_index, iPlate in run_data.plates.items():
        for iReadout_index, iReadout in iPlate.read_outs.items():
            data = iReadout.data
            for i_row, i_row_plate, i_data_row, i_layout_row in zip(range(1, len(data) + 1), iReadout.axes['x'], data, plate_layout):
                for i_col, i_col_plate, i_data, i_layout in zip(range(1, len(i_data_row) + 1), iReadout.axes['y'], i_data_row, i_layout_row):
                    all_data.append([iPlate.name, i_row_plate, i_col_plate, i_row, i_col, iPlate_index, i_data, iReadout_index, i_layout])

    return "\n".join([delimiter.join([str(j) for j in i]) for i in all_data])