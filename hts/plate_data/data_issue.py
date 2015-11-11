# (C) 2015 Elke Schaper

"""
    :synopsis: The DataIssue Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import os
import pickle

from hts.plate_data import plate_data_io
from hts.plate_data import plate_data

LOG = logging.getLogger(__name__)


class DataIssue(plate_data.PlateData):

    """ ``DataIssue`` describes all information connected to the plate_data of a
    high throughput screen.

    Attributes:
        sample_replicate_count (str): (Explain!)
        layout_general_type (list of lists): The plate layout (explain!)

    """

    def __init__(self, data, **kwargs):
        # Perform DataIssue specific __init__

        # Run super __init__
        super().__init__(data=data, **kwargs)


    @classmethod
    def create_well_list(cls, well_list, width, height, data_tag, **kwargs):
        """

        Args:
            well_list (list of tuple):  List of wells with data issues, given as coordinate tuples (rowi, columni)
            width (int): Width of the well plate
            height (int): Height of the well plate
            data_tag (str): Tag of the created data
        """

        data = [[True for i in range(width)] for row in range(height)]
        for well in well_list:
            data[well[0]][well[1]] = False

        return cls(data={data_tag: data}, **kwargs)


    def write(self, format, path=None, tag=None, *args):
        """ Serialize and write ``DataIssue`` instances.

        Serialize ``DataIssue`` instance using the stated ``format``.

        Args:
            format (str):  The output format: Currently only "pickle".
            path (str): Path to output file

        .. todo:: Write checks for ``format`` and ``path``.
        """

        if format == 'pickle':
            with open(path, 'wb') as fh:
                pickle.dump(self, fh)
        if format == "csv":
            with open(path, 'w') as fh:
                for row in self.data[tag]:
                    fh.write(",".join([str(datum) for datum in row]) + "\n")
        else:
            raise Exception('Format is unknown: {}'.format(format))
