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
from mpl_toolkits.axes_grid1 import AxesGrid
import numpy as np

import GPy


LOG = logging.getLogger(__name__)


def create_report(*args, **kwargs):
    """
    This methods is expected by run.Run .
    Todo: Needs implementation if Matplotlib reports are required.
    """

    return None


################ Readout wise methods ####################


def heat_map_single(run, data_tag, plate_tag, **kwargs):
    """ Create a heat_map for a single plate

    Create a heat_map for a single plate
    """

    plate = run.plates[plate_tag]
    data = plate.filter(value_data_type="readout", value_data_tag=data_tag, return_list=False, **kwargs)

    # Invert all columns (to comply with naming standards in HTS).
    # Unfortunately, simply inverting the y-axis did not seem to work.
    #data = data[::-1]

    if not type(data) == np.ndarray:
        data = np.array(data)

    data = np.ma.array(data, mask=np.isnan(data))

    fig = plt.figure()
    plt.pcolor(data)
    plt.colorbar()
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
    ax.set_aspect('equal')

    #fig.set_size_inches(5, 4, forward=True)
    plt.show()


def heat_map_single_gaussian_process_model(run, data_tag_readout, sample_tag, plate_tag, magnification=5, *args, **kwargs):
    """ Create a heat_map for multiple readouts

    Create a heat_map for multiple readouts


model_as_gaussian_process(self, data_tag_readout, sample_key,
                                  kernel_type='m32',
                                  n_max_iterations=1000,
                                  plot_kwargs=False,

    """

    wells_high_resolution = list(itertools.product(np.arange(0,run.width,1/magnification), np.arange(0,run.height,1/magnification)))
    x_wells = np.array(wells_high_resolution)


    plate = run.plates[plate_tag]
    m, y_mean, y_std = plate.model_as_gaussian_process(data_tag_readout=data_tag_readout, sample_tag=sample_tag, **kwargs)
    y_predicted_mean, y_predicted_var = m.predict(x_wells)
    y_predicted_as_matrix = y_predicted_mean.reshape(magnification*run.width,magnification*run.height).transpose()

    fig = plt.figure()

    # im is of type matplotlib.image.AxesImage
    plt.imshow(y_predicted_as_matrix)
    plt.colorbar()
    plt.gca().invert_yaxis()
    fig.set_size_inches(5, 4, forward=True)
    plt.show()


def slice_single_gaussian_process_model(run, data_tag_readout, sample_tag, plate_tag, slice=5, **kwargs):
    """ Create a heat_map for multiple readouts

    Create a heat_map for multiple readouts


    # Currently: using Plotly.
    # Perhaps, matplotlib.axes._subplots.AxesSubplot can be integrated with Matplotlib's AxesGrid as above.
    """

    plate = run.plates[plate_tag]
    m, y_mean, y_std = plate.model_as_gaussian_process(data_tag_readout=data_tag_readout, sample_tag=sample_tag, **kwargs)

    m.plot(fixed_inputs=[(1,slice)], plot_data=False)



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




def heat_map_multiple_gaussian_process_model(run, data_tag_readout, sample_tag, result_file=None, magnification=5, n_plates_max=10, *args, **kwargs):
    """ Create a heat_map for multiple readouts

    Create a heat_map for multiple readouts
    """

    wells_high_resolution = list(itertools.product(np.arange(0,run.width,1/magnification), np.arange(0,run.height,1/magnification)))
    x_wells = np.array(wells_high_resolution)

    plate_tags = run.plates.keys()
    if len(plate_tags) > n_plates_max:
        plate_tags = plate_tags[::round(len(plate_tags)/n_plates_max)]

    a = math.ceil(len(plate_tags)/2)
    b = 2

    data = []
    for plate_tag in plate_tags:
        plate = run.plates[plate_tag]
        m, y_mean, y_std = plate.model_as_gaussian_process(data_tag_readout=data_tag_readout, sample_tag=sample_tag, **kwargs)
        y_predicted_mean, y_predicted_var = m.predict(x_wells)
        y_predicted_as_matrix = y_predicted_mean.reshape(magnification*run.width,magnification*run.height).transpose()
        data.append(y_predicted_as_matrix)



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
        # im is of type matplotlib.image.AxesImage


    grid.cbar_axes[0].colorbar(im)

    for cax in grid.cbar_axes:
        cax.toggle_label(False)

    if result_file:
        pp = PdfPages(result_file)
        pp.savefig(fig, dpi=20, bbox_inches='tight')
        pp.close()

    fig.set_size_inches(30, 14, forward=True)
    plt.show()




def slice_multiple_gaussian_process_model(run, data_tag_readout, sample_tag, result_file=None, slice=5, n_plates_max=10, *args, **kwargs):
    """ Create a heat_map for multiple readouts

    Create a heat_map for multiple readouts


    # Currently: using Plotly.
    # Perhaps, matplotlib.axes._subplots.AxesSubplot can be integrated with Matplotlib's AxesGrid as above.
    """



    plate_tags = run.plates.keys()
    if len(plate_tags) > n_plates_max:
        plate_tags = plate_tags[::round(len(plate_tags)/n_plates_max)]

    a = math.ceil(len(plate_tags)/2)
    b = 2

    models = []
    for plate_tag in plate_tags:
        plate = run.plates[plate_tag]
        m, y_mean, y_std = plate.model_as_gaussian_process(data_tag_readout=data_tag_readout, sample_tag=sample_tag, **kwargs)
        models.append(m)

    GPy.plotting.change_plotting_library('plotly')
    figure = GPy.plotting.plotting_library().figure(len(models), 1, shared_xaxes=True,)

    for i,m in enumerate(models):
        canvas = m.plot(figure=figure, fixed_inputs=[(1,slice)], row=(i+1), plot_data=False)
        # canvas is of type matplotlib.axes._subplots.AxesSubplot

    #grid.cbar_axes[0].colorbar(im)

    GPy.plotting.show(canvas, filename='basic_gp_regression_notebook_slicing')

    GPy.plotting.change_plotting_library('matplotlib')


