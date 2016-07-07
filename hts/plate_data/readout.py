# (C) 2015, 2016 Elke Schaper @ Vital-IT, Swiss Institute of Bioinformatics

"""
    :synopsis: The ``Readout`` Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@sib.swiss>
"""

import logging
import numpy as np

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



    def create_envision_csv(path, name, tag=None, type=None, **kwargs):
        readout_dict_info, channel_wise_reads, channel_wise_info = readout_io.read_envision_csv(path, **kwargs)
        if len(channel_wise_reads) == 0:
            raise Exception("No signal data determined in file {path} with method read_envision_csv. Please check file."
                            " In case file is correct, the current parsing does not work and either `read_envision_csv`"
                            " needs generalization, or a new parser needs to be written.".format(path=path))
        return Readout(name=name, data=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info, tag=tag, type=type)

    def create_insulin_csv(path, name, tag=None, type=None, **kwargs):
        readout_dict_info, channel_wise_reads, channel_wise_info = readout_io.read_insulin_csv(path, **kwargs)
        return Readout(name=name, data=channel_wise_reads, readout_dict_info=readout_dict_info, channel_wise_info=channel_wise_info, tag=tag, type=type)



