import ntpath
import os
import pytest

from hts.readout import readout, readout_dict
from hts.plate_layout.plate_layout import PlateLayout

import logging
logging.basicConfig(level=logging.INFO)

TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"
TEST_RUN_CONFIG = "run_config_insulin_1.txt"



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


@notfixed
@pytest.mark.no_external_software_required
def test_create_from_csv(path):
    test_plate = readout_dict.ReadoutDict.create(path = "abc", format = "csv")


@pytest.mark.no_external_software_required
def test_create_from_envision_csv(path_raw):
    TEST_FILE_ENVISION = os.path.join(path_raw, "mimic_jc-1_7.csv")
    test_plate = readout_dict.ReadoutDict.create(path = TEST_FILE_ENVISION, format = "envision_csv")
    assert test_plate.name == ntpath.basename(TEST_FILE_ENVISION)
    assert type(test_plate.read_outs) == dict
    assert type(list(test_plate.read_outs.values())[0]) == readout.Readout

@pytest.mark.no_external_software_required
def test_create_from_insulin_csv(path_raw):
    TEST_FILE_INSULIN = os.path.join(path_raw, "raw_data_insulin", "150701_AmAmAs384_SanofiBatches12.csv")
    test_plate = readout_dict.ReadoutDict.create(path = TEST_FILE_INSULIN, format = "insulin_csv")
    assert test_plate.name == ntpath.basename(TEST_FILE_INSULIN)
    assert type(test_plate.read_outs) == dict
    assert type(list(test_plate.read_outs.values())[0]) == readout.Readout


@pytest.mark.no_external_software_required
def test_calculate_net_fret(path, path_raw):
    TEST_FILE_SIRNA = os.path.join(path_raw, "siRNA", "siRNA_12595.csv")
    test_plate = readout_dict.ReadoutDict.create(path = TEST_FILE_SIRNA, format = "envision_csv")
    TEST_PLATELAYOUT = os.path.join(path, "Plate_layouts", "plate_layout_siRNA_20150708_old_setup_Marc.csv")
    test_plate_layout = PlateLayout.create(path=TEST_PLATELAYOUT, format="csv")
    test_plate.set_plate_layout(plate_layout=test_plate_layout)
    # Add plate_layout
    test_plate.calculate_net_fret(donor_channel="2", acceptor_channel="1")
    assert type(test_plate.read_outs["net_fret"]) == readout.Readout
    # Update the next line!
    assert test_plate.read_outs["net_fret"].data == []