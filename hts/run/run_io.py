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

from hts.plate import plate

LOG = logging.getLogger(__name__)

################################## WRITE RUN DATA  #########################


def serialize_run_for_r(run_data, delimiter = ",", column_name = None):
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
    if not column_name:
        column_name = ["x3_plate_name", "xp1", "xp2", "x1", "x2", "x3", "y", "y_type", "sample", "sample_type", "sample_replicate"]

    all_data = [column_name]
    # Iterate over plates
    for iPlate_index, iPlate in run_data.plates.items():
        # Plates can have different layouts.
        plate_layout_container = iPlate.plate_layout
        plate_layout = plate_layout_container.data["layout"]
        layout_general_type = plate_layout_container.data["layout_general_type"]
        sample_replicate_count = plate_layout_container.data["sample_replicate_count"]
        # Iterate over readouts in plates (raw and preprocessed)
        #import pdb; pdb.set_trace()
        for iReadout_index, iReadout in iPlate.readout.data.items():
            # Iterate over the x axis ("width") and the y axis ("height")
            for i_row, i_col in itertools.product(range(iPlate.height), range(iPlate.width)):
                h_coordinate = plate.translate_coordinate_humanreadable((i_row, i_col))
                all_data.append([iPlate.name,
                                h_coordinate[1],
                                h_coordinate[0],
                                i_col + 1,
                                i_row + 1,
                                iPlate_index,
                                iReadout[i_row][i_col],
                                iReadout_index,
                                plate_layout[i_row][i_col],
                                layout_general_type[i_row][i_col],
                                sample_replicate_count[i_row][i_col]])



    return "\n".join([delimiter.join([str(j) for j in i]) for i in all_data])