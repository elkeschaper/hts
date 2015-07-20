import os
import pytest

from hts.plate import plate


import logging
logging.basicConfig(level=logging.INFO)

TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"
TEST_RUN_CONFIG = "run_config_insulin_1.txt"



notfixed = pytest.mark.notfixed


@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Raw_data')

@pytest.fixture
def path_insulin():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Raw_data', 'raw_data_insulin')


@notfixed
@pytest.mark.no_external_software_required
def test_create_from_csv(path):
    test_plate = plate.Plate.create(path = "abc", format = "csv")


@pytest.mark.no_external_software_required
def test_create_from_envision_csv(path):
    TEST_FILE_ENVISION = "mimic_jc-1_7.csv"
    test_plate = plate.Plate.create(path = os.path.join(path, TEST_FILE_ENVISION), format = "envision_csv")
    assert test_plate.name == TEST_FILE_ENVISION
    assert type(test_plate.raw_read_outs) == dict
    assert type(list(test_plate.raw_read_outs.values())[0]) == list

@pytest.mark.no_external_software_required
def test_create_from_insulin_csv(path_insulin):
    TEST_FILE_INSULIN = "150701_AmAmAs384_SanofiBatches12.csv"
    test_plate = plate.Plate.create(path = os.path.join(path_insulin, TEST_FILE_INSULIN), format = "insulin_csv")
    assert test_plate.name == TEST_FILE_INSULIN
    assert type(test_plate.raw_read_outs) == dict
    assert type(list(test_plate.raw_read_outs.values())[0]) == list