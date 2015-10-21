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
        self.width = len(next(iter(self.data.values()))[0])

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


    def create(self, *args, **kwargs):
        raise NotImplementedError('Implement create()')


    def write(self, *args, **kwargs):
        raise NotImplementedError('Implement write()')