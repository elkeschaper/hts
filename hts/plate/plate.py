# (C) 2015 Elke Schaper

"""
    :synopsis: The Plate Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import ast
import itertools
import logging
import numpy as np
import os
import pickle
import re
import scipy.stats
import string

from hts.plate_data import plate_data, data_issue, plate_layout, readout

KNOWN_DATA_TYPES = ["plate_layout", "readout", "data_issue", "meta_data"]
LETTERS = list(string.ascii_uppercase) + ["".join(i) for i in itertools.product(string.ascii_uppercase, string.ascii_uppercase)]
MAX_WIDTH = 48
MAX_HEIGHT = 32
TRANSLATE_HUMANREADABLE_COORDINATE = {(LETTERS[cc[0]], str(cc[1]+1)): cc for cc in itertools.product(range(MAX_HEIGHT), range(MAX_WIDTH))}
TRANSLATE_COORDINATE_HUMANREADABLE = {cc: (LETTERS[cc[0]], str(cc[0]+1), str(cc[1]+1)) for cc in itertools.product(range(MAX_HEIGHT), range(MAX_WIDTH))}
LOG = logging.getLogger(__name__)


## TODO: Instead of creating a matrix for both coordinates, simply create a list each to safe memory.

def translate_coordinate_humanreadable(coordinate):

    return TRANSLATE_COORDINATE_HUMANREADABLE[coordinate]


def translate_humanreadable_coordinate(humanreadable):

    pattern = re.compile('([a-zA-Z]+)0*(\d+)')
    match = re.match(pattern, humanreadable)
    if not match:
        LOG.error("pattern: {} did not match {}".format(pattern, humanreadable))
    humanreadable = (match.group(1), match.group(2))

    return TRANSLATE_HUMANREADABLE_COORDINATE[humanreadable]


class Plate:

    """ ``Plate`` describes all information connected to the readout_dict
    of a high throughput screen. This could be either several readouts of a
    plate, or the same plate across several plates.

    Attributes:
        name (str): Name of the plate
        width (int): Width of the plate
        height (int): Height of the plate
        KNOWN_DATA_TYPES[i] (subclass of plate_data.PlateData): The data associated to this Plate, e.g. a plate layout,
                                                                or readouts.

    """

    def __str__(self):
        """
            Create string for Plate instance.
        """
        if hasattr(self, "name"):
            name = self.name
        else:
            name = "<not named>"
        try:
            readout_dict = ("<Plate instance>\nname: {}\nread_outs: {}"
                    "\nNumber of read_outs: {}\nwidth: {}\nheight: {}".format(name,
                    str(self.readout.data.keys()), len(self.readout.data),
                    self.width, self.height))
        except:
            readout_dict = "<Plate instance>"
            LOG.warning("Could not create string of Plate instance.")

        return readout_dict


    def __init__(self, data, name, **kwargs):

        LOG.debug(data)

        self.name = name

        for data_type in KNOWN_DATA_TYPES:
            if data_type in data:
                if not isinstance(data[data_type], plate_data.PlateData):
                    raise Exception("type of {} data is {}, not plate_data.PlateData.".format(data_type, type(data[data_type])))
                setattr(self, data_type, data[data_type])
            else:
                setattr(self, data_type, None)

        if "height" in kwargs:
            self.height = kwargs.pop("height")
        if "width" in kwargs:
            self.width = kwargs.pop("width")

        # You are using this construct in many an __init__ . Consider turning into decorator.
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

        """
        FORMERLY:
        # Make sure all readouts are equal in height and width.
        plate_heights = [i.height for i in self.readout.data.values()]
        plate_widths = [i.width for i in self.readout.data.values()]
        if len(set(plate_heights)) != 1 or len(set(plate_widths)) != 1:
            raise Exception("Plate widths and lengths in the parsed output "
                "files are not all equal: plate_heights: {}, plate_widths: {} "
                    "".format(plate_heights, plate_widths))

        """



    def create(format, name=None, **kwargs):
        """ Create ``Plate`` instance.

        Create ``Plate`` instance.

        Args:
            path (str): Path to input file or directory
            format (str):  Format of the input file, at current not specified

        """

        if format == "config":
            data = {}
            if "meta_data" in kwargs:
                data["meta_data"] = meta_data.MetaData.create(**kwargs["meta_data"])
            if "plate_layout" in kwargs:
                data["plate_layout"] = plate_layout.PlateLayout.create(**kwargs["plate_layout"])
            if "data_issue" in kwargs:
                data["data_issue"] = data_issue.DataIssue.create(**kwargs["data_issue"])
            if "readout" in kwargs:
                data["readout"] = readout.Readout.create(**kwargs["readout"])
            height = len(next(iter(next(iter(data.values())).data.values())))
            width = len(next(iter(next(iter(data.values())).data.values()))[0])
            if not name:
                name = next(iter(data.values())).name
            return Plate(data=data, height=height, width=width, name=name)
        elif format == 'pickle':
            with open(kwargs["path"], 'rb') as fh:
                return pickle.load(fh)
        else:
            raise Exception("Format: {} is not implemented in "
                            "Plate.create()".format(format))


    def add_data(self, data_type, data, force=False, tag=None):
        """ Add `data` of `data_type` to `self.meta_data`

        Add `data` of `data_type` to `self.meta_data`
        """

        if data_type == "meta_data" and not isinstance(data, meta_data.MetaData):
            raise Exception('data is not of type meta_data.MetaData, but {}'.format(type(data)))
        elif data_type == "plate_layout" and not isinstance(data, plate_layout.PlateLayout):
            raise Exception('data is not of type plate_layout.PlateLayout, but {}'.format(type(data)))
        elif data_type == "data_issue" and not isinstance(data, data_issue.DataIssue):
            raise Exception('data is not of type data_issue.DataIssue, but {}'.format(type(data)))
        elif data_type == "readout" and not isinstance(data, readout.Readout):
            raise Exception('data is not of type readout.Readout, but {}'.format(type(data)))

        if force or not hasattr(self, data_type) or not isinstance(getattr(self, data_type), plate_data.PlateData):
            setattr(self, data_type, data)
        else:
            getattr(self, data_type).add_data(data=data, tag=tag)


    def write(self, format, path=None, return_string=None, *args):
        """ Serialize and write ``Plate`` instances.

        Serialize ``Plate`` instance using the stated ``format``.

        Args:
            format (str):  The output format: Currently only "pickle".
            path (str): Path to output file

        .. todo:: Write checks for ``format`` and ``path``.
        """

        if format == 'pickle':
            with open(path, 'wb') as fh:
                pickle.dump(self, fh)
        else:
            raise Exception('Format is unknown: {}'.format(format))

        if path:
            with open(path, 'w') as fh:
                fh.write(output)
        if return_string:
            return output



    def filter(self, condition_data_type, condition_data_tag, condition, value_data_type, value_data_tag, value_type=None):
        """

        Get list of values for defined `wells` of the data tagged with `data_tag`.
        If `value_type` is set, check if all values conform with `value_type`.

        Args:
            condition_data_type (str): Reference to PlateData instance on which wells are filtered for the condition.
            condition_data_tag (str): Data tag for condition_data_type
            condition (method): The condition expressed as a method.
            value_data_type (str): Reference to PlateData instance from which (for filtered wells) the values are retrieved.
            value_data_tag (str): Data tag for value_data_type.
            value_type (str): The type of the return values.

        Returns:
            (list of x), where x are of type `value_type`, if `value_type` is set.
        """

        #if value_data_tag == "net_fret":
        #    import pdb; pdb.set_trace()

        condition_plate_data = getattr(self, condition_data_type)
        value_plate_data = getattr(self, value_data_type)

        wells = condition_plate_data.get_wells(data_tag=condition_data_tag, condition=condition)
        values = value_plate_data.get_values(wells=wells, data_tag=value_data_tag, value_type=value_type)

        return values


    #### Preprocessing functions

    def preprocess(self, methodname, **kwargs):

            method = getattr(self, methodname)
            method(**kwargs)


    def calculate_net_fret(self, donor_channel, acceptor_channel,
                            fluorophore_donor = "fluorophore_donor",
                            fluorophore_acceptor = "fluorophore_acceptor",
                            buffer = "buffer", net_fret_key = "net_fret"):
        """ Calculate the net FRET signal for a donor acceptor FRET setup.

        Calculate the net FRET signal for a donor acceptor FRET setup.
        Typical donor -> aceptor pairs include

        * 414nm CFP -> 475nm -> YFP 525nm
        * EU -> 615nm -> APC 665nm

        The following wells are needed, for both channels

        * `donor` Donor_fluorophor blank
        * `acceptor` Acceptor_fluorophor blank
        * `buffer` Buffer blank

        The proportionality factor for donor compensation is then calculation as
        .. math::

        p = \frac{\hat{donor_{acceptor_channel}} - \hat{buffer_{acceptor_channel}}}{\hat{donor_{donor_channel}} - \hat{buffer_{donor_channel}}}

        Further, the net FRET signal `f` for all wells `x` may be calculated as:
        .. math::

        netfret = x_{acceptor_channel} - \hat{acceptor_{acceptor_channel}} - p \cdot (x_{donor_channel} - \hat{buffer_{donor_channel}})

        Args:
            donor_channel (str):  The key for self.readout.data where the donor_channel ``Readout`` instance is stored.
            acceptor_channel (str):  The key for self.readout.data where the acceptor_channel ``Readout`` instance is stored.
            fluorophore_donor (str):  The name of the donor fluorophore in self.plate_data.
            fluorophore_acceptor (str):  The name of the acceptor fluorophore in self.plate_data.
            buffer (str):  The name of the buffer in self.plate_data.
            net_fret_key (str):  The key for self.readout.data where the resulting net fret ``Readout`` instance will be stored.

        """

        if net_fret_key in self.readout.data:
            LOG.warning("The net_fret_key {} is already in self.readout.data. "
                        "Skipping recalculation".format(net_fret_key))
            return

        mean_donor_donor_channel = np.mean(self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                       condition=lambda x: x==fluorophore_donor,
                                                       value_data_type="readout", value_data_tag=donor_channel))
        mean_acceptor_donor_channel = np.mean(self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                       condition=lambda x: x==fluorophore_acceptor,
                                                       value_data_type="readout", value_data_tag=donor_channel))
        mean_buffer_donor_channel = np.mean(self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                       condition=lambda x: x==buffer,
                                                       value_data_type="readout", value_data_tag=donor_channel))
        mean_donor_acceptor_channel = np.mean(self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                       condition=lambda x: x==fluorophore_donor,
                                                       value_data_type="readout", value_data_tag=acceptor_channel))
        mean_acceptor_acceptor_channel = np.mean(self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                       condition=lambda x: x==fluorophore_acceptor,
                                                       value_data_type="readout", value_data_tag=acceptor_channel))
        mean_buffer_acceptor_channel = np.mean(self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                       condition=lambda x: x==buffer,
                                                       value_data_type="readout", value_data_tag=acceptor_channel))

        for i, value in enumerate([mean_donor_donor_channel, mean_acceptor_donor_channel, mean_buffer_donor_channel, mean_donor_acceptor_channel, mean_acceptor_acceptor_channel, mean_buffer_acceptor_channel]):
            if np.isnan(value):
                import pdb; pdb.set_trace()
                raise ValueError("Calculation of variable {} resulted in {}. Check whether the plate layout is correctly assigned.".format(i, value))

        p = (mean_donor_acceptor_channel - mean_buffer_acceptor_channel) / (mean_donor_donor_channel - mean_buffer_donor_channel)


        # Calculate the net FRET signal for the entire plate
        # See TechNote #TNPJ100.04 PROzyme
        # http://prozyme.com/pages/tech-notes
        netfret = self.readout.get_data(acceptor_channel) - mean_acceptor_acceptor_channel - p*(self.readout.get_data(donor_channel) - mean_buffer_donor_channel)

        # ToDo: Add calculations for other values, as described by Eq. 5 or Eq. 6 in the Technote.

        self.readout.add_data(data={net_fret_key: netfret}, tag=net_fret_key)


    def calculate_net_signal(self):
        LOG.warning("I'm current not implemented.")
        return

    def calculate_data_issue_cell_viability_real_time_glo(self, real_time_glo_measurement, normal_well,
                                                          data_issue_key="realtime-glo", threshold_level=0.05):
        """ Calculate which wells suffer from cell viability issues via RealTime-Glo measurements.

        Calculate which wells suffer from cell viability issues via RealTime-Glo measurements.
        Add the results to self.data_issue.

        Current approach: We assume that the `real_time_glo_measurement` readout values for `normal_well` follow a
        Gaussian distribution. Further, we define that any `real_time_glo_measurement` readout values for other wells
        outside a `threshold_level` (analogous to a significance level; e.g. 5%) from this Gaussian distribution
        has cell viability issues. For increased growth, we mark as "1". For decreased growth, we mark as "-1". For
        normal growth, we mark the well as "0".

        Args:
            real_time_glo_measurement (str):  The key for self.readout.data where the
                                            real_time_glo_measurement ``Readout`` instance is stored.
            normal_well (str):  The name of the wells in self.plate_layout that show standard RealTimeGlo measurements.
                                All other wells will be evaluated in comparison to these wells.
            data_issue_key (str):  The key for self.data_issue.data where the resulting ``DataIssue`` instance will be
                                  stored.
        """

        if hasattr(self, "data_issue") and self.data_issue and data_issue_key in self.data_issue.data:
            raise ValueError("The data_issue_key {} is already in self.data_issue.data.".format(data_issue_key))


        normal_rtglo = self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                       condition=lambda x: x==normal_well,
                                                       value_data_type="readout",
                                                       value_data_tag=real_time_glo_measurement)

        # First, calculate the critical value of the distribution.



        mu_normal = np.mean(normal_rtglo)
        sigma_normal = np.std(normal_rtglo)
        z_score = (self.readout.get_data(real_time_glo_measurement) - mu_normal)/sigma_normal
        # p_value for one-sided test. For two-sided test, multiply by 2:
        p_value = scipy.stats.norm.sf(abs(z_score))

        # Mark wells as True if they persist the Quality Control threshold.
        qc = [[True if datum > threshold_level else False for datum in row] for row in p_value]

        data = data_issue.DataIssue(data={data_issue_key + "_pvalue": p_value,
                                          data_issue_key + "_qc": qc,
                                          data_issue_key + "_zscore": z_score},
                                    name=data_issue_key)

        self.add_data(data_type="data_issue", data=data)
