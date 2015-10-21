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


    def add_data(self, data_tag, data):

        if data_tag in self.data:
            LOG.warning("data_tag {} already in self.data - overwriting".format(data_tag))

        self.data[data_tag] = data


    def get_data(self, data_tag):

        if data_tag not in self.data:
            raise Exception("data_tag {} not in self.data: {}".format(data_tag, self.data.keys()))

        return self.data[data_tag]


    def get_wells(self, data_tag, condition):
        """ Get list of well coordinates for which the data tagged with `data_tag` conforms to `condition`.

        Get list of well coordinates for which the data tagged with `data_tag` conforms to `condition`.

        Args:
            data_tag (str): Data tag.
            condition (method): The condition expressed as a method. E.g., condition=lambda x: x==True

        Returns:
            (list of (int, int)).
        """

        if data_tag in self.data:
            data = self.data[data_tag]
        else:
            raise Exception("data_tag {} not in self.data {}".format(data_tag, self.data.keys()))

        well_coordinates = [cc for cc in itertools.product(range(self.height), range(self.width)) if condition(data[cc[0]][cc[1]])]

        return well_coordinates


    def get_values(self, wells, data_tag, value_type=None):
        """ Get list of values for defined `wells` of the data tagged with `data_tag`.

        Get list of values for defined `wells` of the data tagged with `data_tag`.
        If `value_type` is set, check if all values conform with `value_type`.

        Args:
            wells (lists of tuple):  List of well coordinates.
            data_tag (str): Data tag.
            value_type (str): The type of the return values.

        Returns:
            (list of x), where x are of type `value_type`, if `value_type` is set.
        """

        if data_tag in self.data:
            data = self.data[data_tag]
        else:
            raise Exception("data_tag {} not in self.data {}".format(data_tag, self.data.keys()))

        values = [data[cc[0]][cc[1]] for cc in wells]

        if value_type and not all([type(i) == value_type for i in values]):
            raise Exception("Not all values conform with value_type{}:\n{}".format(value_type, values))

        return values
