# (C) 2015 Elke Schaper

"""
    :synopsis: The ReadoutDict Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import ast
import logging
import numpy as np
import os
import pickle
import re
import sys

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
        if hasattr(self, "name"):
            name = self.name
        else:
            name = "<not named>"
        try:
            readout_dict = ("<ReadoutDict instance>\nname: {}\nread_outs: {}"
                    "\nNumber of read_outs: {}\nwidth: {}\nheight: {}".format(name,
                    str(self.read_outs.keys()), len(self.read_outs),
                    self.width, self.height))
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


    def create(path, format=None, **kwargs):
        """ Create ``ReadoutDict`` instance.

        Create ``ReadoutDict`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input file, at current not specified

        .. todo:: Write checks for ``format`` and ``path``.
        .. todo:: Implement
        """
        path_trunk, file = os.path.split(path)
        if "name" in kwargs:
            name = kwargs.pop("name")
        else:
            name = file
        LOG.debug("filename: {}".format(file))

        if format == 'csv':
            readout_dict = plate_io.read_csv(path)
            return ReadoutDict(name=name, read_outs=readout_dict)
        elif format == 'excel':
            readout_dict = plate_io.read_excel(path, **kwargs)
            return ReadoutDict(name=name, read_outs=readout_dict)
        elif format == 'envision_csv':
            readout_dict_info, channel_wise_reads, channel_wise_info = plate_io.read_envision_csv(path)
            return ReadoutDict(name=name, read_outs=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info)
        elif format == 'insulin_csv':
            readout_dict_info, channel_wise_reads, channel_wise_info = plate_io.read_insulin_csv(path)
            return ReadoutDict(name=name, read_outs=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info)
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
            return self.read_outs[tag]
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

    #### Preprocessing functions

    def preprocess(self, methodname, **kwargs):

            method = getattr(self, methodname)
            method(**kwargs)


    def calculate_net_fret(self, donor_channel, acceptor_channel,
                            fluorophore_donor = "fluorophore_donor",
                            fluorophore_acceptor = "fluorophore_acceptor",
                            buffer = "buffer", net_fret_key = "net_fret"):
        """ Calculate the net FRET signal for a donor acceptor FRET setup.

        Calculate the net FRET signal for a donor acceptor FRET setup.
        Typical donor -> aceptor pairs include

        * 414nm CFP -> 475nm -> YFP 525nm
        * EU -> 615nm -> APC 665nm

        The following wells are needed, for both channels

        * `donor` Donor_fluorophor blank
        * `acceptor` Acceptor_fluorophor blank
        * `buffer` Buffer blank

        The proportionality factor for donor compensation is then calculation as
        .. math::

        p = \frac{\hat{donor_{acceptor_channel}} - \hat{buffer_{acceptor_channel}}}{\hat{donor_{donor_channel}} - \hat{buffer_{donor_channel}}}

        Further, the net FRET signal `f` for all wells `x` may be calculated as:
        .. math::

        netfret = x_{acceptor_channel} - \hat{acceptor_{acceptor_channel}} - p \cdot (x_{donor_channel} - \hat{buffer_{donor_channel}})

        Args:
            donor_channel (str):  The key for self.read_outs where the donor_channel ``Readout`` instance is stored.
            acceptor_channel (str):  The key for self.read_outs where the acceptor_channel ``Readout`` instance is stored.
            fluorophore_donor (str):  The name of the donor fluorophore in self.plate_layout.
            fluorophore_acceptor (str):  The name of the acceptor fluorophore in self.plate_layout.
            buffer (str):  The name of the buffer in self.plate_layout.
            net_fret_key (str):  The key for self.read_outs where the resulting net fret ``Readout`` instance will be stored.

        """

        if net_fret_key in self.read_outs:
            raise ValueError("The net_fret_key {} is already in self.read_outs.".format(net_fret_key))

        #import pdb; pdb.set_trace()
        donor_readout = self.read_outs[donor_channel]
        acceptor_readout = self.read_outs[acceptor_channel]

        # Calculate p
        mean_donor_donor_channel = np.mean(donor_readout.filter_wells(fluorophore_donor))
        mean_acceptor_donor_channel = np.mean(donor_readout.filter_wells(fluorophore_acceptor))
        mean_buffer_donor_channel = np.mean(donor_readout.filter_wells(buffer))
        mean_donor_acceptor_channel = np.mean(acceptor_readout.filter_wells(fluorophore_donor))
        mean_acceptor_acceptor_channel = np.mean(acceptor_readout.filter_wells(fluorophore_acceptor))
        mean_buffer_acceptor_channel = np.mean(acceptor_readout.filter_wells(buffer))

        #import pdb; pdb.set_trace()
        for i in [mean_donor_donor_channel, mean_acceptor_donor_channel, mean_buffer_donor_channel, mean_donor_acceptor_channel, mean_acceptor_acceptor_channel, mean_buffer_acceptor_channel]:
            if np.isnan(i):
                raise ValueError("Calculation of {} resulted in {}. Check whether the plate layout is correctly assigned.".format(varname(i), i))

        p = (mean_donor_acceptor_channel - mean_buffer_acceptor_channel) / (mean_donor_donor_channel - mean_buffer_donor_channel)


        # Calculate the net FRET signal for the entire plate
        netfret = acceptor_readout.data - mean_acceptor_acceptor_channel - p*(donor_readout.data - mean_buffer_donor_channel)
        self.read_outs[net_fret_key] = readout.Readout(netfret)
        self.read_outs[net_fret_key].plate_layout = self.plate_layout