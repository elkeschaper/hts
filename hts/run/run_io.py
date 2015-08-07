# (C) 2015 Elke Schaper

"""
    :synopsis: Input/output for runs.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import csv
import itertools
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

    plate_layout_container = run_data.plate_layout()
    plate_layout = plate_layout_container.layout
    layout_general_type = plate_layout_container.layout_general_type
    sample_replicate_count = plate_layout_container.sample_replicate_count

    all_data = [["x3_plate_name", "xp1", "xp2", "x1", "x2", "x3", "y", "y_type", "sample", "sample_type", "sample_replicate"]]
    # Iterate over plates
    for iPlate_index, iPlate in run_data.plates.items():
        # Iterate over readouts in plates (raw and preprocessed)
        for iReadout_index, iReadout in iPlate.read_outs.items():
            # Iterate over the x axis ("width") and the y axis ("height")
            for i_row, i_col in itertools.product(range(iPlate.height), range(iPlate.width)):
                all_data.append([iPlate.name,
                                iReadout.axes['x'][i_col],
                                iReadout.axes['y'][i_row],
                                i_col + 1,
                                i_row + 1,
                                iPlate_index,
                                iReadout.data[i_row][i_col],
                                iReadout_index,
                                plate_layout[i_row][i_col],
                                layout_general_type[i_row][i_col],
                                sample_replicate_count[i_row][i_col]])



    return "\n".join([delimiter.join([str(j) for j in i]) for i in all_data])