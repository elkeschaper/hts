# (C) 2015 Elke Schaper

"""
    :synopsis: The Plate Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import os
import pickle
import re

from plate import plate_io

LOG = logging.getLogger(__name__)


class Plate:

    """ ``Plate`` describes all information connected to the plate of a
    high throughput screen.

    Attributes:
        name (str): Name of the plate
        width (int): Width of the plate
        height (int): Height of the plate
        raw_read_outs (dict of np.array of np.arrays): The raw readouts from i.e. the envision reader.
        net_read_outs (dict of np.array of np.arrays): The net readouts derived from the raw_read_outs


    """

    def __init__(self, name, raw_read_outs, **kwargs):

        self.name = name
        self.raw_read_outs = raw_read_outs

        # Make sure all readouts are equal in height and width.
        plate_heights = [len(i) for i in all_plates]
        plate_widths = [len(i[0]) for i in all_plates]
        if len(set(plate_heights)) != 1 or len(set(plate_widths)) != 1:
            raise Exception("Plate widths and lengths in the parsed output "
                "files are not all equal: plate_heights: {}, plate_widths: {} "
                    "".format(plate_heights, plate_widths))
        self.height = plate_heights[0]
        self.width = plate_widths[0]

        for key, value in kwargs.items():
            if not self.haskey(key):
                setattr(self, value, key)


    def create(path, source=None, format=None):
        """ Create ``Plate`` instance.

        Create ``Plate`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input file, at current not specified

        .. todo:: Write checks for ``format`` and ``path``.
        .. todo:: Implement
        """

        if format == 'csv':
            plate = plate_io.read_csv(path)
            path, file = os.path.split(path)
            return Plate(name = file, plate)
        if format == 'envision_csv':
            plate_info, channel_wise_reads, channel_wise_info = plate_io.read_envision_csv(path)
            path, file = os.path.split(path)
            return Plate(name=file, raw_read_out=channel_wise_reads, plate_info=plate_info, channel_wise_info = channel_wise_info)
        elif format == 'pickle':
            with open(file, 'rb') as fh:
                return pickle.load(fh)
        else:
            raise Exception("Format: {} is not implemented in "
                            "Plate.create()".format(format))


    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``Plate`` instances.

        Serialize ``Plate`` instance using the stated ``format``.

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