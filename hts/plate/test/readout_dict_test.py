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
TEST_PLATELAYOUT = os.path.join("Plate_layouts", "plate_layout_siRNA_Marc_20150708_old_setup.csv")
TEST_PLATELAYOUT = os.path.join("Plate_layouts", "plate_layout_siRNA_1.csv")

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
    test_plate = plate.Plate.create(path=os.path.join(path_raw, TEST_FILE_INSULIN), format="insulin_csv")
    assert test_plate.name == ntpath.basename(TEST_FILE_INSULIN)
    assert type(test_plate.read_outs) == dict
    assert type(list(test_plate.read_outs.values())[0]) == readout.Readout


@pytest.mark.no_external_software_required
def test_calculate_net_fret(path, path_raw):
    test_plate = plate.Plate.create(path=os.path.join(path_raw, TEST_FILE_SIRNA), format="envision_csv")
    test_plate_layout = PlateLayout.create(path=os.path.join(path, TEST_PLATELAYOUT), format="csv") # Add plate_data
    test_plate.set_plate_layout(plate_layout=test_plate_layout)

    test_plate.calculate_net_fret(donor_channel="2", acceptor_channel="1")
    assert type(test_plate.read_outs["net_fret"]) == readout.Readout
    assert type(test_plate.read_outs["net_fret"].data) == numpy.ndarray