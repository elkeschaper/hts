# (C) 2015, 2016 Elke Schaper @ Vital-IT, Swiss Institute of Bioinformatics

"""
    .. moduleauthor:: Elke Schaper <elke.schaper@sib.swiss>
"""

import logging

import GPy
import numpy as np

from hts.data_tasks.gaussian_processes import create_gaussian_process_composite_kernel

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



