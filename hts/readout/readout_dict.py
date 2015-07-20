# (C) 2015 Elke Schaper

"""
    :synopsis: The ReadoutDict Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import ast
import logging
import os
import pickle
import re

from hts.readout import plate_io, readout

LOG = logging.getLogger(__name__)


class ReadoutDict:

    """ ``ReadoutDict`` describes all information connected to the readout_dict
    of a high throughput screen. This could be either several readouts of a
    plate, or the same readout across several plates.

    Attributes:
        name (str): Name of the readout_dict (e.g. plate)
        #width (int): Width of the plate
        #height (int): Height of the plate
        read_outs (dict of Readout): The raw readouts from i.e. the envision reader.
        net_read_outs (dict of Readout): The net readouts derived from the read_outs


    """

    def __str__(self):
        """
            Create string for ReadoutDict instance.
        """
        try:
            readout_dict = ("<ReadoutDict instance>\nname: {}\nNumber of read_outs: {}"
                    "\nwidth: {}\nheight: {}".format(self.name,
                    len(self.read_outs), self.width, self.height))
        except:
            readout_dict = "<ReadoutDict instance>"
            LOG.warning("Could not create string of ReadoutDict instance.")

        return readout_dict


    def __init__(self, read_outs, name = None, **kwargs):

        LOG.debug(read_outs)

        self.read_outs = {i: j if type(j) == readout.Readout else readout.Readout(j) for i,j in read_outs.items()}

        if name:
            self.name = name

        # Make sure all readouts are equal in height and width.
        plate_heights = [i.height for i in self.read_outs.values()]
        plate_widths = [i.width for i in self.read_outs.values()]
        if len(set(plate_heights)) != 1 or len(set(plate_widths)) != 1:
            raise Exception("ReadoutDict widths and lengths in the parsed output "
                "files are not all equal: plate_heights: {}, plate_widths: {} "
                    "".format(plate_heights, plate_widths))
        self.height = plate_heights[0]
        self.width = plate_widths[0]

        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


    def create(path, format=None):
        """ Create ``ReadoutDict`` instance.

        Create ``ReadoutDict`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input file, at current not specified

        .. todo:: Write checks for ``format`` and ``path``.
        .. todo:: Implement
        """

        if format == 'csv':
            readout_dict = plate_io.read_csv(path)
            path, file = os.path.split(path)
            return ReadoutDict(name=file, read_outs=readout_dict)
        elif format == 'envision_csv':
            readout_dict_info, channel_wise_reads, channel_wise_info = plate_io.read_envision_csv(path)
            path, file = os.path.split(path)
            return ReadoutDict(name=file, read_outs=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info)
        elif format == 'insulin_csv':
            readout_dict_info, channel_wise_reads, channel_wise_info = plate_io.read_insulin_csv(path)
            path, file = os.path.split(path)
            return ReadoutDict(name=file, read_outs=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info)
        elif format == 'pickle':
            with open(file, 'rb') as fh:
                return pickle.load(fh)
        else:
            raise Exception("Format: {} is not implemented in "
                            "ReadoutDict.create()".format(format))


    def get_readout(self, tag):
        """ Retrieve readout `tag`

        Retrieve readout `tag`

        Args:
            tag (str): Key of readout

        """

        try:
            return self.read_outs[key]
        except:
            try:
                return self.read_outs[ast.literal_eval(tag)]
            except:
                raise KeyError('tag: {} is not in self.readouts: {}'
                                ''.format(tag, self.read_outs.keys()))

    def set_plate_layout(self, plate_layout):
        """ Set `self.plate_layout`

        Set `self.plate_layout`

        Args:
            plate_layout (PlateLayout): A ``PlateLayout`` instance
        """

        self.plate_layout = plate_layout
        # Push PlateLayout to readouts
        for read_out in self.read_outs.values():
            read_out.plate_layout = self.plate_layout



    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``ReadoutDict`` instances.

        Serialize ``ReadoutDict`` instance using the stated ``format``.

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