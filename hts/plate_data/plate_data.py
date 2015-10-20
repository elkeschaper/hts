# (C) 2015 Elke Schaper

"""
    :synopsis: The PlateData Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import itertools
import logging
import string


LOG = logging.getLogger(__name__)


PLATE_LETTERS = list(string.ascii_uppercase) + ["".join(i) for i in itertools.product(string.ascii_uppercase, string.ascii_uppercase)]


class PlateData:

    """ ``PlateData`` describes arbitrary data for all wells in a plate.

    Attributes:
        width (int): Width of the plate
        height (int): Height of the plate
        data (dict of lists of lists): A dict of same-sized matrices with arbitrary data

    """

    def __str__(self):
        """
            Create string for Readout instance.
        """
        try:
            data = ("<PlateData instance>\nContains a list of lists."
                    "\nwidth: {}\nheight: {}".format(self.width, self.height))
        except:
            data = "<PlateData instance>"
            LOG.warning("Could not create string of PlateData instance.")

        return data


    def __init__(self, data, **kwargs):

        self.data = data
        self.height = len(next(iter(self.data.values())))
        self.height = len(next(iter(self.data.values()))[0])

        if "name" in kwargs:
            self.name = kwargs.pop("name")

         for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

        # You may want to shift this to plate... also get inspired HTS sample trace.
        if self.height <= len(PLATE_LETTERS):
            self.axes = {"x": list(range(1, self.width + 1)), "y": PLATE_LETTERS[:self.height]}
        else:
            raise Exception("Add plate letters for large plates. Plate height:"
                    " {}".format(self.height))


"""
Readout:
        # Convert all data to floats
        self.data = np.array([np.array([float(read) if read else np.nan for read in column]) for column in data])


"""

"""
PlateLayout:


        # Get short forms of well content. E.g. s_1 -> s
        # Assuming that the short forms are marked by the underscore character "_"
        deliminator = "_"
        self.layout_general_type = [[j.split(deliminator)[0] for j in i] for i in layout]

        # Define sample replicates. Traverse row-wise, the first occurence is counted as replicate 1, and so on.
        counter = {i:1 for i in set([item for sublist in layout for item in sublist])}
        sample_replicate_count = np.zeros((self.height, self.width))
        for iRow, iColumn in itertools.product(range(self.height), range(self.width)):
            type = layout[iRow][iColumn]
            sample_replicate_count[iRow][iColumn] = counter[type]
            counter[type] += 1
        self.sample_replicate_count = sample_replicate_count
"""