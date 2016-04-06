# (C) 2015 Elke Schaper

"""
    :synopsis: Input/output for runs.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import collections
import csv
import itertools
import logging
import os
import re

from hts.plate import plate
from hts.plate_data import plate_data, readout

LOG = logging.getLogger(__name__)


################################## READ RUN DATA  #########################

def convert_well_id_format(well, read="letternumber"):

    if read=="letternumber":
        p = re.compile("([A-Za-z]+)(\d+)")
        match = p.match(well)
        row = match.group(1)
        column = str(int(match.group(2)))
        well_id = plate.TRANSLATE_HUMANREADABLE_COORDINATE[(row, column)]

    return well_id


def read_csv(file, column_plate_name, column_well, columns_readout, columns_meta, width, height, delimiter=",", remove_empty_row=True):
    """Read run data file in csv format, with one row for each well.

    E.g.:
    Plate ID,Well ID,Compound,,Data_0,Data_1,signal
    XYZ005,A001,Glucose,,4444,5555,0.3

    Attributes:
        file (str): The path to the file.
        column_plate_name (str): The column with plate name information.
        column_well (str): The column with well coordinate information.
        columns_readouts (list of str): Columns with readout data.
        columns_metas (list of str): Columns with meta data.
    """

    data = collections.defaultdict(dict)

    with open(file, 'r') as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        header = next(reader)

        try:
            column_id_plate_name = header.index(column_plate_name)
            column_id_well = header.index(column_well)
            columns_id_readouts = [header.index(i) for i in columns_readout]
            columns_id_metas = [header.index(i) for i in columns_meta]
        except:
            raise Exception('Please check column_plate_name {}, column_well {}, and columns_save {}. No match '
                            'in the header {} found.'.format(column_plate_name, column_well, columns_readout, columns_meta, header))

        for line in reader:
            if remove_empty_row and (line == [] or set(line) == {''}):
                continue
            if len(header) != len(line):
                raise Exception('Header and rows in {} are not of the same length:\nHeader: {}\nRow: {}'.format(file, header, line))
            data[line[column_id_plate_name]][convert_well_id_format(line[column_id_well])] = [line[i] for i in columns_id_readouts + columns_id_metas]


    # Convert well-wise to plate-wise data and create PlateData and Plate Objects
    plates = []
    for plate_name, plate_data_unstructured in data.items():
        if len(plate_data_unstructured) != width * height:
            LOG.error('Plate "{}" is ignored: {} instead of {} wells.'.format(plate_name, len(plate_data_unstructured), width * height))
            continue
        plate_data_structured = {}
        # Shape readout data
        readout_data = {}
        for column_name in columns_readout:
            try:
                readout_data[column_name] = [[plate_data_unstructured[(row, column)].pop(0) for column in range(width)] for row in range(height)]
            except:
                import pdb; pdb.set_trace()
        plate_data_structured["readout"] = readout.Readout(readout_data)
        # Shape meta data
        meta_data = {}
        for column_name in columns_meta:
            meta_data[column_name] = [[plate_data_unstructured[(row, column)].pop(0) for column in range(width)] for row in range(height)]
        plate_data_structured["meta_data"] = plate_data.PlateData(meta_data)

        plates.append(plate.Plate(data=plate_data_structured, name=plate_name, width=width, height=height))

    LOG.info("Number of plates: {}, height: {}, width: {}".format(len(data), 11, 66))
    return plates




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
    for i_plate_index, i_plate in run_data.plates.items():
        # Plates can have different layouts.
        plate_layout_container = i_plate.plate_layout
        plate_layout = plate_layout_container.data["layout"]
        layout_general_type = plate_layout_container.data["layout_general_type"]
        sample_replicate_count = plate_layout_container.data["sample_replicate_count"]
        # Iterate over readouts in plates (raw and preprocessed)
        #import pdb; pdb.set_trace()
        for iReadout_index, iReadout in i_plate.readout.data.items():
            # Iterate over the x axis ("width") and the y axis ("height")
            for i_row, i_col in itertools.product(range(i_plate.height), range(i_plate.width)):
                h_coordinate = plate.translate_coordinate_humanreadable((i_row, i_col))
                all_data.append([i_plate.name,
                                h_coordinate[1],
                                h_coordinate[0],
                                i_col + 1,
                                i_row + 1,
                                i_plate_index,
                                iReadout[i_row][i_col],
                                iReadout_index,
                                plate_layout[i_row][i_col],
                                layout_general_type[i_row][i_col],
                                sample_replicate_count[i_row][i_col]])



    return "\n".join([delimiter.join([str(j) for j in i]) for i in all_data])


def write_csv(run_data, readouts=None, plate_name="Plate ID", well_name="Well ID", plate_layout_name="sample type", delimiter=","):
    """Write run data file in csv format, with one row for each well.

    E.g.:
    Plate ID,Well ID,Compound,,Data_0,Data_1,signal
    XYZ005,A001,Glucose,,4444,5555,0.3

    Attributes:
        readouts (list of str): Which readouts will be printed. If not indicated, all readouts are printed.
        plate_name (str): The name of the plate name column
        well_name (str): The name of the well name column
        plate_layout_name (str): The name of the plate layout column
    """

    if readouts==None:
        i_plate = next (iter (run_data.plates.values()))
        readouts = sorted(list(i_plate.readout.data.keys()))

    column_name = [plate_name, well_name, plate_layout_name] + readouts

    all_data = [column_name]
    # Iterate over plates
    for i_plate_index, i_plate in run_data.plates.items():
        # Plates can have different layouts.
        plate_layout_container = i_plate.plate_layout
        plate_layout = plate_layout_container.data["layout"]
        layout_general_type = plate_layout_container.data["layout_general_type"]
        # Iterate over the x axis ("width") and the y axis ("height")
        for i_row, i_col in itertools.product(range(i_plate.height), range(i_plate.width)):
            h_coordinate = plate.translate_coordinate_humanreadable((i_row, i_col))
            h_coordinate_fraunhofer = "{0}{1:03d}".format(h_coordinate[0], int(h_coordinate[2]))
            # Iterate over readouts in plates (raw and preprocessed)
            readout_data = [i_plate.readout.data[i][i_row][i_col] if i in i_plate.readout.data else None for i in readouts]
            all_data.append([i_plate_index,
                             h_coordinate_fraunhofer,
                             plate_layout[i_row][i_col]
                             ] + readout_data)

    return "\n".join([delimiter.join([str(j) for j in i]) for i in all_data])
