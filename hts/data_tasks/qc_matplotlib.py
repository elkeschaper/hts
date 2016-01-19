# (C) 2015 Elke Schaper

"""
    :synopsis: ``quality_control`` implementes all methods connected to the
    quality control of a high throughput screening experiment
    qc_matplotlib implements matplotlib specific methods.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import math

import matplotlib

matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1 import AxesGrid
import numpy as np


LOG = logging.getLogger(__name__)


def create_report(*args, **kwargs):
    """
    This methods is expected by run.Run .
    Todo: Needs implementation if Matplotlib reports are required.
    """

    return None


################ Readout wise methods ####################


def heat_map_single(run, data_tag,  result_file=None, *args, **kwargs):
    """ Create a heat_map for a single plate

    Create a heat_map for a single plate

    ..todo:: Share code between heat_map_single and heat_map_multiple
    """


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

    if result_file:
        pp = PdfPages(result_file)
        pp.savefig(fig, dpi=20, bbox_inches='tight')
        pp.close()

    fig.clear()

    return ax


################ Batch wise methods ####################


def heat_map_multiple(run, data_tag, result_file=None, n_plates_max=10, *args, **kwargs):
    """ Create a heat_map for multiple readouts

    Create a heat_map for multiple readouts

    """

    data = run.filter(value_data_type="readout", value_data_tag=data_tag, return_list=False, **kwargs)

    # Invert all columns (to comply with naming standards in HTS).
    # Unfortunately, simply inverting the y-axis did not seem to work.
    data = [plate[::-1] for plate in data]

    data = np.array(data)

    plate_tags = run.plates.keys()

    if len(plate_tags) > n_plates_max:
        plate_tags = plate_tags[::round(len(plate_tags)/n_plates_max)]

    a = math.ceil(len(plate_tags)/2)
    b = 2

    fig = plt.figure()

    grid = AxesGrid(fig, 111,
                    nrows_ncols=(b, a),
                    axes_pad=0.05,
                    share_all=True,
                    label_mode="L",
                    cbar_location="right",
                    cbar_mode="single",
                    )

    for val, ax in zip(data,grid):
        im = ax.imshow(val)

    grid.cbar_axes[0].colorbar(im)

    for cax in grid.cbar_axes:
        cax.toggle_label(False)

    if result_file:
        pp = PdfPages(result_file)
        pp.savefig(fig, dpi=20, bbox_inches='tight')
        pp.close()

    fig.set_size_inches(30, 14, forward=True)
    plt.show()

    # Do we need this line?
    #fig.clear()
