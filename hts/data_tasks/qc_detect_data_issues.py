# (C) 2015 Elke Schaper

"""
    :synopsis: ``qc_detect_data_issues`` implements methods to apply specified thresholds, and declare data that does not
    comply with this cut-offs, either in terms of a Run instance with truncated data, or a Data issue file.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import logging
import numpy as np
import os
from scipy import stats

from hts.plate_data.data_issue import DataIssue

LOG = logging.getLogger(__name__)



def detect_low_cell_viability(run, control_readout_tag, control_sample_type, controlled_sample_types, data_issue_tag, path, alpha=0.05, *args, **kwargs):
    """
    Detect which wells suffer from low cell viability by too strong divergence of a base value.
    As a practical example, RealTime-Glo measurements are performed for all wells. Sample wells that deviate > x
    from nominal control wells are considered to have "issues".

    Args:
        run (run.Run):  A Run instance.
        control_readout_tag (str): Tag of the control experiment readout (e.g. RealTime-Glo)
        control_sample_type (str): sample_type used as control.
        controlled_sample_types (list of str): sample_types that will be evaluated in reference to `control_sample_type`
        data_issue_tag (str): Tag of the data issue data that is created.
        path (str): Path to data issue result file.
        alpha (float): Significance level for Real-TimeGlo cut-off.
    """

    if not os.path.exists(os.path.dirname(path)):
        LOG.debug("Create dir: {}".format(path))
        os.makedirs(os.path.dirname(path))

    results = {}
    for plate_name, plate in run.plates.items():

        ## Calculate condition. E.g. what is the distribution of the control?
        filter_args = {"condition_data_type": "plate_layout",
                       "condition_data_tag": "layout_general_type",
                       "condition": lambda x: x in control_sample_type,
                       "value_data_type": "readout",
                       "value_data_tag": control_readout_tag}
        control_data = plate.filter(**filter_args)

        # What are the critical values of the control distribution, assuming it follows a normal distribution?
        critical_value_standard_normal = stats.norm.ppf(1-alpha)
        critical_value_control_lower_limit = np.mean(control_data) - critical_value_standard_normal * np.std(control_data)
        critical_value_control_upper_limit = np.mean(control_data) + critical_value_standard_normal * np.std(control_data)

        ## Apply condition. E.g., which wells do diverge too much from the distribution of the control?
        wells = plate.readout.get_wells(data_tag=control_readout_tag, condition=lambda x: x < critical_value_control_lower_limit or x > critical_value_control_upper_limit)
        data_issue = DataIssue.create_well_list(well_list=wells, width=plate.width, height=plate.height, data_tag=data_issue_tag)
        plate.add_data(data_type="data_issues", data=data_issue)

        # Which wells are sample wells?
        sample_wells = plate.plate_layout.get_wells(data_tag="layout_general_type", condition=lambda x: x in controlled_sample_types)

        platewise_path = os.path.join(path, "{}.csv".format(plate_name))
        data_issue.write(format="csv", path=platewise_path, tag=data_issue_tag)

        results[plate_name] = wells

    return results

