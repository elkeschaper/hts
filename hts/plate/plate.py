# (C) 2015, 2016 Elke Schaper

"""
    :synopsis: The Plate Class.

    .. moduleauthor:: Elke Schaper <elke.schaper@isb-sib.ch>
"""

import ast
import GPy
import itertools
import logging
import numpy as np
import os
import pickle
import pylab
import re
import scipy.stats
import string

from hts.plate import prediction
from hts.plate_data import plate_data, data_issue, plate_layout, readout

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

        if data_type == "config_data" and not isinstance(data, meta_data.MetaData):
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
        """ Normalize the data by rtglo as a proxy for the relative cell number.

        .. math::
        rtglo_normalized_i = \frac{ x_{unnormalized_i} - \hat{x_{low}} } {  \hat{x_{high}} - \hat{x_{low}} }

        x_low could for example be cell-less wells ("blank" or "buffer). Here, the RTGlo signal should be minimal.
        x_high could be the wells were cells are expected to grow best, and grow homogenously across plates.

        Args:
            rtglo_key (str):  The key for self.readout.data where the rtglo ``Readout`` instance is stored.
            unnormalized_key (str):  The key for self.readout.data where the unnormalized ``Readout`` instance is stored.
            normalized_key (str):  The key for self.readout.data where the resulting normalized ``Readout`` instance will be stored.
            x_low (list of str):  The list of names of all low fixtures in the plate layout (self.plate_data).
            x_high (str): The name of the high fixture in the plate layout (self.plate_data).
        """

        if normalized_key in self.readout.data:
            LOG.warning("The normalized_key {} is already in self.readout.data. "
                        "Skipping recalculation".format(normalized_key))
            return

        relative_data = self.readout.get_data(unnormalized_key) / self.readout.get_data(normalizer_key)

        self.readout.add_data(data={normalized_key: relative_data}, tag=normalized_key)


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
                                   condition=lambda x: x == normal_well,
                                   value_data_type="readout",
                                   value_data_tag=real_time_glo_measurement)

        # First, calculate the critical value of the distribution.

        mu_normal = np.mean(normal_rtglo)
        sigma_normal = np.std(normal_rtglo)
        z_score = (self.readout.get_data(real_time_glo_measurement) - mu_normal) / sigma_normal
        # p_value for one-sided test. For two-sided test, multiply by 2:
        p_value = scipy.stats.norm.sf(abs(z_score))

        # Mark wells as True if they persist the Quality Control threshold.
        qc = [[True if datum > threshold_level else False for datum in row] for row in p_value]

        data = data_issue.DataIssue(data={data_issue_key + "_pvalue": p_value,
                                          data_issue_key + "_qc": qc,
                                          data_issue_key + "_zscore": z_score},
                                    name=data_issue_key)

        self.add_data(data_type="data_issue", data=data)

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

        x, y, y_mean, y_std = self.convert_values(wells=sampled_wells, values=values, normalize=False)

        return prediction.cross_validate_predictions(x, y, prediction_method, **kwargs)

    def map_coordinates(self, coordinates_list):
        # map plate coordinates to "standard" coordinates. E.g. switch axes, turn x-Axis.
        return [(i[1], self.height - i[0] + 1) for i in coordinates_list]

    def convert_values(self, wells, values, normalize=False):

        n_samples = len(wells)

        # map plate coordinates to "standard" coordinates. E.g. switch axes, turn x-Axis.
        sampled_wells = self.map_coordinates(wells)

        # Structure of X: Similar to http://gpy.readthedocs.org/en/master/tuto_GP_regression.html
        x = np.array(sampled_wells)
        y = np.array(values)

        y_mean = y.mean()
        y_std = y.std()

        y = y.reshape((n_samples, 1))

        if normalize:
            y_norm = y - y_mean
            y_norm /= y_std
            y = y_norm

        return x, y, y_mean, y_std

    #### Prediction functions - Gaussian processes


    def model_as_gaussian_process(self, data_tag_readout, sample_tag,
                                  n_max_iterations=10000,
                                  plot_kwargs=False,
                                  kernel=None,
                                  kernels=None,
                                  optimization_method='bfgs'):
        """ Model data as a gaussian process. Return the Gaussian process model, and mean and std of the input data for
        renormalization.

        Args:
            data_tag_readout (str):  The key for self.readout.data where the ``Readout`` instance is stored.
            sample_tag (str):  The sample for which the gaussian process will be modeled according to the
                                position in self.plate_layout.data. E.g. for positive controls "pos"
            optimization_method (str): The GPy optimization method. E.g. bfgs, scg, tnc
        """

        sampled_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == sample_tag)
        values = self.readout.get_values(wells=sampled_wells, data_tag=data_tag_readout)  # value_type=float

        x, y_norm, y_mean, y_std = self.convert_values(wells=sampled_wells, values=values, normalize=True)

        if not kernel and kernels:
            kernel = prediction.create_gaussian_process_kernel(dimension=x.shape[1], kernel=None, kernels=kernels)

        m = GPy.models.GPRegression(x, y_norm, kernel)
        # len_prior = GPy.priors.inverse_gamma(1,18) # 1, 25
        # m.set_prior('.*lengthscale',len_prior)

        LOG.info(m)

        ## It is not clear whether you should really perform this optimisation - perhaps you know the best length scale ?
        m.optimize(optimization_method, max_f_eval=n_max_iterations)

        LOG.info(m)

        if plot_kwargs:
            # m.kern.plot_ARD()
            # Plot the posterior of the GP
            m.plot_data()
            m.plot_f()
            m.plot(**plot_kwargs)
            pylab.show()

        return m, y_mean, y_std

    def predict_from_gaussian_process(self, model, y_mean=0, y_std=1, sample_key=None, data_tag_prediction=None):
        """ Predict data for Gaussian process model `model`

        Args:
            sample_key (str):  The sample for which the gaussian process will be predicted according to the
                                position in self.plate_layout.data. E.g. for positive controls "pos". If not assigned,
                                predictions for whole plate will be returned.
            data_tag_prediction (str): If data_tag_prediction is set to a string, the data will be saved as a readout
                                with tag *data_tag_prediction*.
        """
        if sample_key:
            raise Exception("Not yet implemented")
        else:
            all_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: True)
            all_wells = self.map_coordinates(all_wells)
            x_all = np.array(all_wells)

        y_predicted_mean, y_predicted_var = model.predict(x_all)
        y_predicted_mean_abs = y_predicted_mean * y_std + y_mean
        y_predicted_sd_abs = np.sqrt(y_predicted_var) * y_std

        # Are you absolutely sure you got the mapping back to list of lists right?
        y_predicted_mean_abs = [i for j in y_predicted_mean_abs for i in j]
        y_predicted_mean_abs = np.array(
            [y_predicted_mean_abs[row * self.width:(row + 1) * self.width] for row in range(self.height)])
        y_predicted_sd_abs = [i for j in y_predicted_sd_abs for i in j]
        y_predicted_sd_abs = np.array(
            [y_predicted_sd_abs[row * self.width:(row + 1) * self.width] for row in range(self.height)])

        if data_tag_prediction:
            self.readout.add_data(data={data_tag_prediction: y_predicted_mean_abs}, tag=data_tag_prediction)

        return y_predicted_mean_abs, y_predicted_sd_abs

    def apply_gaussian_process(self, data_tag_readout, sample_tag_input, data_tag_prediction=None, **kwargs):

        """ Model data as a gaussian process. Predict data for the entire plate. [Compare predictions and real values.]

        Args:
            data_tag_readout (str): The key for self.readout.data where the ``Readout`` instance is stored.
            sample_tag_input (str): The sample for which the gaussian process will be predicted according to the
                                    position in self.plate_layout.data. E.g. for positive controls "pos".
                                    If not assigned, predictions for whole plate will be returned.
        """

        m, y_mean, y_std = self.model_as_gaussian_process(data_tag_readout, sample_tag_input, **kwargs)
        y_predicted_mean_abs, y_predicted_sd_abs = self.predict_from_gaussian_process(model=m,
                                                                                      y_mean=y_mean,
                                                                                      y_std=y_std,
                                                                                      data_tag_prediction=data_tag_prediction)

        return m, y_predicted_mean_abs, y_predicted_sd_abs

    def evaluate_well_value_prediction(self, data_predictions, data_tag_readout, sample_key=None):
        """
        Calculate mean squared prediction error.

       ToDo: Debug
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

    def calculate_control_normalized_signal(self,
                                            data_tag_readout,
                                            negative_control_key,
                                            positive_control_key,
                                            data_tag_normalized_readout=None,
                                            data_tag_pvalue_vs_neg_control=None,
                                            data_tag_normalized_negative_control=None,
                                            data_tag_normalized_positive_control=None,
                                            local=True,
                                            **kwargs):
        """ Normalize the signal in `data_tag_readout`, normalized by `negative_control_key` and `positive_control_key`.

        Normalize the signal in `data_tag_readout`, normalized by `negative_control_key` and `positive_control_key`.

        The normalization is calculated as:
        .. math::

        y' = \frac{y - mu_{nc}}{| mu_{nc} - mu_{pc}| }

        For local==True, $mu_{nc}$ and $mu_{pc}$ are predicted locally to the well (using Gaussian processes).
        For local==False, $mu_{nc}$ and $mu_{pc}$ are estimated by the average control values across the plate.

        WARNING! For pvalue calculation, we assume that the control, which has lower mean values, is also supposed to
        show lower mean values. [Otherwise, we would have to introduce a boolean "pos_control_lower_than_neg_control."]

        Args:
            data_tag_readout (str):  The key for self.readout.data where the readouts are stored.
            negative_control_key (str):  The name of the negative control in the plate layout.
            positive_control_key (str):  The name of the positive control in the plate layout.
            data_tag_readout (str):  The key for self.readout.data where the normalized readouts will be stored.
            local (Bool): If True, use Gaussian processes to locally predict the control distributions. Else, use
                          plate-wise control distributions.

        """

        if data_tag_normalized_readout == None:
            data_tag_normalized_readout = "{}_GP_normalized_by_controls".format(data_tag_readout)

        if data_tag_pvalue_vs_neg_control == None:
            data_tag_pvalue_vs_neg_control = "{}_GP_pvalue_vs_neg_control".format(data_tag_readout)

        if data_tag_normalized_negative_control == None:
            data_tag_normalized_negative_control = "{}_GP_normalized_neg".format(data_tag_readout)

        if data_tag_normalized_positive_control == None:
            data_tag_normalized_positive_control = "{}_GP_normalized_pos".format(data_tag_readout)

        all_readouts = self.readout.get_data(data_tag_readout)

        if not local:
            # Normalize by "global" plate averages of negative and positive controls.
            nc_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == negative_control_key)
            nc_values = self.readout.get_values(wells=nc_wells, data_tag=data_tag_readout)
            data_nc_mean = np.mean(nc_values)
            data_nc_std = np.std(nc_values)

            pc_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x == positive_control_key)
            pc_values = self.readout.get_values(wells=pc_wells, data_tag=data_tag_readout)
            data_pc_mean = np.mean(pc_values)

            LOG.debug("Normalize globally with mean negative control: {} "
                      "and mean negative control: {}.".format(data_nc_mean, data_pc_mean))
        else:
            # Normalize by "local" predictions of negative and positive control distributions (extracted with Gaussian
            # processes.)

            # Calculate predicted values for mean and std: negative control.
            m, data_nc_mean, data_nc_std = \
                self.apply_gaussian_process(data_tag_readout=data_tag_readout, sample_tag_input=negative_control_key,
                                            **kwargs)

            # Calculate predicted values for mean and std: positive control.
            m, data_pc_mean, data_pc_std = \
                self.apply_gaussian_process(data_tag_readout=data_tag_readout, sample_tag_input=positive_control_key,
                                            **kwargs)

        # Calculate the normalised data
        normalized_data = (all_readouts - data_nc_mean) / (data_pc_mean - data_nc_mean)

        if self.name == "I4":
            pass
            # import pdb; pdb.set_trace()

        # Calculate the p-Value of all data points compared to the negative control.
        # Inspired by:
        # http://stackoverflow.com/questions/17559897/python-p-value-from-t-statistic

        LOG.warning("Make sure that the local data_nc_std has the same interpretation as the global data_nc_std.")
        p_value_neg = scipy.stats.norm(data_nc_mean, data_nc_std).cdf(all_readouts)

        self.readout.add_data(data={data_tag_normalized_readout: normalized_data,
                                    data_tag_pvalue_vs_neg_control: p_value_neg,
                                    data_tag_normalized_negative_control: data_nc_mean,
                                    data_tag_normalized_positive_control: data_pc_mean,
                                    },
                              tag=data_tag_normalized_readout)
