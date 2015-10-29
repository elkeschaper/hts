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

    def __init__(self, data, name, **kwargs):

        # Perform DataIssue specific __init__
        data = {name: data}

        # Run super __init__
        super().__init__(data=data, name=name, **kwargs)



    def create(path, format=None, **kwargs):
        """ Create ``DataIssue`` instance.

        Create ``DataIssue`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input file, at current not specified


        .. todo:: Write checks for ``format`` and ``path``.
        """

        if format == 'csv':
            data = plate_data_io.read_csv(path, remove_empty_row=False)
            path, file = os.path.split(path)
            return DataIssue(name=file, data=data)
        elif format == 'pickle':
            with open(path, 'rb') as fh:
                return pickle.load(fh)
        else:
            raise Exception("Format: {} is not implemented in "
                            "DataIssue.create()".format(format))



    def write(self, format, path=None, return_string=None, *args):
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
        else:
            raise Exception('Format is unknown: {}'.format(format))

        if path:
            with open(path, 'w') as fh:
                fh.write(output)
        if return_string:
            return output