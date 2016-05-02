# (C) 2015, 2016 Elke Schaper

"""
    :synopsis: Input/output for runs.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import collections
import csv
import io
import itertools
import logging
import os
import re

import pandas as pd

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
        plate_data_structured["config_data"] = plate_data.PlateData(meta_data)

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


def serialize_as_csv_one_row_per_well(run_data, readouts=None, rename_columns_dict=None, **kwargs):
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

    # Get data as pandas.
    data_frame = serialize_as_pandas(run_data=run_data, readouts=readouts)

    # Rename columns on demand.
    data_frame = rename_pd_columns(data_frame=data_frame, rename_dict=rename_columns_dict)

    # Give back results as csv.
    s = io.StringIO()
    data_frame.to_csv(s, **kwargs)
    string = s.getvalue()
    return string


def serialize_as_pandas(run_data, readouts=None, well_name_pattern=None):
    """ Serialize data as pandas with one row == one well.

    E.g.:
    Plate ID,Well ID,Compound,,Data_0,Data_1,signal
    XYZ005,A001,Glucose,,4444,5555,0.3

    Attributes:
        readouts (list of str): Which readouts will be printed. If not indicated, all readouts are printed.
        plate_name (str): The name of the plate name column
        well_name (str): The name of the well name column
        plate_layout_name (str): The name of the plate layout column
    """

    if readouts == None:
        i_plate = next(iter(run_data.plates.values()))
        readouts = sorted(list(i_plate.readout.data.keys()))

    all_data = collections.defaultdict(list)

    # Iterate over plates
    for i_plate_index, i_plate in run_data.plates.items():
        # Plates can have different layouts.
        plate_layout_container = i_plate.plate_layout
        plate_layout = plate_layout_container.data["layout"]
        layout_general_type = plate_layout_container.data["layout_general_type"]
        # Iterate over the x axis ("width") and the y axis ("height")
        for i_row, i_col in itertools.product(range(i_plate.height), range(i_plate.width)):
            h_coordinate = plate.translate_coordinate_humanreadable((i_row, i_col))
            # Here, we decide what data is saved:
            all_data["well_1"].append(h_coordinate[0])
            all_data["well_2"].append(h_coordinate[1])
            all_data["well_name"].append(plate.translate_coordinate_humanreadable((i_row, i_col), pattern=well_name_pattern))
            all_data["plate_name"].append(i_plate_index)
            for readout in readouts:
                if readout in i_plate.readout.data:
                    all_data[readout].append(i_plate.readout.data[readout][i_row][i_col])
                else:
                    all_data[readout].append(None)

    return pd.DataFrame(all_data)


def add_meta_data(run_data, meta_data_kwargs, meta_data_well_name_pattern=None,
                  meta_data_rename=None, meta_data_exclude_columns=None, readouts=None):

    read_data = serialize_as_pandas(run_data, readouts=readouts, well_name_pattern=meta_data_well_name_pattern)

    meta_data = pd.read_csv(**meta_data_kwargs)

    # Rename columns on demand.
    meta_data = rename_pd_columns(meta_data, rename_dict=meta_data_rename)

    # Delete columns on demand.
    if type(meta_data_exclude_columns) == list:
        for excluded_column in meta_data_exclude_columns:
            meta_data.drop(excluded_column, axis=1, inplace=True)

    if len(set(read_data["well_name"]) & set(meta_data["well_name"])) == 0:
        raise Exception("Different well_name format: hts data {} and meta_data {}".format(set(read_data["well_name"]),
                                                                                          set(meta_data["well_name"])))

    if len(set(read_data["plate_name"]) & set(meta_data["plate_name"])) == 0:
        raise Exception("Different plate_name format: hts data {} and meta_data {}".format(set(read_data["plate_name"]),
                                                                                          set(meta_data["plate_name"])))
    # Perform a join on the data frames.
    merged_data = pd.merge(read_data, meta_data, on=["well_name", "plate_name"])
    return merged_data



def rename_pd_columns(data_frame, rename_dict):

    if rename_dict != None:
        for original_name, new_name in rename_dict.items():
            try:
                data_frame.rename(columns={original_name: new_name}, inplace=True)
            except:
                LOG.error("Could not replace column name {} with {}".format(original_name, new_name))
    else:
        LOG.warning("Did not rename pandas dataframe columns - no dict was provided.")

    return data_frame

