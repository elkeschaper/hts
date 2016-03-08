# (C) 2016 Elke Schaper

"""
    :synopsis: ``data_normalization`` implements methods connected to the
    readout normalization of a high throughput screening experiment

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging

LOG = logging.getLogger(__name__)

KERNEL_CHOICE = {
    "standard_squared_exponential": {"kernels": [("RBF", {}, {})]},
    "standard_matern32": {"kernels": [("Matern32", {}, {})]},
    "white_noise": {"kernels": [("White", {}, {})]},
    "standard_squared_exponential__stdperiodic_row": {"kernels": [("RBF", {}, {}), ("StdPeriodic", {"ARD1": True}, {"wavelengths": ("fix", [400, 2])})]},
    "standard_squared_exponetial__stdperiodic_free": {"kernels": [("RBF", {}, {}), ("StdPeriodic", {"ARD1": True}, {})]},
}


def apply_gaussian_process_normalization(run,
                                         data_tag_readout,
                                         sample_tag_input="s",
                                         result_tag_predicted="{data_tag_readout}_predicted_error_{kernel}",
                                         result_tag_normalized="{data_tag_readout}_normalized_readout_{kernel}",
                                         kernels=KERNEL_CHOICE,
                                         **kwargs):
    """ Perform Gaussian process normalization

    Perform Gaussian process normalization.
    Execute indirectly by: data_tasks.perform_task(run=run, task_name="data_normalization.apply_gaussian_process_normalization" *args, **kwargs)
    Execute directly by: data_normalization.apply_gaussian_process_normalization(run=run, *args, **kwargs)

    ..todo:: Add methods
    """

    for plate_tag, plate in run.plates.items():
        LOG.info("Applying Gaussian process on plate {}.".format(plate_tag))
        for kernel_name, kernel in kernels.items():

            tag_predicted_tmp = result_tag_predicted.format(kernel=kernel_name, data_tag_readout=data_tag_readout)
            tag_normalized_tmp = result_tag_normalized.format(kernel=kernel_name, data_tag_readout=data_tag_readout)

            m, predictions_mean_abs, predictions_sd = \
            plate.apply_gaussian_process(data_tag_readout=data_tag_readout,
                                         sample_tag_input=sample_tag_input,
                                         data_tag_prediction=tag_predicted_tmp,
                                         **kernel, **kwargs)

            # Save the difference as a new readout.
            normalized_data = run.plates[plate_tag].readout.data[data_tag_readout] - run.plates[plate_tag].readout.data[tag_predicted_tmp]
            run.plates[plate_tag].readout.add_data(data={tag_normalized_tmp: normalized_data}, tag=tag_normalized_tmp)
