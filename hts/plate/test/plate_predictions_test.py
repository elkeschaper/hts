import itertools
import logging
import os

import numpy as np
import pytest

import hts.data_tasks.gaussian_processes
from hts.data_tasks import prediction
from hts.plate import plate
from hts.plate_data import plate_layout, readout

logging.basicConfig(level=logging.INFO)

TEST_FILE_SIRNA = os.path.join("siRNA", "siRNA_12595.csv")
TEST_PLATELAYOUT = os.path.join("Plate_layouts", "plate_layout_siRNA_1.csv")

TEST_PLATE_NAME = "test_plate"

TEST_PLATELAYOUT_GPY = os.path.join("Plate_layouts", "plate_layout_gpy_1.csv")


notfixed = pytest.mark.notfixed


@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath("."), "../", "test_data")

@pytest.fixture
def path_raw():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath("."), "../", "test_data", "Raw_data")

@pytest.fixture
def create_simulate_test_readout(plate_name, h=16, w=24):

    def numpify(y, h, w):
        return np.array([y[i*w:(i+1)*w] for i in range(h)])

    x = [(i,j) for i,j in itertools.product(range(h), range(w))]
    #y = np.sin(x[:,0:1]/2) * np.sin(x[:,1:2]/4)+ np.random.randn(len(x),1)*0.005
    #y = np.sin(x[:,0:1]/2 + x[:,1:2]/3)
    #y = [y[i*w:(i+1)*w] for i in range(h)]

    y0 = [np.sin(ix[0]/3 * ix[1]/6) for ix in x]
    y2 = [np.sin(ix[0]/3 + ix[1]/2) for ix in x]
    y3 = [(ix[0]/((h-1)/2) - 1)**2 + (ix[1]/((w-1)/2) - 1)**2 for ix in x]
    y = numpify(y0, h, w) + numpify(y3, h, w)*2

    test_plate = [[str(i) for i in row] for row in y]
    test_data = {plate_name: test_plate}

    return readout.Readout(data=test_data)


@pytest.mark.no_external_software_required
def test_model_as_gaussian_process(path, path_raw):

    config = {"readout": {"paths": [os.path.join(path_raw, TEST_FILE_SIRNA)], "formats": ["envision_csv"]},
              "plate_layout": {"paths": [os.path.join(path, TEST_PLATELAYOUT)], "formats": ["csv"]}
              }
    test_plate = plate.Plate.create(format="config", **config)
    test_plate.model_as_gaussian_process(data_tag_readout="1", sample_tag="pos")


@pytest.mark.no_external_software_required
def test_model_as_gaussian_process_from_simulated_data(path, path_raw):

    h = 16
    w = 24
    test_readout = create_simulate_test_readout(h=h, w=w, plate_name=TEST_PLATE_NAME)
    test_plate_layout = plate_layout.PlateLayout.create(formats=["csv"], paths=[os.path.join(path, TEST_PLATELAYOUT_GPY)])
    test_plate = plate.Plate(data={"readout": test_readout, "plate_layout": test_plate_layout}, height=test_readout.height, width=test_readout.width, name=TEST_PLATE_NAME)

    assert type(test_plate) == plate.Plate
    assert test_plate.name == TEST_PLATE_NAME
    assert test_plate.height == test_readout.height
    assert test_plate.width == test_readout.width

    test_predictions_mean_abs, test_predictions_sd = \
        test_plate.apply_gaussian_process(data_tag_readout=TEST_PLATE_NAME, sample_tag_input="pos")

    assert test_predictions_mean_abs.ndim == 2
    assert test_predictions_mean_abs.shape == (16, 24)
    assert test_predictions_sd.shape == (16, 24)

    test_error = test_plate.evaluate_well_value_prediction(data_predictions=test_predictions_mean_abs, data_tag_readout=TEST_PLATE_NAME)
    assert abs(test_error - 2.5) < 1

    test_error = test_plate.evaluate_well_value_prediction(data_predictions=test_predictions_mean_abs, data_tag_readout=TEST_PLATE_NAME, sample_key="pos")
    assert abs(test_error - 0) < 0.001

    test_error = test_plate.evaluate_well_value_prediction(data_predictions=test_predictions_mean_abs, data_tag_readout=TEST_PLATE_NAME, sample_key="neg")
    assert abs(test_error - 1.5) < 0.1


@pytest.mark.no_external_software_required
def test_calculate_BIC_for_gaussian_process_models(path, path_raw):

    h = 16
    w = 24
    test_readout = create_simulate_test_readout(h=h, w=w, plate_name=TEST_PLATE_NAME)
    test_plate_layout = plate_layout.PlateLayout.create(formats=["csv"], paths=[os.path.join(path, TEST_PLATELAYOUT_GPY)])
    test_plate = plate.Plate(data={"readout": test_readout, "plate_layout": test_plate_layout}, height=test_readout.height, width=test_readout.width, name=TEST_PLATE_NAME)
    test_kernels = {"RBF": {"lengthscale": ("constrain_fixed", "4")}}
    m, y_mean, y_std = test_plate.model_as_gaussian_process(data_tag_readout=TEST_PLATE_NAME, sample_tag="pos", kernels=test_kernels)

    test_BIC = hts.data_tasks.gaussian_processes.calculate_BIC_Gaussian_process_model(m)
    assert type(test_BIC) == np.float64
    assert test_BIC > 0


def test_control_normalization(path, path_raw):


    config = {"readout": {"paths": [os.path.join(path_raw, TEST_FILE_SIRNA)], "formats": ["envision_csv"]},
              "plate_layout": {"paths": [os.path.join(path, TEST_PLATELAYOUT)], "formats": ["csv"]}
              }
    test_plate = plate.Plate.create(format="config", **config)
    test_plate.calculate_net_fret(donor_channel="2", acceptor_channel="1")

    test_plate.calculate_control_normalized_signal(data_tag_readout="net_fret",
                                                   negative_control_key="neg_1",
                                                   positive_control_key="pos"
                                                   )

    assert "net_fret_normalized_by_controls" in test_plate.readout.data
    assert "net_fret_pvalue_vs_neg_control" in test_plate.readout.data
    assert type(test_plate.readout.data["net_fret_normalized_by_controls"]) == np.ndarray


def test_cross_validation(path):

    h = 16
    w = 24
    test_readout = create_simulate_test_readout(h=h, w=w, plate_name=TEST_PLATE_NAME)
    test_plate_layout = plate_layout.PlateLayout.create(formats=["csv"], paths=[os.path.join(path, TEST_PLATELAYOUT_GPY)])
    test_plate = plate.Plate(data={"readout": test_readout, "plate_layout": test_plate_layout}, height=test_readout.height, width=test_readout.width, name=TEST_PLATE_NAME)

    #kwargs = {"kernel": "a"}
    kwargs = {}

    test_error = test_plate.cross_validate_predictions(p=1, data_tag_readout=TEST_PLATE_NAME, sample_tag="pos", method_name="gp", **kwargs)
    assert type(test_error) == list
    assert test_error == []

