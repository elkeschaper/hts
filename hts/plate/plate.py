# (C) 2015 Elke Schaper

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
                raise Exception("Not implemented.")
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



    def map_coordinates(self, coordinates_list):
        # map plate coordinates to "standard" coordinates. E.g. switch axes, turn x-Axis.
        return [(i[1], self.height-i[0]+1) for i in coordinates_list]

    def model_as_gaussian_process(self, data_tag_readout, sample_key,
                                  kernel_type='m32',
                                  n_max_iterations=1000,
                                  plot_kwargs=False,
                                  **kwargs):
        """ Model data as a gaussian process. Predict data for the entire plate. Compare predictions and real values.


        Args:
            data_tag_readout (str):  The key for self.readout.data where the ``Readout`` instance is stored.
            sample_key (str):  The sample for which the gaussian process will be modeled according to the
                                position in self.plate_layout.data. E.g. for positive controls "pos"

        """


        sampled_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x==sample_key)
        values = self.readout.get_values(wells=sampled_wells, data_tag=data_tag_readout) # value_type=float

        n_samples = len(sampled_wells)

        # map plate coordinates to "standard" coordinates. E.g. switch axes, turn x-Axis.
        sampled_wells = self.map_coordinates(sampled_wells)

        # Structure of X: Similar to http://gpy.readthedocs.org/en/master/tuto_GP_regression.html
        X = np.array(sampled_wells)
        #X1 = np.array([i[0] for i in sampled_wells])
        #X2 = np.array([i[1] for i in sampled_wells])
        #X = np.vstack((X1, X2))

        Y = np.array(values)
        Y_mean = Y.mean()
        Y_std = Y.std()

        Y = Y.reshape((n_samples,1))
        Y_norm = Y - Y_mean
        Y_norm /= Y_std

        if kernel_type == 'linear':
            kernel = GPy.kern.Linear(input_dim=X.shape[1], ARD=2)
        elif kernel_type == 'rbf_inv':
            kernel = GPy.kern.RBF_inv(input_dim=X.shape[1], ARD=2)
        elif kernel_type == 'rbf':
            kernel = GPy.kern.RBF(input_dim=X.shape[1])
        elif kernel_type == 'm32':
            kernel = GPy.kern.Matern32(input_dim=X.shape[1])
        else:
            raise ValueError("Kernel {} is currently not implemented".format(kernel_type))

        kernel += GPy.kern.White(input_dim=X.shape[1]) # + GPy.kern.Bias(input_dim=X.shape[0])

        m = GPy.models.GPRegression(X, Y_norm, kernel)
        # len_prior = GPy.priors.inverse_gamma(1,18) # 1, 25
        # m.set_prior('.*lengthscale',len_prior)

        #m.optimize(optimizer='scg', max_iters=n_max_iterations)

        LOG.info(m)

        #   GP_regression.           |  value  |  constraints  |  priors
        # sum.rbf.variance         |    1.0  |      +ve      |
        # sum.rbf.lengthscale      |    1.0  |      +ve      |
        # sum.white.variance       |    1.0  |      +ve      |
        # Gaussian_noise.variance  |    1.0  |      +ve      |

        ## It is not clear whether you should really perform this optimisation - perhaps you know the best length scale ?
        m.optimize(max_f_eval = n_max_iterations)

        LOG.info(m)

        if plot_kwargs:
            #m.kern.plot_ARD()
            # Plot the posterior of the GP
            m.plot_data()
            m.plot_f()
            m.plot(**plot_kwargs)
            pylab.show()

        #Y_predicted_mean, Y_predicted_var = m.predict(X)
        #f_mean, f_var = m._raw_predict(X) # Difference to m.predict(X)
        #Y_predicted_abs = Y_predicted_mean * Y_std + Y_mean
        #Y_error = Y_norm - Y_predicted_mean
        #Y_error_abs = Y - Y_predicted_abs

        all_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: True)
        all_wells = self.map_coordinates(all_wells)
        X_all = np.array(all_wells)

        Y_all_predicted_mean, Y_all_predicted_var  = m.predict(X_all)
        Y_all_predicted_mean_abs = Y_all_predicted_mean * Y_std + Y_mean
        Y_all_predicted_sd_abs = np.sqrt(Y_all_predicted_var) * Y_std

        # Are you absolutely sure you got the mapping back to list of lists right?
        Y_all_predicted_mean_abs = [i for j in Y_all_predicted_mean_abs for i in j]
        Y_all_predicted_mean_abs = np.array([Y_all_predicted_mean_abs[row*24:(row+1)*24] for row in range(self.height)])
        Y_all_predicted_sd_abs = [i for j in Y_all_predicted_sd_abs for i in j]
        Y_all_predicted_sd_abs = np.array([Y_all_predicted_sd_abs[row*24:(row+1)*24] for row in range(self.height)])

        return Y_all_predicted_mean_abs, Y_all_predicted_sd_abs


    def evaluate_well_value_prediction(self, data_predictions, data_tag_readout, sample_key=None):

        wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: True)
        values = self.readout.get_values(wells=wells, data_tag=data_tag_readout) # value_type=float

        #### This needs to be debugged, as data_predictions now come in a different format.
        raise Exception("Needs debugging.")
        values = np.array(values).reshape((len(values),1))
        diff = data_predictions - values

        if sample_key:
            specific_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x==sample_key)
            if len(specific_wells) == 0:
                raise Exception("sample_key: {} does not define any wells.".format(sample_key))
            diff = np.array([diff[wells.index(well)] for well in specific_wells])

        return np.linalg.norm(diff)


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
        For local==False, $mu_{nc}$ and $mu_{pc}$ are estimated by the averge control values across the plate.

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

        if not data_tag_normalized_readout:
            data_tag_normalized_readout = "{}_normalized_by_controls".format(data_tag_readout)


        all_readouts = self.readout.get_data(data_tag_readout)

        if not local:
            # Normalize by "global" plate averages of negative and positive controls.
            nc_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x==negative_control_key)
            nc_values = self.readout.get_values(wells=nc_wells, data_tag=data_tag_readout)
            data_nc_mean = np.mean(nc_values)
            data_nc_std = np.std(nc_values)

            pc_wells = self.plate_layout.get_wells(data_tag="layout", condition=lambda x: x==positive_control_key)
            pc_values = self.readout.get_values(wells=pc_wells, data_tag=data_tag_readout)
            data_pc_mean = np.mean(pc_values)

            LOG.debug("Normalize globally with mean negative control: {} "
                      "and mean negative control: {}.".format(data_nc_mean, data_pc_mean))
        else:
            # Normalize by "local" predictions of negative and positive control distributions (extracted with Gaussian
            # processes.)

            # Calculate predicted values for mean and std: negative control.
            data_nc_mean, data_nc_std = \
                self.model_as_gaussian_process(data_tag_readout=data_tag_readout, sample_key=negative_control_key, **kwargs)

            # Calculate predicted values for mean and std: positive control.
            data_pc_mean, data_pc_std = \
                self.model_as_gaussian_process(data_tag_readout=data_tag_readout, sample_key=positive_control_key, **kwargs)


        # Calculate the normalised data
        normalized_data = (all_readouts - data_nc_mean)/abs(data_nc_mean - data_pc_mean)

        # Calculate the p-Value of all data points compared to the negative control.
        # Inspired by:
        # http://stackoverflow.com/questions/17559897/python-p-value-from-t-statistic

        LOG.warning("Make sure that the local data_nc_std has the same interpretation as the global data_nc_std.")
        p_value_neg = scipy.stats.norm(data_nc_mean, data_nc_std).cdf(all_readouts)

        self.readout.add_data(data={data_tag_normalized_readout: normalized_data,
                                    "{}_pvalue_vs_neg_control".format(data_tag_readout): p_value_neg},
                              tag=data_tag_normalized_readout)