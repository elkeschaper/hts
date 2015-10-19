# (C) 2015 Elke Schaper

"""
    :synopsis: ``qc_detect_data_issues`` implements methods to apply specified thresholds, and declare data that does not
    comply with this cut-offs, either in terms of a Run instance with truncated data, or a Data issue file.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import collections
import datetime
import logging
import os
import sys

from hts.readout import readout, readout_dict

LOG = logging.getLogger(__name__)



def detect_low_cell_viability(run, result_path, *args, **kwargs):
    """
    Detect which wells suffer from low cell viability by too strong divergence of a base value.
    As a pratical example, RealTime-Glo measurements are performed for all wells. Sample wells that deviate > x
    from nominal control wells are considered to have "issues".

    """

    if not os.path.exists(os.path.dirname(result_path)):
        LOG.debug("Create dir: {}".format(result_path))
        os.makedirs(os.path.dirname(result_path))

    with open(result_path, "w") as fh:
        fh.write("TEST")

    return {"TEST": "TEST"}

