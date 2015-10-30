# (C) 2015 Elke Schaper

"""
    :synopsis: Input/output for plate data.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import csv
import logging
import os
import re
import xlrd

LOG = logging.getLogger(__name__)

################################## READ SCREEN DATA  #########################


def read_csv(file, delimiter=",", remove_empty_row=True):
    """Read plate data file in csv format.

    The arrangement in the .csv file corresponds exactly to the plate layout.
    """

    with open(file, 'r') as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        if remove_empty_row:
            data = [line for line in reader if line != [] and set(line) != {''}]
        else:
            data = [[datum if datum != "" else None for datum in line] for line in reader]
        if len(set([len(row) for row in data])) != 1:
            raise Exception('Rows in input file {} differ in lengths: {}'.format(file, [len(row) for row in data]))

        LOG.info("File: {}, height: {}, width: {}".format(file, len(data), len(data[0])))

        return data

        # For readout, this used to be (with a tag supplied to the method):
        #return {tag: data}



def read_excel(path, tags=None, **kwargs):
    """Read plate data path in excel format.

    Read plate data path in excel format.
    The plate values must be the only data in the excel sheets. That is, no
    check of the content of the sheet, nor of its size is currently performed.


    Args:
        path (str): Path to the path with  data in the excel path format.
        tag (list of str): Names of all spreadsheets for which the data shall be returned.


    Returns:
        data (dict of list of lists): Data retrieved from the excel file

    """

    excel_workbook = xlrd.open_workbook(path)

    if tags:
        try:
            excel_sheets = [excel_workbook.sheet_by_name(i) for i in tags]
        except:
            raise ValueError('Retrieving the excel sheets by name failed.'
                'Probably, the tags {} were not included in the excel path {},'
                '{}'.format(tags, path, excel_workbook.sheet_names()))
    else:
        excel_sheets = excel_workbook.sheets()

    data = {}
    for i_sheet in excel_sheets:
        # Only add sheets that contain data:
        if i_sheet.nrows > 0:
            tmp_data = [i_sheet.row_values(i) for i in range(i_sheet.nrows)]
            data[i_sheet.name] = tmp_data

    if data == {}:
        raise ValueError('One of the requested excel sheets in {} with defined tags {} is empty.'.format(path, tags))

    return data