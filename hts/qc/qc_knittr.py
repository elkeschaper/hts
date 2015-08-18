# (C) 2015 Elke Schaper

"""
    :synopsis: ``quality_control`` implementes all methods connected to the
    quality control of a high throughput screening experiment.
    qc_knittr implements knittr specific methods.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import os
import re
import sys

from hts.readout import readout, readout_dict

LOG = logging.getLogger(__name__)

PATH = '/Users/elkeschaper/Downloads/'

def perform_qc(methods, data, *args, **kwargs):
    local_methods = {getattr(sys.modules[__name__], method_name): methods[method_name] for method_name in methods.keys()}
    #import pdb; pdb.set_trace()
    if not (type(data) == readout.Readout or type(data) == readout_dict.ReadoutDict):
        if type(data) == dict:
            data = readout_dict.ReadoutDict(read_outs = data)
        else:
            data = readout.Readout(data)
    results = [i(data, **param) for i, param in local_methods.items()]
    ### ADD: combine results (e.g. for R add data printout)
    return results

################ Readout wise methods ####################


def heat_map_single(data, *args, **kwargs):
    """ Create knittr code for a heat_map for a single readout

    Create knittr code for a heat_map for a single readout
    """

    return None


################ Readout_dict wise methods ####################

def heat_map_multiple(data, plate_tags = None, file = "heat_map_run.pdf", nPlates_max = 10, *args, **kwargs):
    """ Create knittr code for a heat_map for multiple readouts

    Create knittr code for a heat_map for for multiple readouts
    """

    return None