# (C) 2016 Elke Schaper

"""
    :synopsis: ``data_normalization`` implements methods connected to the
    readout normalization of a high throughput screening experiment

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

from distutils.util import strtobool
import logging

LOG = logging.getLogger(__name__)

KERNEL_CHOICE = {
    "standard_squared_exponential": {"kernels": [("RBF", {}, {})]},
    "standard_matern32": {"kernels": [("Matern32", {}, {})]},
    "white_noise": {"kernels": [("White", {}, {})]},
    "standard_squared_exponential__stdperiodic_row": {
        "kernels": [("RBF", {}, {}), ("StdPeriodic", {"ARD1": True}, {"wavelengths": ("fix", [400, 2])})]},
    "standard_squared_exponetial__stdperiodic_free": {
        "kernels": [("RBF", {}, {}), ("StdPeriodic", {"ARD1": True}, {})]},
}




def do_gaussian_process_normalization(run,
                                      data_tag_readout,
                                      methods,
                                      sample_tag_input="s",
                                      result_tag_predicted="{data_tag_readout}__{sample_tag_input}__{kernel}__predicted",
                                      result_tag_normalized="{data_tag_readout}__{sample_tag_input}__{kernel}__normalized",
                                      method_tag="{method_name}_{sample_tag_input}",
                                      **kwargs):
    """ Perform Gaussian process normalization

    Perform Gaussian process normalization.
    Execute indirectly by: data_tasks.perform_task(run=run, task_name="data_normalization.apply_gaussian_process_normalization" *args, **kwargs)
    Execute directly by: data_normalization.apply_gaussian_process_normalization(run=run, *args, **kwargs)
    """

    kernels = {}
    for method_name, kernel_config in methods.items():
        # if method_name in KERNEL_CHOICE and len(kernel_config) == 0:
        #     logging.info("Using default Kernel config for {}".format(method_name))
        #     kernel_config = KERNEL_CHOICE[method_name]

        try:
            is_per_plate = kernel_config.pop('is_per_plate')
            if strtobool(is_per_plate) == 0:
                logging.error("runwise gaussian process normalization is currently not implemented.")
                continue
        except:
            logging.info("Could not evaluate is_per_plate - assuming is_per_plate==True.")

        try:
            is_zigzag = kernel_config.pop('is_zigzag')
            if strtobool(is_zigzag) == 1:
                logging.error("is_zig_zag gaussian process normalization is currently not implemented.")
                continue
        except:
            logging.info("Could not evaluate is_zigzag - assuming is_zigzag==False.")

        from hts.plate import prediction

        kernels[method_name] = prediction.create_gaussian_process_composite_kernel(input_dim=2, kernels=kernel_config.values())


    for plate_tag, plate in run.plates.items():
        LOG.info("Applying Gaussian process on plate {}.".format(plate_tag))

        for method_name, kernel in kernels.items():
            tag_predicted_tmp = result_tag_predicted.format(kernel=method_name, data_tag_readout=data_tag_readout, sample_tag_input=sample_tag_input)
            tag_normalized_tmp = result_tag_normalized.format(kernel=method_name, data_tag_readout=data_tag_readout, sample_tag_input=sample_tag_input)

            m, predictions_mean_abs, predictions_sd = \
                plate.apply_gaussian_process(data_tag_readout=data_tag_readout,
                                             sample_tag_input=sample_tag_input,
                                             data_tag_prediction=tag_predicted_tmp,
                                             kernel=kernel,
                                             **kwargs)

            m.hts_predicted_tag = tag_predicted_tmp
            m.hts_normalized_tag = tag_normalized_tmp
            plate.gp_model[method_tag.format(method_name=method_name, sample_tag_input=sample_tag_input)] = m

            # Save the difference as a new readout.
            normalized_data = plate.readout.data[data_tag_readout] - plate.readout.data[tag_predicted_tmp]
            plate.readout.add_data(data={tag_normalized_tmp: normalized_data}, tag=tag_normalized_tmp)

