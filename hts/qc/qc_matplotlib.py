# (C) 2015 Elke Schaper

"""
    :synopsis: ``quality_control`` implementes all methods connected to the
    quality control of a high throughput screening experiment
    qc_matplotlib implements matplotlib specific methods.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import itertools
import logging
import math
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
import pickle
import re
import sys


from hts.readout import readout, readout_dict

LOG = logging.getLogger(__name__)

PATH = '/Users/elkeschaper/Downloads/'


#import pdb; pdb.set_trace()


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


def heat_map_single(data, file = "heat_map_plate.pdf", *args, **kwargs):
    """ Create a heat_map for a single readout

    Create a heat_map for a single readout

    ..todo:: Share code between heat_map_single and heat_map_multiple
    """

    np_data = data.data
    pp = PdfPages(os.path.join(PATH, file))

    fig, ax = plt.subplots()

    im = ax.pcolormesh(np_data, vmin=np_data.min(), vmax=np_data.max()) # cmap='RdBu'
    fig.colorbar(im)

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(np_data.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(np_data.shape[0]) + 0.5, minor=False)

    # Invert the y-axis such that the data is displayed as it appears on the plate.
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    ax.set_xticklabels(data.axes['x'], minor=False)
    ax.set_yticklabels(data.axes['y'], minor=False)

    pp.savefig(fig)
    pp.close()
    fig.clear()

    return ax


################ Readout_dict wise methods ####################

def heat_map_multiple(data, plate_tags = None, file = "heat_map_run.pdf", nPlates_max = 10, *args, **kwargs):
    """ Create a heat_map for multiple readouts

    Create a heat_map for multiple readouts

    """

    if "subset" in kwargs:
        subset = kwargs["subset"]
    else:
        subset = None

    plate_data = data.read_outs
    if not plate_tags:
        plate_tags = sorted(plate_data.keys())

    if len(plate_tags) > nPlates_max:
        plate_tags = plate_tags[::round(len(plate_tags)/nPlates_max)]

    a = math.ceil(len(plate_tags)/2)
    b = 2

    pp = PdfPages(os.path.join(PATH, file))

    data_min = min(plate_data[plate_tag].min() for plate_tag in plate_tags)
    data_max = max(plate_data[plate_tag].max() for plate_tag in plate_tags)

    #import pdb; pdb.set_trace()
    #plt.ioff()
    # Use axes.ravel() instead ????
    fig, axes = plt.subplots(a, b, sharex='col', sharey='row')
    if a > 1 and b > 1:
        laxes = [item for sublist in axes for item in sublist]
    else:
        laxes = axes
    #ax1.set_title('Sharing x per column, y per row')

    for plate_tag, ax in zip(plate_tags, laxes):
        idata = plate_data[plate_tag]
        im = ax.pcolormesh(idata.data, vmin=data_min, vmax=data_max) # cmap='RdBu'

        # put the major ticks at the middle of each cell
        ax.set_xticks(np.arange(idata.data.shape[1]) + 0.5, minor=False)
        ax.set_yticks(np.arange(idata.data.shape[0]) + 0.5, minor=False)

        # Invert the y-axis such that the data is displayed as it appears on the plate.
        ax.invert_yaxis()
        ax.xaxis.tick_top()

        ax.set_xticklabels(idata.axes['x'], minor=False)
        ax.set_yticklabels(idata.axes['y'], minor=False)

    # Fine-tune figure; hide x ticks for top plots and y ticks for right plots. Source: http://matplotlib.org/examples/pylab_examples/subplots_demo.html
    if a > 1 and b > 1:
        #plt.setp([ax.get_xticklabels() for ax in laxes], visible=False)
        plt.setp([ax.get_xticklabels() for ax in axes[0, :]], visible=True)
        plt.setp([ax.get_yticklabels() for ax in axes[:, 1]], visible=False)
    else:
        plt.setp(laxes[1].get_xticklabels(), visible=False)

    matplotlib.rcParams.update({'font.size': 2.5})
    plt.subplots_adjust(left=0.1, right=0.5, top=0.9, bottom=0.1)
    cbar = fig.colorbar(im, ax=axes.ravel().tolist())
    #import pdb; pdb.set_trace()
    cbar.ax.set_position((0.45, 0.4, 0.2, 0.2))

    pp.savefig(fig, dpi=20, bbox_inches='tight')
    #plt.show()
    pp.close()
    fig.clear()

    return axes
