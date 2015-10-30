# (C) 2015 Elke Schaper

"""
    :synopsis: The PlateLayout Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import itertools
import logging
import numpy as np
import os
import pickle
import re

from hts.plate_data import plate_data_io
from hts.plate_data import plate_data

LOG = logging.getLogger(__name__)




class PlateLayout(plate_data.PlateData):

    """ ``PlateLayout`` describes all information connected to the plate_data of a
    high throughput screen.

    Vocabulary:
    neg_k: negative control k
    pos_k: positive control k
    s_k: sample k
    All other names may be used, but are not interpreted at current.

    Attributes:
        sample_replicate_count (str): (Explain!)
        layout_general_type (list of lists): The plate layout (explain!)

    """

    def __init__(self, layout, **kwargs):

        # Perform PlateLayout specific __init__

        # Get short forms of well content. E.g. s_1 -> s
        # Assuming that the short forms are marked by the underscore character "_"

        layout = [[datum.lower() for datum in row] for row in layout]

        deliminator = "_"
        layout_general_type = [[j.split(deliminator)[0] for j in i] for i in layout]

        # Define sample replicates. Traverse row-wise, the first occurence is counted as replicate 1, and so on.
        counter = {i:1 for i in set([item for sublist in layout for item in sublist])}
        sample_replicate_count = np.zeros_like(layout)
        for iRow, iColumn in itertools.product(range(len(layout)), range(len(layout[0]))):
            type = layout[iRow][iColumn]
            sample_replicate_count[iRow][iColumn] = counter[type]
            counter[type] += 1

        data = {"layout": layout, "layout_general_type": layout_general_type, "sample_replicate_count": sample_replicate_count}

        # Run super __init__
        super().__init__(data=data, **kwargs)


    @classmethod
    def create_csv(cls, path, name, **kwargs):
        data = plate_data_io.read_csv(path)
        return cls(name=name, layout=data)


    def invert(self):
        """ Create an inverted ``PlateLayout`` instance.

        Create an inverted ``PlateLayout`` instance.
        The misfortunate experimenter turned the plate by 180 degrees, such that the general plate layout needs
        to be adjusted.
        """

        inverted_layout = [[j for j in i[::-1]] for i in self.data["layout"][::-1]]
        return PlateLayout(name="{}_inverted".format(self.name), data={"layout": inverted_layout})


    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``PlateLayout`` instances.

        Serialize ``PlateLayout`` instance using the stated ``format``.

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