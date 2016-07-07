# (C) 2015 Elke Schaper

"""
    :synopsis: The DataIssue Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
from hts.plate_data import plate_data

LOG = logging.getLogger(__name__)


class DataIssue(plate_data.PlateData):

    """ ``DataIssue`` describes all information connected to the plate_data of a
    high throughput screen.

    Attributes:
        sample_replicate_count (str): (Explain!)
        layout_general_type (list of lists): The plate layout (explain!)

    """

    def __init__(self, data, **kwargs):
        # Perform DataIssue specific __init__

        # Run super __init__
        super().__init__(data=data, **kwargs)


    @classmethod
    def create_well_list(cls, well_list, width, height, data_tag, **kwargs):
        """

        Args:
            well_list (list of tuple):  List of wells with data issues, given as coordinate tuples (rowi, columni)
            width (int): Width of the well plate
            height (int): Height of the well plate
            data_tag (str): Tag of the created data
        """

        data = [[True for i in range(width)] for row in range(height)]
        for well in well_list:
            data[well[0]][well[1]] = False

        return cls(data={data_tag: data}, **kwargs)

