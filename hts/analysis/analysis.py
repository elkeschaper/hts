# (C) 2015 Elke Schaper

"""
    :synopsis: ``analysis`` implements all methods connected to the
    analysis of a high throughput screening experiment

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import os
import sys

from fit.model import Model

#from fit.model_dpia_linear_ml import ModelDPIAML

from hts.plate import plate
from hts.plate_data import readout

LOG = logging.getLogger(__name__)

def perform_analysis(methods, data, *args, **kwargs):

    try:
        path = kwargs.pop("analysis_result_path")
    except:
        LOG.warning("analysis_result_path is not defined.")
        path = ""

    local_methods = {getattr(sys.modules[__name__], method_name): methods[method_name] for method_name in methods.keys()}
    #import pdb; pdb.set_trace()
    if not (type(data) == readout.Readout or type(data) == plate.Plate):
        if type(data) == dict:
            data = plate.Plate(read_outs = data)
        else:
            data = readout.Readout(data)
    results = [i(data, path=path, *args, **kwargs) for i, param in local_methods.items()]
    ### ADD: combine results (e.g. for R add data printout)
    return results

################ Readout wise methods ####################


def perform_prion_fitting(data, path, write_data=False, *args, **kwargs):
    """ Perform prion fitting

    Perform prion fitting

    ..todo:: Add methods
    """

    if 'plate_data' in kwargs:
        plate_layout = kwargs['plate_data']
    else:
        raise ValueError('plate_data is not in kwargs. Check e.g. definitions in the run config file.')
    if 'dpia_dilution' in kwargs:
        dpia_dilution = kwargs['dpia_dilution']
    else:
        raise ValueError('dpia_dilution is not in kwargs. Check e.g. definitions in the run config file.')

    if not path:
        LOG.info("path is not defined. The Fit library saves the plots to unknown location.")

    model_name = "dPIA"

    results = {}

    #For each run, several dPIA experiments are usually defined. Iterate through all dPIA experiments.
    for dpia_experiment_tag, dpia_plates in dpia_dilution.items():
        # For each dpia_experiment_tag, perform the dPIA fitting for all defined dilutions (which all contain "neg" and "s" data).

        # You need to delete this line if you wish to recalculate anything :)
        model_file_pickle = os.path.join(path, dpia_experiment_tag + ".fit.pickle")
        #if os.path.isfile(model_file_pickle):
        #    continue

        LOG.info("dpia_experiment_tag: {}, dpia_plates: {}".format(dpia_experiment_tag, dpia_plates))

        # Prepare the fit input
        # 1) plate_data
        plate_data = {plate_name: {"value": float(dilution)} for plate_name, dilution in dpia_plates.items()}
        model_parameters = {"dilution": {"type": "local", "plates": plate_data}}
        LOG.info(model_parameters)

        # 2) model_data. model_data needs to follows the following form:
        # {"plateA": {"neg": np.array([1,2,1]), "s": np.array([3,4,4,3])}, "plateB": {"neg": np.array([3,2,3]), "s": np.array([4,5,6,2])}, ...}
        model_data = {plate_name: {"neg": data.read_outs[plate_name].filter_wells("neg"), "sample": data.read_outs[plate_name].filter_wells("s")} for plate_name in dpia_plates.keys()}
        LOG.info(model_data)

        my_model = Model.create(origin="dict", model_class=ModelDPIAML, model_name=model_name, data=model_data, parameters=model_parameters)

        if not os.path.exists(path):
            LOG.warning("analysis: Create new directory: {}".format(path))
            os.makedirs(path)

        if write_data:
            model_datafile_pickle = os.path.join(path, dpia_experiment_tag + ".fit_data_only.pickle")
            my_model.write(format="pickle", path=model_datafile_pickle)
            continue

        # Todo: Delete the plates that did not go through qc and rerun...
        fit_parameters, optimisation_parameters = my_model.fit_model()

        my_model.result_report(result_file=os.path.join(path, dpia_experiment_tag + ".Rmd"),
                               result_data_file=os.path.join(path, dpia_experiment_tag + ".csv"))

        my_model.write(format="pickle", path=model_file_pickle)

        # Define the return values
        results[dpia_experiment_tag] = {"fit_parameters": fit_parameters['dict'], "optimisation_parameters": optimisation_parameters["dict"]}

    return results
