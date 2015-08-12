# (C) 2015 Elke Schaper

"""
    :synopsis: ``analysis`` implementes all methods connected to the
    analysys of a high throughput screening experiment

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import itertools
import logging
import numpy as np
import os
import pickle
import re
import sys

from hts.readout import readout, readout_dict

LOG = logging.getLogger(__name__)

PATH = '/Users/elkeschaper/Downloads/'


#import pdb; pdb.set_trace()


def perform_analysis(methods, data, *args, **kwargs):
    local_methods = {getattr(sys.modules[__name__], method_name): methods[method_name] for method_name in methods.keys()}
    #import pdb; pdb.set_trace()
    if not (type(data) == readout.Readout or type(data) == readout_dict.ReadoutDict):
        if type(data) == dict:
            data = readout_dict.ReadoutDict(read_outs = data)
        else:
            data = readout.Readout(data)
    results = [i(data, *args, **kwargs) for i, param in local_methods.items()]
    ### ADD: combine results (e.g. for R add data printout)
    return results

################ Readout wise methods ####################


def perform_prion_fitting(data, file = "tata", *args, **kwargs):
    """ Perform prion fitting

    Perform prion fitting

    ..todo:: Add methods
    """

    from hts.analysis import analysis_prion_propagation_model as appm

    if 'plate_layout' in kwargs:
        plate_layout = kwargs['plate_layout']
    else:
        raise ValueError('plate_layout is not in kwargs. Check e.g. definitions in the run config file.')
    if 'dpia_dilution' in kwargs:
        dpia_dilution = kwargs['dpia_dilution']
    else:
        raise ValueError('dpia_dilution is not in kwargs. Check e.g. definitions in the run config file.')

    results = {}

    for dpia_experiment_tag, dpia_plates in dpia_dilution.items():
        LOG.info("dpia_experiment_tag: {}, dpia_plates: {}".format(dpia_experiment_tag, dpia_plates))
        dilutions = [float(i) for i in dpia_plates.values()]
        LOG.info(dilutions)
        all_thresholds=np.zeros([100,len(dilutions)]) # Legacy code - clean up
        all_frac_below=np.zeros([100,len(dilutions)]) # Legacy code - clean up
        #for dpia_tag, dpia_dilution in dpia_plates.items():
        for i_dilution, dpia_dilution in enumerate(dilutions):
            dpia_tag = next((dpia_tag for dpia_tag, i_dpia_dilution in dpia_plates.items() if float(i_dpia_dilution) == dpia_dilution), None)
            LOG.info("dpia_tag: {};  dpia_dilution: {}".format(dpia_tag, dpia_dilution))
            sample_y = data.read_outs[dpia_tag].filter_wells("s_0")
            neg_control_y = data.read_outs[dpia_tag].filter_wells("neg")
            # Legacy code - clean up:
            temp=appm.neg_control_normaliser(sample_y,neg_control_y) # returns a vector of the fraction of points below the threshold, as a function of the threshold, units are in terms of standard deviations of the negative control, zeroed to the mean of the negtive control.
            all_thresholds[:,i_dilution]=temp[:,0] # Legacy code - clean up
            all_frac_below[:,i_dilution]=temp[:,1] # Legacy code - clean up

        parameter_names, identifiers_all, parameters_all = appm.prion_fitter_input_parameters(dilutions_list=dilutions)
        LOG.debug(parameter_names)
        LOG.debug(identifiers_all)
        LOG.debug(parameters_all)
        LOG.debug(all_thresholds)
        LOG.debug(all_frac_below)

        parameters_fit, fitter_output, upper_errors,lower_errors= appm.fit_prion_model(all_thresholds, all_frac_below, parameters_all, identifiers_all, parameter_names, appm.prions_fbelow_sat, basinhops=1)

        n_propagons_per_well_undiluted_sample = parameters_fit[0,0]
        sum_squares_error = fitter_output['fun']
        plot_header = dpia_experiment_tag +'\nError(sum of squares) = %(err).1e, \nNumber of propagons per well in an undiluted sample = %(pri).1e' % {'err':sum_squares_error,'pri':n_propagons_per_well_undiluted_sample}
        appm.plot_prion_propagation_model_fit(appm.prions_fbelow_sat, parameters_fit, all_frac_below, all_thresholds, plot_header, dilutions, tag = dpia_experiment_tag)
        results[dpia_experiment_tag] = {"sum_squares_error": sum_squares_error, "n_propagons_per_well_undiluted_sample": n_propagons_per_well_undiluted_sample}

    import pdb; pdb.set_trace()
    return results