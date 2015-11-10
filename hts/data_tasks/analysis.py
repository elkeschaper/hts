# (C) 2015 Elke Schaper

"""
    :synopsis: ``analysis`` implements all methods connected to the
    analysis of a high throughput screening experiment

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import configobj
import logging
import os
import sys

from fit.model import Model
#from fit.model_dpia_linear_ml import ModelDPIAML

from hts.plate import plate
from hts.plate_data import readout

LOG = logging.getLogger(__name__)


################ Readout wise methods ####################


def perform_prion_fitting(run, tag, path, write_data=False, *args, **kwargs):
    """ Perform prion fitting

    Perform prion fitting

    ..todo:: Add methods
    """

    tmp = run

    general_filter_args = {i:j for i,j in kwargs.items() if not isinstance(j, configobj.Section)}
    dilution_wise_filter_args = {i:j for i,j in kwargs.items() if isinstance(j, configobj.Section)}
    dilutions = list(dilution_wise_filter_args.keys())

    if not path:
        LOG.info("path is not defined. The Fit library saves the plots to unknown location.")

    model_name = "dPIA"

    # Perform the dPIA fitting for all defined dilutions (which all contain "neg" and "s" data).
    # You need to delete this line if you wish to recalculate anything :)
    model_file_pickle = os.path.join(path, tag + ".fit.pickle")
    #if os.path.isfile(model_file_pickle):
    #    continue
    LOG.info("dpia_experiment_tag: {}, dpia_plates: {}".format(tag, dilution_wise_filter_args))

    # Prepare the fit input
    # 1) plate_data
    plate_data = {dilution: {"value": float(dilution)} for dilution in dilutions}
    model_parameters = {"dilution": {"type": "local", "plates": plate_data}}
    LOG.info(model_parameters)

    # 2) model_data. model_data needs to follows the following form:
    # {"plateA": {"neg": np.array([1,2,1]), "s": np.array([3,4,4,3])}, "plateB": {"neg": np.array([3,2,3]), "s": np.array([4,5,6,2])}, ...}

    model_data = {}
    for dilution, config in dilution_wise_filter_args.items():
        config_all = dict(config, **general_filter_args)
        sample = filter(run, **config_all)
        config_all["sample_type"] = ["neg"]
        neg = filter(run, **config_all)
        model_data[dilution] = {"neg": neg, "sample": sample}
    LOG.info(model_data)

    my_model = Model.create(origin="dict", model_class=ModelDPIAML, model_name=model_name, data=model_data, parameters=model_parameters)

    if not os.path.exists(path):
        LOG.warning("analysis: Create new directory: {}".format(path))
        os.makedirs(path)

    if write_data:
        model_datafile_pickle = os.path.join(path, tag + ".fit_data_only.pickle")
        my_model.write(format="pickle", path=model_datafile_pickle)
        return

    # Todo: Delete the plates that did not go through qc and rerun...
    fit_parameters, optimisation_parameters = my_model.fit_model()

    my_model.result_report(result_file=os.path.join(path, tag + ".Rmd"),
                           result_data_file=os.path.join(path, tag + ".csv"))

    my_model.write(format="pickle", path=model_file_pickle)

    # Define the return values
    results = {"fit_parameters": fit_parameters['dict'], "optimisation_parameters": optimisation_parameters["dict"]}

    return results


def filter(data, readout_tag, plates, sample_type, **kwargs):

    plate_wise_filter_args = {plate: {"condition_data_type": "plate_layout",
                                      "condition_data_tag": "layout_general_type",
                                      "condition": lambda x: x in sample_type,
                                      "value_data_type": "readout",
                                      "value_data_tag": readout_tag}
                             for plate in plates}

    return data.filter(plate_wise_filter_args=plate_wise_filter_args)