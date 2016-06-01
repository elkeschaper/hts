import GPy
import logging

import configobj
import numpy as np

LOG = logging.getLogger(__name__)


def cross_validate_predictions(x, y, prediction_method, p=1, **kwargs):
    """ Calculate the prediction error of `prediction_method` on a dataset with input x and output y
    with cross validation.

    Args:
        x (np.array): The input.
        y (np.array): The output/signal.
        prediction_method (method): The prediction method.
        p (int): The cross-validation chunk size. E.g., p=1 is leave-one-out cross-validation.
    """

    assert len(x) == len(y)

    if p != 1:
        raise Exception("p != 1 is not implemented; only leave-one-out cross-validation is possible.")

    error = []
    for i in range(len(x)):
        y_predict = prediction_method(x=np.delete(x,i,axis=0), y=np.delete(y,i,axis=0), x_predict=x[i:i+1], **kwargs)
        error.append((y[i:i+1]-y_predict).sum())

    return error


def predict_with_gaussian_process(x, y, x_predict, kernel_kwargs=None, optimize_kwargs=None, **kwargs):
    """ Train a Gaussian process model with training data `x`, `y`. Predict values for `x_predict`.

    Args:
        x (np.array):  The input data for training.
        y (np.array):  The output data for training.
        x_predict (np.array): The input data for prediction.
        kernel_kwargs (dict): E.g. {"StdPeriodic": {"wavelengths": ("fix", 12)}}
        optimize_kwargs (dict): E.g. {"optimizer": "bfgs", "max_f_eval": 1000}
    """
    if kernel_kwargs == None:
        kernel_kwargs = {}
    if optimize_kwargs == None:
        optimize_kwargs = {}

    assert len(x) == len(y)
    kernel = create_gaussian_process_composite_kernel(input_dim=x.shape[1], kernel=None, kernels=kernel_kwargs)
    m = GPy.models.GPRegression(x, y, kernel)
    LOG.info(m)

    m.optimize(**optimize_kwargs)
    y_predicted_mean, y_predicted_var = m.predict(x_predict)

    return y_predicted_mean


def create_gaussian_process_kernel(kernel_type, input_dim, info=None, constraints=None):
    '''
    `kernel_type` is the name of the kernel. Currently available kernels:
    ['Add', 'BasisFuncKernel', 'Bias', 'Brownian', 'ChangePointBasisFuncKernel', 'Coregionalize', 'Cosine', 'DEtime', 'DiffGenomeKern', 'DomainKernel', 'EQ_ODE2', 'ExpQuad', 'Exponential', 'Fixed', 'Hierarchical', 'IndependentOutputs', 'Kern', 'Linear', 'LinearFull', 'LinearSlopeBasisFuncKernel', 'LogisticBasisFuncKernel', 'MLP', 'Matern32', 'Matern52', 'ODE_UY', 'ODE_UYC', 'ODE_st', 'ODE_t', 'OU', 'PeriodicExponential', 'PeriodicMatern32', 'PeriodicMatern52', 'Poly', 'Prod', 'RBF', 'RatQuad', 'Spline', 'SplitKern', 'StdPeriodic', 'TruncLinear', 'TruncLinear_inf', 'White'
    '''
    try:
        kernel = getattr(GPy.kern, kernel_type)
    except:
        raise ValueError("Error: Kernel {} is currently not implemented in GPy.kern:\n{}".format(kernel_type, str(dir(GPy.kern))))

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
        import pdb; pdb.set_trace()
        raise ValueError("Please check you kernel kwargs for kernel kernel_type: {} with input_dim: {}".format(kernel_type, input_dim))


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
            kernel_tmp = create_gaussian_process_kernel(input_dim=input_dim, kernel_type=kernel_type, info=kernel_info, constraints=kernel_constraints)
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



def calculate_BIC_Gaussian_process_model(model):

    """
    Calculate the Bayesian Information Criterion (BIC) for a (trained) GPy `model`.
    https://en.wikipedia.org/wiki/Bayesian_information_criterion


    ToDo: Check that model.log_likelihood() and model._size_transformed() are the correct inputs.
    ToDo: Check that len(model.X) is always the sample size.
    """

    # model._size_transformed() is the number of optimisation parameters, model.size the total number of parameters.
    # model.log_likelihood() is the natural logarithm of the marginal likelihood of the Gaussian process.
    return - 2 * model.log_likelihood() + len(model.X) * np.log(model._size_transformed())


