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

        LOG.debug(name)
        LOG.debug(raw_read_outs)

        self.name = name
        self.raw_read_outs = raw_read_outs

        # Make sure all readouts are equal in height and width.
        plate_heights = [len(i) for i in self.raw_read_outs.values()]
        plate_widths = [len(i[0]) for i in self.raw_read_outs.values()]
        if len(set(plate_heights)) != 1 or len(set(plate_widths)) != 1:
            raise Exception("Plate widths and lengths in the parsed output "
                "files are not all equal: plate_heights: {}, plate_widths: {} "
                    "".format(plate_heights, plate_widths))
        self.height = plate_heights[0]
        self.width = plate_widths[0]

        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


    def create(path, format=None):
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
            return Plate(name=file, raw_read_outs=plate)
        elif format == 'envision_csv':
            plate_info, channel_wise_reads, channel_wise_info = plate_io.read_envision_csv(path)
            path, file = os.path.split(path)
            return Plate(name=file, raw_read_outs=channel_wise_reads, plate_info=plate_info, channel_wise_info=channel_wise_info)
        elif format == 'insulin_csv':
            plate_info, channel_wise_reads, channel_wise_info = plate_io.read_insulin_csv(path)
            path, file = os.path.split(path)
            return Plate(name=file, raw_read_outs=channel_wise_reads, plate_info=plate_info, channel_wise_info=channel_wise_info)
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