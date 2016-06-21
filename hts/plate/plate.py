# (C) 2015, 2016 Elke Schaper

"""
    :synopsis: The Plate Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import itertools
import logging
import pickle
import random
import re
import string

import GPy
import numpy as np
import pylab
import scipy.stats

import hts.data_tasks.gaussian_processes
from hts.data_tasks import prediction
from hts.plate_data import plate_data, data_issue, meta_data, plate_layout, readout

KNOWN_DATA_TYPES = ["plate_layout", "readout", "data_issue", "config_data"]
LETTERS = list(string.ascii_uppercase) + ["".join(i) for i in
                                          itertools.product(string.ascii_uppercase, string.ascii_uppercase)]
MAX_WIDTH = 48
MAX_HEIGHT = 32
TRANSLATE_HUMANREADABLE_COORDINATE = {(LETTERS[cc[0]], str(cc[1] + 1)): cc for cc in
                                      itertools.product(range(MAX_HEIGHT), range(MAX_WIDTH))}
TRANSLATE_COORDINATE_HUMANREADABLE = {cc: (LETTERS[cc[0]], str(cc[0] + 1), str(cc[1] + 1)) for cc in
                                      itertools.product(range(MAX_HEIGHT), range(MAX_WIDTH))}
LOG = logging.getLogger(__name__)


## TODO: Instead of creating a matrix for both coordinates, simply create a list each to safe memory.

def translate_coordinate_humanreadable(coordinate, pattern=None):
    coordinate_human = TRANSLATE_COORDINATE_HUMANREADABLE[coordinate]
    if pattern:
        return pattern.format(coordinate_human[0], int(coordinate_human[2]))
    else:
        return coordinate_human


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
                                                                                      str(self.readout.data.keys()),
                                                                                      len(self.readout.data),
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
                    raise Exception(
                        "type of {} data is {}, not plate_data.PlateData.".format(data_type, type(data[data_type])))
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
        """ Add `data` of `data_type` to `self.config_data`

        Add `data` of `data_type` to `self.config_data`
        """

        if data_type == "meta_data" and not isinstance(data, meta_data.MetaData):
            raise Exception('data is not of type config_data.MetaData, but {}'.format(type(data)))
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

    def filter(self, value_data_type, value_data_tag, value_type=None,
               condition_data_type=None, condition_data_tag=None, condition=None,
               return_list=True):
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
            return_list (bool): Returns a flattened list of all values

        Returns:
            (list of x), where x are of type `value_type`, if `value_type` is set.

        ..todo: rename method from filter to get_data
        """

        value_plate_data = getattr(self, value_data_type)

        if condition_data_type:
            condition_plate_data = getattr(self, condition_data_type)
            wells = condition_plate_data.get_wells(data_tag=condition_data_tag, condition=condition)
            if return_list:
                return value_plate_data.get_values(wells=wells, data_tag=value_data_tag, value_type=value_type)
            else:
                data = np.empty([self.height, self.width])
                data[:] = np.NAN
                for well in wells:
                    value = value_plate_data.get_values(wells=[well], data_tag=value_data_tag, value_type=value_type)
                    data[well[0], well[1]] = value[0]
                return data
                # ToDo: Return matrix of values, with None for wells that do not fulfill the condition, and
                # the value otherwise.

        else:
            data = value_plate_data.data[value_data_tag]
            if return_list:
                return [item for sublist in data for item in sublist]
            else:
                return data

        return values

    #### Preprocessing functions

    def preprocess(self, methodname, **kwargs):

        method = getattr(self, methodname)
        method(**kwargs)

    def calculate_linearly_normalized_signal(self, unnormalized_key, normalized_0, normalized_1, normalized_key):
        """ Linearly normalize the data

        .. math::
        normalized__i = \frac{ x_{unnormalized_i} - \hat{x_{low}} } {  \hat{x_{high}} - \hat{x_{low}} }

        normalized_0 are all wells (according to the plate layout) with mean(wells)==0 after normalization.
        normalized_1 are all wells (according to the plate layout) with mean(wells)==1 for normalization.

        Args:
            unnormalized_key (str):  The key for self.readout.data where the unnormalized ``Readout`` instance is stored.
            normalized_key (str):  The key for self.readout.data where the resulting normalized ``Readout`` instance will be stored.
            x_low (list of str):  The list of names of all low fixtures in the plate layout (self.plate_data).
            x_high (list of str): The list of names of the high fixture in the plate layout (self.plate_data).
        """

        if normalized_key in self.readout.data:
            LOG.warning("The normalized_key {} is already in self.readout.data. "
                        "Skipping recalculation".format(normalized_key))
            return

        data_normalized_0 = self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                        condition=lambda x: x in normalized_0,
                                        value_data_type="readout",
                                        value_data_tag=unnormalized_key)

        data_normalized_1 = self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                        condition=lambda x: x in normalized_1,
                                        value_data_type="readout",
                                        value_data_tag=unnormalized_key)

        normalized_data = (self.readout.get_data(unnormalized_key) - np.mean(data_normalized_0)) / (
            np.mean(data_normalized_1) - np.mean(data_normalized_0))

        self.readout.add_data(data={normalized_key: normalized_data}, tag=normalized_key)

    def calculate_normalization_by_division(self, unnormalized_key, normalizer_key, normalized_key):
        """ The normalize data set is equal to a division of all data by the mean of a subset of the data.
        Args:
            unnormalized_key (str):  The key for self.readout.data where the unnormalized ``Readout`` instance is stored.
            normalized_key (str):  The key for self.readout.data where the resulting normalized ``Readout`` instance will be stored.
        """

        if normalized_key in self.readout.data:
            LOG.warning("The normalized_key {} is already in self.readout.data. "
                        "Skipping recalculation".format(normalized_key))
            return

        relative_data = self.readout.get_data(unnormalized_key) / self.readout.get_data(normalizer_key)

        self.readout.add_data(data={normalized_key: relative_data}, tag=normalized_key)


    def subtract_readouts(self, data_tag_readout_minuend, data_tag_readout_subtrahend, data_tag_readout_difference, **kwargs):

        if data_tag_readout_difference in self.readout.data:
            LOG.warning("The data_tag_readout_difference {} is already in self.readout.data. "
                        "Skipping recalculation".format(data_tag_readout_difference))
            return

        difference = self.readout.get_data(data_tag_readout_minuend) - self.readout.get_data(data_tag_readout_subtrahend)

        self.readout.add_data(data={data_tag_readout_difference: difference}, tag=data_tag_readout_difference)


    def calculate_net_fret(self, donor_channel, acceptor_channel,
                           fluorophore_donor="fluorophore_donor",
                           fluorophore_acceptor="fluorophore_acceptor",
                           buffer="buffer", net_fret_key="net_fret"):
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
                                                       condition=lambda x: x == fluorophore_donor,
                                                       value_data_type="readout", value_data_tag=donor_channel))
        mean_acceptor_donor_channel = np.mean(
            self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                        condition=lambda x: x == fluorophore_acceptor,
                        value_data_type="readout", value_data_tag=donor_channel))
        mean_buffer_donor_channel = np.mean(self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                                                        condition=lambda x: x == buffer,
                                                        value_data_type="readout", value_data_tag=donor_channel))
        mean_donor_acceptor_channel = np.mean(
            self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                        condition=lambda x: x == fluorophore_donor,
                        value_data_type="readout", value_data_tag=acceptor_channel))
        mean_acceptor_acceptor_channel = np.mean(
            self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                        condition=lambda x: x == fluorophore_acceptor,
                        value_data_type="readout", value_data_tag=acceptor_channel))
        mean_buffer_acceptor_channel = np.mean(
            self.filter(condition_data_type="plate_layout", condition_data_tag="layout",
                        condition=lambda x: x == buffer,
                        value_data_type="readout", value_data_tag=acceptor_channel))

        for i, value in enumerate([mean_donor_donor_channel, mean_acceptor_donor_channel, mean_buffer_donor_channel,
                                   mean_donor_acceptor_channel, mean_acceptor_acceptor_channel,
                                   mean_buffer_acceptor_channel]):
            if np.isnan(value):
                import pdb;
                pdb.set_trace()
                raise ValueError(
                    "Calculation of variable {} resulted in {}. Check whether the plate layout is correctly assigned.".format(
                        i, value))

        p = (mean_donor_acceptor_channel - mean_buffer_acceptor_channel) / (
            mean_donor_donor_channel - mean_buffer_donor_channel)

        # Calculate the net FRET signal for the entire plate
        # See TechNote #TNPJ100.04 PROzyme
        # http://prozyme.com/pages/tech-notes
        netfret = self.readout.get_data(acceptor_channel) - mean_acceptor_acceptor_channel - p * (
            self.readout.get_data(donor_channel) - mean_buffer_donor_channel)

        # ToDo: Add calculations for other values, as described by Eq. 5 or Eq. 6 in the Technote.

        self.readout.add_data(data={net_fret_key: netfret}, tag=net_fret_key)



    def calculate_control_normalized_signal(self,
                                            data_tag_readout,
                                            negative_control_key,
                                            positive_control_key,
                                            data_tag_normalized_readout=None,
                                            local=True,
                                            **kwargs):
        """ Normalize the signal in `data_tag_readout`, normalized by `negative_control_key` and `positive_control_key`.

        Normalize the signal in `data_tag_readout`, normalized by `negative_control_key` and `positive_control_key`.

        The normalization is calculated as:
        .. math::

        y' = \frac{y - mu_{nc}}{| mu_{nc} - mu_{pc}| }

        For local==True, $mu_{nc}$ and $mu_{pc}$ are predicted locally to the well (using Gaussian processes).
        For local==False, $mu_{nc}$ and $mu_{pc}$ are estimated by the average control values across the plate.

        Args:
            data_tag_readout (str):  The key for self.readout.data where the readouts are stored.
            negative_control_key (str):  The name of the negative control in the plate layout.
            positive_control_key (str):  The name of the positive control in the plate layout.
            data_tag_normalized_readout (str):  The key for self.readout.data where the normalized readouts will be stored.
            local (Bool): If True, use Gaussian processes to locally predict the control distributions. Else, use
                          plate-wise control distributions.
        """

        if data_tag_normalized_readout == None:
            data_tag_normalized_readout = "{}__control_normalized".format(data_tag_readout)

        all_readouts = self.readout.get_data(data_tag_readout)

        if local != True:
            # Normalize by "global" plate averages of negative and positive controls.
            nc_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == negative_control_key)
            nc_values = self.readout.get_values(wells=nc_wells, data_tag=data_tag_readout)
            data_nc_mean = np.mean(nc_values)
            data_nc_std = np.std(nc_values)

            pc_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == positive_control_key)
            pc_values = self.readout.get_values(wells=pc_wells, data_tag=data_tag_readout)
            data_pc_mean = np.mean(pc_values)
            data_pc_std = np.std(pc_values)

            LOG.debug("Normalize globally with mean negative control: {} "
                      "and mean negative control: {}.".format(data_nc_mean, data_pc_mean))
        else:
            # Normalize by "local" predictions of negative and positive control distributions (extracted with Gaussian
            # processes.)

            # Calculate predicted values for mean and std: negative control.
            m, data_nc_mean, data_nc_std = self.apply_gaussian_process(data_tag_readout=data_tag_readout,
                                                                       sample_tag_input=negative_control_key,
                                                                       **kwargs)

            # Calculate predicted values for mean and std: positive control.
            m, data_pc_mean, data_pc_std = self.apply_gaussian_process(data_tag_readout=data_tag_readout,
                                                                       sample_tag_input=positive_control_key,
                                                                       **kwargs)

        # Calculate the normalised data
        normalized_data = (all_readouts - data_nc_mean) / (data_pc_mean - data_nc_mean)

        self.readout.add_data(data={data_tag_normalized_readout: normalized_data,
                                    # These are scalars, not arrays x arrays. Does this data need saving this way?
                                    #                           data_tag_normalized_negative_control: data_nc_mean,
                                    #                           data_tag_normalized_positive_control: data_pc_mean,
                                    },
                              tag=data_tag_normalized_readout)


    def calculate_significance_compared_to_null_distribution(self,
                                                             data_tag_readout,
                                                             sample_tag_null_distribution,
                                                             data_tag_standard_score,
                                                             data_tag_p_value,
                                                             is_higher_value_better,
                                                             **kwargs):

        """
        Calculate the standard score and p-value for all data (in `data_tag_readout`) compared to the null distribution
        defined by all data of `sample_tag_null_distribution` in `data_tag_readout`.
        Save as readouts with tags `data_tag_standard_score` and `data_tag_p_value`.

        Assume that the samples in `sample_tag_null_distribution` follows a Gaussian distribution.

        WARNING! For pvalue calculation, we assume that the control, which has lower mean values, is also supposed to
        show lower mean values. [Otherwise, we would have to introduce a boolean "pos_control_lower_than_neg_control."]


        Args:
            data_tag_readout (str):  The key for self.readout.data where the readouts are stored.
            sample_tag_null_distribution (str): The sample key (defined in plate layout) defining what sample will make up the null distribution that we compare all other samples to.
            data_tag_standard_score (str): The key for self.readout.data where the standard scores will be stored.
            data_tag_p_value (str): The key for self.readout.data where the p-values will be stored.
            **kwargs:

        Returns:

        """

        if data_tag_standard_score == None:
            data_tag_standard_score = "{}__all__vs__{}__standard_score".format(data_tag_readout,
                                                                               sample_tag_null_distribution)

        if data_tag_p_value == None:
            data_tag_p_value = "{}__all__vs__{}__pvalue".format(data_tag_readout, sample_tag_null_distribution)

        all_readouts = self.readout.get_data(data_tag_readout)

        if type(sample_tag_null_distribution) != list:
            sample_tag_null_distribution = [sample_tag_null_distribution]

        # Extract null distribution.
        null_distribution_wells = self.plate_layout.get_wells(data_tag="layout",
                                                              condition=lambda x: x in sample_tag_null_distribution)
        null_distribution_values = self.readout.get_values(wells=null_distribution_wells, data_tag=data_tag_readout)
        null_mean = np.mean(null_distribution_values)
        null_std = np.std(null_distribution_values)

        LOG.debug("Null distribution of sample {} has mean {} and std: {}.".format(sample_tag_null_distribution,
                                                                                   null_mean, null_std))

        # Compute the z-score or standard score
        standard_score = (all_readouts - null_mean) / null_std

        # Calculate the p-Value of all data points compared to the null distribution.
        # Inspired by:
        # http://stackoverflow.com/questions/17559897/python-p-value-from-t-statistic
        p_value = scipy.stats.norm(null_mean, null_std).cdf(all_readouts)

        # Alternative pvalue calculation:
        ## p_value for one-sided test. For two-sided test, multiply by 2:
        # p_value = scipy.stats.norm.sf(abs(standard_score))

        # ToDo: Check and understand
        if is_higher_value_better in [True, "true", "True", "TRUE"]:
            standard_score = - standard_score
            p_value = 1 - p_value

        self.readout.add_data(data={data_tag_standard_score: standard_score,
                                    data_tag_p_value: p_value,
                                    },
                              tag=data_tag_readout)



    def calculate_local_ssmd(self, data_tag_mean_pos, data_tag_mean_neg, data_tag_std_pos, data_tag_std_neg, data_tag_ssmd, **kwargs):
        """
        Calculate local SSMD values.

        Args:
            data_tag_mean_pos:
            data_tag_mean_neg:
            data_tag_std_pos:
            data_tag_std_neg:
            data_tag_ssmd:

        Returns:

        """

        mean_pos = self.readout.get_data(data_tag_mean_pos)
        mean_neg = self.readout.get_data(data_tag_mean_neg)
        std_pos = self.readout.get_data(data_tag_std_pos)
        std_neg = self.readout.get_data(data_tag_std_neg)

        ssmd = np.abs(mean_pos - mean_neg)/np.sqrt(std_pos**2 + std_neg**2)

        self.readout.add_data(data={data_tag_ssmd: ssmd},
                              tag=data_tag_ssmd)


    def classify_by_cutoff(self, data_tag_readout, data_tag_classified_readout, threshold, is_higher_value_better=True, is_twosided=False, **kwargs):
        """
        Map a dataset of float values to either binary (`is_twosided==False`) or [-1,0,1] (`is_twosided==True`), depending
        on whether values fall below `threshold`

        Args:
            data_tag_readout: The key for self.readout.data where the readouts are stored.
            data_tag_classified_readout: The key for self.readout.data where the True/False classification values will be stored.
            threshold:

        Returns:
        """

        all_readouts = self.readout.get_data(data_tag_readout)

        if is_twosided in [True, "true", "True", "TRUE"]:
            is_twosided = True
        if is_higher_value_better in [True, "true", "True", "TRUE"]:
            is_higher_value_better = True

        threshold = float(threshold)

        if is_twosided:
            classified = [[1 if datum > threshold else -1 if abs(datum) > threshold else 0 for datum in row] for row in all_readouts]
        elif is_higher_value_better:
            classified = [[True if datum > threshold else False for datum in row] for row in all_readouts]
        else:
            classified = [[True if datum < threshold else False for datum in row] for row in all_readouts]

        data = data_issue.DataIssue(data={data_tag_classified_readout: classified}, name=data_tag_classified_readout)
        self.add_data(data_type="data_issue", data=data)


    def randomize_values(self,
                         data_tag_readout,
                         data_tag_randomized_readout,
                         randomized_samples="s",
                         **kwargs):

        """
        Randomize the signal in a readout per plate and for a specific sample.
        The result of this method has only visualization purposes.


        Args:
            data_tag_readout (str):  The key for self.readout.data where the readouts are stored.
            data_tag_randomized_readout (str): The key for self.readout.data where the randomized data will be stored.
            **kwargs:

        """
        if data_tag_randomized_readout == None:
            data_tag_randomized_readout = "{}__randomized".format(data_tag_readout)

        all_readouts = self.readout.get_data(data_tag_readout)

        # Extract wells
        randomizable_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == randomized_samples)
        randomizable_values = self.readout.get_values(wells=randomizable_wells, data_tag=data_tag_readout)
        random.shuffle(randomizable_values)

        randomized_readouts = all_readouts.copy()
        for well, value in zip(randomizable_wells, randomizable_values):
            randomized_readouts[well] = value

        self.readout.add_data(data={data_tag_randomized_readout: randomized_readouts,}, tag=data_tag_readout)


    #### Prediction functions


    def cross_validate_predictions(self, data_tag_readout, sample_tag, method_name, **kwargs):
        """ Cross validate sample value predictions for sample type `sample_tag` and readout `data_tag_readout`,
        using prediction method `method_name`.

        Args:
            data_tag_readout (str):  The key for self.readout.data where the ``Readout`` instance is stored.
            sample_tag (str):  The sample for which the gaussian process will be modeled according to the
                                position in self.plate_layout.data. E.g. for positive controls "pos"
            method_name (str): The prediction method. E.g. gp for Gaussian processes.
        """
        sampled_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == sample_tag)
        values = self.readout.get_values(wells=sampled_wells, data_tag=data_tag_readout)  # value_type=float

        if method_name == "gp":
            prediction_method = prediction.predict_with_gaussian_process

        x, y, y_mean, y_std = self.flatten_data(wells=sampled_wells, values=values, normalize=False)

        return prediction.cross_validate_predictions(x, y, prediction_method, **kwargs)



    def evaluate_well_value_prediction(self, data_predictions, data_tag_readout, sample_key=None):
        """
        Calculate mean squared prediction error.

       ToDo: Debug. Better: REWRITE!
        """

        # y_predicted_mean, y_predicted_var = m.predict(X)
        # f_mean, f_var = m._raw_predict(X) # Difference to m.predict(X)
        # y_predicted_abs = y_predicted_mean * y_std + y_mean
        # y_error = y_norm - y_predicted_mean
        # y_error_abs = y - y_predicted_abs


        wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: True)
        values = self.readout.get_values(wells=wells, data_tag=data_tag_readout)  # value_type=float

        #### This needs to be debugged, as data_predictions now come in a different format.
        raise Exception("Needs debugging.")
        values = np.array(values).reshape((len(values), 1))
        diff = data_predictions - values

        if sample_key:
            specific_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == sample_key)
            if len(specific_wells) == 0:
                raise Exception("sample_key: {} does not define any wells.".format(sample_key))
            diff = np.array([diff[wells.index(well)] for well in specific_wells])

        return np.linalg.norm(diff)


    #### Prediction functions - Gaussian processes

    def map_coordinates(self, coordinates_list):
        # map plate coordinates to "standard" coordinates. E.g. switch axes, turn x-Axis.
        return [(i[1], self.height - i[0] + 1) for i in coordinates_list]

    def flatten_data(self, wells, values):
        return self.flatten_wells(wells), self.flatten_values(values)

    def flatten_wells(self, wells):
        # Structure of X: Similar to http://gpy.readthedocs.org/en/master/tuto_GP_regression.html
        # map plate coordinates to "standard" coordinates. E.g. switch axes, turn x-Axis.
        sampled_wells = self.map_coordinates(wells)
        x = np.array(sampled_wells)
        return x

    def flatten_values(self, values):
        y = np.array(values)
        y = y.reshape((len(values), 1))
        return y

    def un_flatten_data(self, y):
        y = [i for j in y for i in j]
        y = np.array([y[row * self.width:(row + 1) * self.width] for row in range(self.height)])
        return y

    def get_data_for_gaussian_process(self, data_tag_readout, sample_tags):

        if type(sample_tags) != list:
            sample_tags = [sample_tags]

        sampled_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x in sample_tags)
        values = self.readout.get_values(wells=sampled_wells, data_tag=data_tag_readout)  # value_type=float

        x, y = self.flatten_data(wells=sampled_wells, values=values)
        return x, y





