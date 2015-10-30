# (C) 2015 Elke Schaper

"""
    :synopsis: The Readout Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import itertools
import logging
import numpy as np
import os
import pickle
import re

from hts.plate_data import plate_data, readout_io


LOG = logging.getLogger(__name__)




class Readout(plate_data.PlateData):

    """ ``Readout`` describes one plate matrix

    Attributes:
        width (int): Width of the plate
        height (int): Height of the plate
        data (np.array of np.arrays): A matrix of plate values
    """

    def __str__(self):
        """
            Create string for Readout instance.
        """
        try:
            data = ("<Readout instance>\nContains a numpy array of arrays."
                    "\nwidth: {}\nheight: {}".format(self.width, self.height))
        except:
            data = "<Readout instance>"
            LOG.warning("Could not create string of Readout instance.")

        return data


    def __init__(self, data, **kwargs):

        # All readout data is transformed to numpy array data
        data = {i: np.array([np.array([float(datum) for datum in row]) for row in j]) for i,j in data.items()}

        # Run super __init__
        super().__init__(data=data, **kwargs)

        # Perform PlateLayout specific __init__

        # This is what you've originally done- what should you do with it now?
        # Convert all data to floats
        #self.data = np.array([np.array([float(read) if read else np.nan for read in column]) for column in data])



    def create_envision_csv(path, name, tag=None, **kwargs):
        readout_dict_info, channel_wise_reads, channel_wise_info = readout_io.read_envision_csv(path, **kwargs)
        return Readout(name=name, data=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info, tag=tag)


    def create_insulin_csv(path, name, tag=None, **kwargs):
        readout_dict_info, channel_wise_reads, channel_wise_info = readout_io.read_insulin_csv(path, **kwargs)
        return Readout(name=name, data=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info, tag=tag)


    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``Readout`` instances.

        Serialize ``Readout`` instance using the stated ``format``.

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

