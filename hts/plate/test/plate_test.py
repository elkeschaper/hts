import ntpath
import os
import logging

import numpy
import pytest

from hts.plate import plate
from hts.plate_data import readout
from hts.plate_data.plate_layout import PlateLayout

logging.basicConfig(level=logging.INFO)

TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"
TEST_RUN_CONFIG = "run_config_insulin_1.txt"
TEST_FILE_INSULIN = os.path.join("insulin", "test_1.csv")
TEST_FILE_SIRNA = os.path.join("siRNA", "siRNA_12595.csv")
TEST_PLATELAYOUT = os.path.join("Plate_layouts", "plate_layout_siRNA_1.csv")
TEST_PLATE_COLUMN_7_s_1 = [107514.0, 106208.0, 101280.0, 99894.0, 103955.0, 101470.0]

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


@pytest.mark.no_external_software_required
def test_create_from_insulin_csv(path_raw):

    config = {"readout": {"path": os.path.join(path_raw, TEST_FILE_INSULIN), "config": {"format": "insulin_csv"}}}
    test_plate = plate.Plate.create(format="config", **config)

    assert test_plate.name == ntpath.basename(TEST_FILE_INSULIN)
    assert type(test_plate.readout) == readout.Readout
    assert len(test_plate.readout.data) == 481
    assert type(test_plate.readout.data[0]) == numpy.ndarray


@pytest.mark.no_external_software_required
def test_calculate_net_fret(path, path_raw):

    config = {"readout": {"path": os.path.join(path_raw, TEST_FILE_SIRNA), "config": {"format": "envision_csv"}},
              "plate_layout": {"path": os.path.join(path, TEST_PLATELAYOUT), "config": {"format": "csv"}}
              }
    test_plate = plate.Plate.create(format="config", **config)

    test_plate.calculate_net_fret(donor_channel="2", acceptor_channel="1")
    assert type(test_plate.readout) == readout.Readout
    assert type(test_plate.readout.data["net_fret"]) == numpy.ndarray


@pytest.mark.no_external_software_required
def test_filter_wells(path, path_raw):

    config = {"readout": {"path": os.path.join(path_raw, TEST_FILE_SIRNA), "config": {"format": "envision_csv"}},
              "plate_layout": {"path": os.path.join(path, TEST_PLATELAYOUT), "config": {"format": "csv"}}
              }
    test_plate = plate.Plate.create(format="config", **config)

    test_neg = test_plate.filter(condition_data_type="plate_layout", condition_data_tag="layout", condition=lambda x: x=="s_1",
                                 value_data_type="readout", value_data_tag="1", value_type=None)
    assert type(test_neg) == list
    assert all([i in test_neg for i in TEST_PLATE_COLUMN_7_s_1])

