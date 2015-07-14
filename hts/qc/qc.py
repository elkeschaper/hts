# (C) 2015 Elke Schaper

"""
    :synopsis: The QualityControl Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import os
import numpy as np
import pickle
import re



LOG = logging.getLogger(__name__)


class QualityControl:

    """ ``QualityControl`` describes all information connected to the quality
        control of a high throughput screening experiment

    Attributes:
        run_data (dict of np.array of np.array): The data on which to perform QC.
        plate_map (list of list of str): Mapping the plates to positives
                controls (pos_k), negative controls (neg_k) and so on.


    ..todo:: Implement.
    """

    def __init__(self, run_data, plate_map = None, **kwargs):

        self.run_data = run_data
        self.plate_map = plate_map



    ################ Plate wise methods ####################

    def heat_map_plate(self, plate, *args, **kwargs):
        """ Create a heat_map for the plate with plate_tag ``plate``

        Create a heat_map for the plate with plate_tag ``plate``


        .. todo:: Implement.
        """

        print("Heatmap plate")

    ################ Run wise methods ####################

    def heat_map_run(self, *args, **kwargs):
        """ Create a heat_map for all plates in the run

        Create a heat_map for all plates in the run


        .. todo:: Implement.
        """

        print("Heatmap run")