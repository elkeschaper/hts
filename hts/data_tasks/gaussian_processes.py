import logging
from distutils.util import strtobool

import GPy
import configobj
import numpy as np

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


class GaussianProcess(object):
    def __str__(self, template="{data_tag}__{sample_tags}__{kernel_tag}"):
        tags_str = {i: str(j) if i != 'sample_tags' else "_".join(j) for i, j in self.tags.items()}
        return template.format(**tags_str)

    def __init__(self, tags, x, y, kernel, optimization_method='bfgs', n_max_iterations=100, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.tags = tags
        self.x = x
        self.y = y
        self.kernel = kernel

        self.optimization_method = optimization_method
        self.n_max_iterations = n_max_iterations

        self.m = GPy.models.GPRegression(x, y, kernel)
        # len_prior = GPy.priors.inverse_gamma(1,18) # 1, 25
        # m.set_prior('.*lengthscale',len_prior)

        LOG.info(self.m)
        ## It is not clear whether you should really perform this optimisation - perhaps you know the best length scale ?
        self.m.optimize(optimization_method, max_f_eval=n_max_iterations)

    @classmethod
    def create(cls, x, y, **kwargs):

        # Normalize y data
        y_mean = y.mean()
        y_std = y.std()
        y_norm = (y - y_mean) / y_std

        # Normalize x data
        x_mean = x.mean()
        x_std = x.std()
        x_norm = x  # (x - x_mean) / x_std

        return cls(x_raw=x, x=x_norm, x_mean=x_mean, x_std=x_std, y_raw=y, y_mean=y_mean, y_std=y_std, y=y_norm,
                   **kwargs)

    @property
    def bic(self):
        """
        Calculate the Bayesian Information Criterion (BIC) for a (trained) GPy `model`.
        https://en.wikipedia.org/wiki/Bayesian_information_criterion


        ToDo: Check that model.log_likelihood() and model._size_transformed() are the correct inputs.
        ToDo: Check that len(model.X) is always the sample size.
        """

        # model._size_transformed() is the number of optimisation parameters, model.size the total number of parameters.
        # model.log_likelihood() is the natural logarithm of the marginal likelihood of the Gaussian process.
        if not hasattr(self, "_bic"):
            self._bic = - 2 * self.m.log_likelihood() + len(self.m.X) * np.log(self.m._size_transformed())
        return self._bic

    def predict(self, x):
        """
        Predict for x value with model.

        Args:
            x: Not normalized input coordinates. ToDo: Normalize

        Returns:

        """

        y_predicted_mean_normalized, y_predicted_var_normalized = self.m.predict(x)
        y_predicted_mean = y_predicted_mean_normalized * self.y_std + self.y_mean
        y_predicted_sd = np.sqrt(y_predicted_var_normalized) * self.y_std

        return y_predicted_mean_normalized, y_predicted_var_normalized, y_predicted_mean, y_predicted_sd


class GaussianProcesses(object):
    def __init__(self, models, run):
        self.models = models
        self.run = run

    def add(self, **kwargs):
        gp = GaussianProcess.create(**kwargs)
        self.models.append(gp)
        return gp

    def filter(self, **filter_kwargs):

        for model in self.models:
            for filter_key, filter_value in filter_kwargs.items():
                if filter_key not in model.tags or model.tags[filter_key] != filter_value:
                    break
            else:
                yield model


def add_gaussian_processes(run,
                           data_tag_readout,
                           methods,
                           sample_tags="s",
                           **kwargs):
    """ Add Gaussian process models to run.

    Add Gaussian process models to run.
    """

    if type(sample_tags) != list:
        sample_tags = [sample_tags]

    for kernel_tag, kernel_config in methods.items():
        # if kernel_tag in KERNEL_CHOICE and len(kernel_config) == 0:
        #     logging.info("Using default Kernel config for {}".format(kernel_tag))
        #     kernel_config = KERNEL_CHOICE[kernel_tag]

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

        logging.info("Created kernel {}.".format(kernel_tag))
        if is_per_plate:

            for plate_tag, plate in run.plates.items():
                LOG.info("Applying Gaussian process on plate {}.".format(plate_tag))

                x, y = plate.get_data_for_gaussian_process(data_tag_readout=data_tag_readout, sample_tags=sample_tags)

                kernel = create_gaussian_process_composite_kernel(input_dim=x.shape[1], kernels=kernel_config.values())

                run.gp_models.add(
                    tags={"plate_tag": plate_tag, "data_tag": data_tag_readout, "sample_tags": sample_tags,
                          "kernel_tag": kernel_tag},
                    x=x, y=y, kernel=kernel)

        else:
            raise Exception("runwise gaussian process normalization is not yet implemented.")


def do_gaussian_process_prediction(run,
                                   data_tag_readout,
                                   result_tag_predicted_mean="{gp_model_str}__predicted_mean",
                                   result_tag_predicted_sd="{gp_model_str}__predicted_sd",
                                   best_mean_tag="best__predicted_mean",
                                   best_sd_tag="best__predicted_sd",
                                   **kwargs):
    """ Perform Gaussian process prediction.

    Perform Gaussian process prediction.
    """

    # ToDo: Allow non-platewise predictions (e.g. runwise, zigzag)

    for plate_tag, plate in run.plates.items():

        y = plate.flatten_wells(wells=plate.plate_layout.get_wells(data_tag="layout", condition=lambda x: True))

        gp_models = list(run.gp_models.filter(plate_tag=plate_tag, data_tag=data_tag_readout))

        # Select the model with the lowest bic
        best_model = min(gp_models, key=lambda x: x.bic)

        for gp_model in gp_models:
            y_pred_mean_normalized, y_pred_var_normalized, y_pred_mean, y_pred_sd = gp_model.predict(y)

            # Map the data from lists back to plate matrices
            y_pred_mean = plate.un_flatten_data(y_pred_mean)
            y_pred_sd = plate.un_flatten_data(y_pred_sd)

            # Save the predicted mean data
            result_tag_mean = result_tag_predicted_mean.format(gp_model_str=str(gp_model))
            plate.readout.add_data(data={result_tag_mean: y_pred_mean}, tag=result_tag_mean)

            # Save the predicted sd data
            result_tag_sd = result_tag_predicted_sd.format(gp_model_str=str(gp_model))
            plate.readout.add_data(data={result_tag_sd: y_pred_sd}, tag=result_tag_sd)

            if gp_model == best_model:
                gp_model.best = True
                plate.readout.add_data(data={best_mean_tag: y_pred_mean}, tag=best_mean_tag)
                plate.readout.add_data(data={best_sd_tag: y_pred_sd}, tag=best_sd_tag)
            else:
                gp_model.best = False


def create_gaussian_process_kernel(kernel_type, input_dim, info=None, constraints=None):
    '''
    `kernel_type` is the name of the kernel. Currently available kernels:
    ['Add', 'BasisFuncKernel', 'Bias', 'Brownian', 'ChangePointBasisFuncKernel', 'Coregionalize', 'Cosine', 'DEtime', 'DiffGenomeKern', 'DomainKernel', 'EQ_ODE2', 'ExpQuad', 'Exponential', 'Fixed', 'Hierarchical', 'IndependentOutputs', 'Kern', 'Linear', 'LinearFull', 'LinearSlopeBasisFuncKernel', 'LogisticBasisFuncKernel', 'MLP', 'Matern32', 'Matern52', 'ODE_UY', 'ODE_UYC', 'ODE_st', 'ODE_t', 'OU', 'PeriodicExponential', 'PeriodicMatern32', 'PeriodicMatern52', 'Poly', 'Prod', 'RBF', 'RatQuad', 'Spline', 'SplitKern', 'StdPeriodic', 'TruncLinear', 'TruncLinear_inf', 'White'
    '''
    try:
        kernel = getattr(GPy.kern, kernel_type)
    except:
        raise ValueError(
            "Error: Kernel {} is currently not implemented in GPy.kern:\n{}".format(kernel_type, str(dir(GPy.kern))))

    if info == None:
        info = {}
    if constraints == None:
        constraints = {}

    try:
        kernel = kernel(input_dim=input_dim, **info)
        for parameter, property in constraints.items():
            # e.g. kernel_tmp.variance.constrain_positive(4) would require kernel_kwargs = {"variance": ("constrain_positive", "4")}
            # Todo: Clean up tuples vs dicts & 1 vs many constraints.
            if type(property) in [list, tuple]:
                method, constraint = property
                getattr(getattr(kernel, parameter), method)(constraint)
            elif type(property) in [dict, configobj.Section]:
                for method, constraint in property.items():
                    getattr(getattr(kernel, parameter), method)(*constraint)
    except:
        import pdb;
        pdb.set_trace()
        raise ValueError(
            "Please check you kernel kwargs for kernel kernel_type: {} with input_dim: {}".format(kernel_type,
                                                                                                  input_dim))

    return kernel


def create_gaussian_process_composite_kernel(input_dim, kernel=None, kernels=None):
    """ Create a gaussian process kernel from kernel string names.

    Kernel descriptions: https://gpy.readthedocs.org/en/latest/GPy.kern.src.html

    Args:
        input_dim (int):  The expected Kernel dimension
        kernel (str):  A previous kernel. More kernel features are added to this previous kernel.
        kernels (dict): Dict of kernel_names: kernel_kwargs. E.g., kernels: {"rbf": None, "white_noise": None}

        # ToDo: Add ARD to the kernel parameters, such that e.g. lengthscales can differ across the plates.
    """
    if not kernels:
        kernels = [("RBF", {}, {}, None), ("White", {}, {}, "+")]

    for kernel_kwargs in kernels:

        # Allow kernel definition either as list of tuples, or as list of dicts.
        if type(kernel_kwargs) == tuple:
            kernel_type, kernel_info, kernel_constraints, kernel_arithmetic = kernel_kwargs
            kernel_tmp = create_gaussian_process_kernel(input_dim=input_dim, kernel_type=kernel_type, info=kernel_info,
                                                        constraints=kernel_constraints)
        elif type(kernel_kwargs) in [dict, configobj.Section]:
            try:
                kernel_arithmetic = kernel_kwargs.pop("kernel_arithmetic")
            except:
                kernel_arithmetic = "+"
            kernel_tmp = create_gaussian_process_kernel(input_dim=input_dim, **kernel_kwargs)
        else:
            raise Exception("Cannot handle kernel_kwargs of type {}.".format(type(kernel_kwargs)))

        if kernel:
            if kernel_arithmetic == "+":
                kernel += kernel_tmp
            elif kernel_arithmetic == "*":
                kernel *= kernel_tmp
            else:
                logging.error('kernel_arithmetic: {} is not implemented.'.format(kernel_arithmetic))
        else:
            kernel = kernel_tmp

    return kernel


#### TMP
def set_best_gaussian_process_normalization(run, data_tag_readout, data_tag_best_model, **kwargs):
    for plate_tag, plate in run.plates.items():
        # pdb.set_trace()
        best_model = plate.readout.best_gp_model(data_tag_readout)

        best_data = None
        plate.readout.add_data(data={data_tag_best_model: best_data}, tag=data_tag_best_model)


def best_gaussian_process_normalization(models, **kwargs):
    import pdb;
    pdb.set_trace()
    for model in models:
        model
