# (C) 2015 Elke Schaper

"""
    :synopsis: The PlateData Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import itertools
import os
import logging
import pickle
import string
import sys

from hts.plate_data import plate_data_io

LOG = logging.getLogger(__name__)


PLATE_LETTERS = list(string.ascii_uppercase) + ["".join(i) for i in itertools.product(string.ascii_uppercase, string.ascii_uppercase)]


class PlateData:

    """ ``PlateData`` describes arbitrary data for all wells in a plate.

    The keys of the the data dicts are referred to as "data_tag".

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
            data = ("{}\nContains a list of lists.\nwidth: {}\nheight: {}".format(type(self).__name__,
                                                                                  self.width, self.height))
        except:
            data = "<PlateData instance>"
            LOG.warning("Could not create string of PlateData instance.")

        return data


    def __init__(self, data, type=None, **kwargs):

        if type:
            self.data = {"{}_{}".format(type, i) :j for i,j in data.items()}
        else:
            self.data = data
        self.height = len(next(iter(self.data.values())))
        self.width = len(next(iter(self.data.values()))[0])

        if "name" in kwargs:
            self.name = kwargs.pop("name")

        if "tag" in kwargs:
            self.tags = [kwargs.pop("tag")]
        else:
            self.tags = []

        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


    def __iter__(self):
        """
            Iterates over data matrices.
        """
        for data_name, data in self.data.items():
            yield data


    def __getitem__(self, i):
        return list(self.data.values())[i]


    @classmethod
    def create(cls, formats, paths, configs=None, names=None, tags=None, types=None, **kwargs):
        """ Create ``PlateData`` instance.

        Create ``PlateData`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input; translates to a method.

        """

        if not names:
            names = [None]*len(formats)
        if not tags:
            tags = [None]*len(formats)
        if not configs:
            configs = [kwargs]*len(formats)
        if not types:
            types = [None]*len(formats)

        my_data_plate = None
        for format, path, name, tag, config, type in zip(formats, paths, names, tags, configs, types):
            create_method = "create_{}".format(format)
            try:
                create_method = getattr(cls, create_method)
            except:
                raise NotImplementedError('Method {} is currently not implemented.'.format(create_method))

            if not name:
                name = os.path.basename(path)
            my_data_tmp = create_method(path=path, name=name, tag=tag, type=type, **config)
            if not my_data_plate:
                my_data_plate = my_data_tmp
            else:
                my_data_plate.add_data(my_data_tmp.data, tag=tag)
        return my_data_plate


    @classmethod
    def create_csv(cls, path, name, tag=None, type=None, **kwargs):
        data = plate_data_io.read_csv(path, **kwargs)
        return cls(name=name, data={type: data}, tag=tag)


    @classmethod
    def create_excel(cls, path, name, tag=None, type=None, **kwargs):
        # This is a hack, such that information for multiple plates can be retrieved from a single plate (see run.py)
        tags = [path]
        path = kwargs.pop("file")
        data = plate_data_io.read_excel(path=path, tags=tags, **kwargs)
        return cls(name=name, data=data, tag=tag, type=type)


    @classmethod
    def create_pickle(cls, path, **kwargs):
        with open(path, 'rb') as fh:
            return pickle.load(fh)


    @classmethod
    def create_from_coordinate_tuple_dict(cls, data, width, height, **kwargs):
        """
        data is a dict: {tag: {(i_row, i_col): datum}}.
        """
        plate_data = {}
        for tag, tag_data in data.items():
            plate_data[tag] = [[tag_data[(i_row, i_col)] if (i_row, i_col) in tag_data else None for i_col in range(width)] for i_row in range(height)]
        return cls(data=plate_data, **kwargs)


    def write(self, *args, **kwargs):
        raise NotImplementedError('Implement write()')


    def add_data(self, data, tag=None):

        if any([i in data for i in self.data.keys()]):
            LOG.warning("Overwriting data keys from {} to {}.".format(self.data.keys(), data.keys()))

        self.data.update(data)

        if tag:
            self.tags += [tag]*len(data)
        else:
            LOG.warning("No tags were supplied.")


    def get_data(self, data_tag):

        if data_tag not in self.data:
            raise Exception("data_tag {} not in self.data: {}".format(data_tag, sorted(self.data.keys())))

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
        if len(well_coordinates) == 0:
            LOG.warning("Under the applied condition (e.g. names for the plate layout), no wells are chosen")

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

