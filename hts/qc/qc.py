# (C) 2015 Elke Schaper

"""
    :synopsis: The QualityControl Class.

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
from string import ascii_uppercase
import sys


LOG = logging.getLogger(__name__)


class QualityControl:

    """ ``QualityControl`` describes all information connected to the quality
        control of a high throughput screening experiment

    Attributes:
        run_data (dict of np.array of np.array): The data on which to perform QC.
        plate_layout (list of list of str): Mapping the plates to positives
                controls (pos_k), negative controls (neg_k) and so on.


    ..todo:: Implement.
    """

    def __init__(self, run_data, plate_layout = None, methods = None, **kwargs):

        # convert all data to floats.
        if not type(run_data) == dict:
            raise Exception("run_data is not of type dict: "
                    " {}".format(run_data))

        self.run_data = {plate_tag: np.array([np.array([float(read) for read in column]) for column in row]) for plate_tag, row in run_data.items()}
        self.plate_layout = plate_layout
        #import pdb; pdb.set_trace()
        if methods:
            self.methods = [getattr(sys.modules[__name__].QualityControl, method_name) for method_name in methods]
        self.width = len(list(run_data.values())[0][0])
        self.height = len(list(run_data.values())[0])
        self.path = '/Users/elkeschaper/Downloads/'
        if self.height <= len(ascii_uppercase):
            self.axes = {"x": list(range(1, self.width + 1)), "y": ascii_uppercase[:self.height]}
        else:
            raise Exception("Add plate letters for large plates. Plate height:"
                    " {}".format(self.height))


    def perform_qc(self, *args, **kwargs):
        for method in self.methods:
            method(self, *args, **kwargs)

    ################ Plate wise methods ####################

    def get_subset(self, tag):
        """ Return subset of run_data with plate_layout "type" only

        Return subset of run_data with plate_layout "type" only

        ..todo:: Implement
        """

        type = []
        for i,j in itertools.product(self.width, self.height):
            if self.plate_layout[i][j] == tag:
                type.append((i,j))

        run_data = {plate_tag: [data[c[0]][c[1]] for c in type] for plate_tag, data in self.run_data.items()}
        return run_data


    def heat_map_plate(self, plate_tag, file = "heat_map_plate.pdf", *args, **kwargs):
        """ Create a heat_map for the plate with plate_tag ``plate``

        Create a heat_map for the plate with plate_tag ``plate``

        ..todo:: Share code between heat_map_run and heat_map_plate
        """

        pp = PdfPages(os.path.join(self.path, file))

        plate_data = self.run_data[plate_tag]

        fig, ax = plt.subplots()

        im = ax.pcolormesh(plate_data, vmin=plate_data.min(), vmax=plate_data.max()) # cmap='RdBu'
        fig.colorbar(im)

        # put the major ticks at the middle of each cell
        ax.set_xticks(np.arange(plate_data.shape[1]) + 0.5, minor=False)
        ax.set_yticks(np.arange(plate_data.shape[0]) + 0.5, minor=False)

        # Invert the y-axis such that the data is displayed as it appears on the plate.
        ax.invert_yaxis()
        ax.xaxis.tick_top()

        ax.set_xticklabels(self.axes['x'], minor=False)
        ax.set_yticklabels(self.axes['y'], minor=False)

        pp.savefig(fig)
        pp.close()
        fig.clear()

        return ax


    ################ Run wise methods ####################

    def heat_map_run(self, plate_tags = None, file = "heat_map_run.pdf", nPlates_max = 10, *args, **kwargs):
        """ Create a heat_map for all plates in the run

        Create a heat_map for all plates in the run

        """

        if not plate_tags:
            plate_tags = sorted(self.run_data.keys())

        if len(plate_tags) > nPlates_max:
            plate_tags = plate_tags[::round(len(plate_tags)/nPlates_max)]

        a = math.ceil(len(plate_tags)/2)
        b = 2

        pp = PdfPages(os.path.join(self.path, file))

        data_min = min(self.run_data[plate_tag].min() for plate_tag in plate_tags)
        data_max = max(self.run_data[plate_tag].max() for plate_tag in plate_tags)

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
            plate_data = self.run_data[plate_tag]
            im = ax.pcolormesh(plate_data, vmin=data_min, vmax=data_max) # cmap='RdBu'

            # put the major ticks at the middle of each cell
            ax.set_xticks(np.arange(plate_data.shape[1]) + 0.5, minor=False)
            ax.set_yticks(np.arange(plate_data.shape[0]) + 0.5, minor=False)

            # Invert the y-axis such that the data is displayed as it appears on the plate.
            ax.invert_yaxis()
            ax.xaxis.tick_top()

            ax.set_xticklabels(self.axes['x'], minor=False)
            ax.set_yticklabels(self.axes['y'], minor=False)

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
