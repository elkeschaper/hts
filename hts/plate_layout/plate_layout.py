# (C) 2015 Elke Schaper

"""
    :synopsis: The PlateLayout Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import os
import pickle
import re

from plate_layout import plate_layout_io

LOG = logging.getLogger(__name__)


class PlateLayout:

    """ ``PlateLayout`` describes all information connected to the plate_layout of a
    high throughput screen.

    Attributes:
        name (str): Name of the plate_layout
        layout (list of lists): The plate layout

    """

    def __init__(self, name, layout):

        self.name = name
        self.layout = layout

    def create(path, format=None):
        """ Create ``PlateLayout`` instance.

        Create ``PlateLayout`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input file, at current not specified


        .. todo:: Write checks for ``format`` and ``path``.
        """

        if format == 'csv':
            layout = plate_layout_io.read_csv(path)
            path, file = os.path.split(path)
            return PlateLayout(name = file, layout)
        elif format == 'pickle':
            with open(file, 'rb') as fh:
                return pickle.load(fh)
        else:
            raise Exception("Format: {} is not implemented in "
                            "PlateLayout.create()".format(format))


    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``PlateLayout`` instances.

        Serialize ``PlateLayout`` instance using the stated ``format``.

        Args:
            format (str):  The output format: Currently only "pickle".
            path (str): Path to output file

        .. todo:: Write checks for ``format`` and ``path``.
        """

        if format == 'pickle':
            with open(file, 'wb') as fh:
                pickle.dump(self, fh)
        else:
            raise Exception('Format is unknown: {}'.format(format))

        if path:
            with open(path, 'w') as fh:
                fh.write(output)
        if return_string:
            return output