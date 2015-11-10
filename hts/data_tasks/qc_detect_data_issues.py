# (C) 2015 Elke Schaper

"""
    :synopsis: ``qc_detect_data_issues`` implements methods to apply specified thresholds, and declare data that does not
    comply with this cut-offs, either in terms of a Run instance with truncated data, or a Data issue file.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import numpy as np
import os

LOG = logging.getLogger(__name__)



def detect_low_cell_viability(run, path, sample_type, control_readout_tag, sample_readout_tag, *args, **kwargs):
    """
    Detect which wells suffer from low cell viability by too strong divergence of a base value.
    As a practical example, RealTime-Glo measurements are performed for all wells. Sample wells that deviate > x
    from nominal control wells are considered to have "issues".

    """

    if not os.path.exists(os.path.dirname(path)):
        LOG.debug("Create dir: {}".format(path))
        os.makedirs(os.path.dirname(path))

    results = {}
    for plate_name, plate in run.plates.items():

        ## Calculate condition. E.g. what is the distribution of the control?
        filter_args = {"condition_data_type": "plate_layout",
                       "condition_data_tag": "layout_general_type",
                       "condition": lambda x: x in sample_type,
                       "value_data_type": "readout",
                       "value_data_tag": control_readout_tag}
        import pdb; pdb.set_trace()
        control_data = plate.filter(**filter_args)
        lower_limit = np.mean(control_data) - 1
        upper_limit = np.mean(control_data) + 1

        ## Apply condition. E.g., which wells do diverge too much from the distribution of the control?
        wells = plate.readout.get_wells(data_tag=sample_type, condition=lambda x: x < lower_limit or x > upper_limit)

        # Which wells are sample wells?
        sample_wells = plate.plate_layout.get_wells(data_tag="layout_general_type", condition=lambda x: x==sample_readout_tag)

        platewise_path = os.path.join(path, "{}.csv".format(plate_name))

        with open(platewise_path, "w") as fh:
            fh.write(wells)

        results[plate_name] = wells

    return results

