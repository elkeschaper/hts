import collections
import os
import pytest

from hts.paths import DATA_DIRECTORY
from hts.run import run, run_io

# Test file names
TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"
TEST_RUN_CONFIG_INSULIN = "run_config_insulin_1.txt"
TEST_RUN_CONFIG_SIRNA = "run_config_siRNA_1.txt"

TEST_RUN_ONE_WELL_PER_ROW = os.path.join("run_one_well_per_row_csv", "test.csv")

notfixed = pytest.mark.notfixed

@pytest.fixture
def path_run():
    """Return the path to the test data files.
    """
    return os.path.join(DATA_DIRECTORY,  'Runs')


@pytest.fixture
def path_raw():
    """Return the path to the test data files.
    """
    return os.path.join(DATA_DIRECTORY,  'Raw_data')


@pytest.mark.no_external_software_required
def test_write_run_csv_insulin(path_run):
    test_run = run.Run.create(origin="config",
                        path=os.path.join(path_run, TEST_RUN_CONFIG_INSULIN))
    test_serial = run_io.serialize_run_for_r(test_run)
    assert type(test_serial) == str
    # In future, check whether all lines in test_serial are of the same length


@pytest.mark.no_external_software_required
def test_write_run_csv_insulin(path_run):
    test_run = run.Run.create(origin="config",
                        path=os.path.join(path_run, TEST_RUN_CONFIG_SIRNA))
    test_serial = run_io.serialize_run_for_r(test_run)
    assert type(test_serial) == str
    # In future, check whether all lines in test_serial are of the same length



@pytest.mark.no_external_software_required
def test_read_run_data(path_raw):

    TEST_RUN_ONE_WELL_PER_ROW_PARAMS = {"column_plate_name": "Plate ID", "column_well": "Well ID",
                                        "columns_readout": ["Data0", "Data1"], "columns_meta": ["Data2"],
                                        "width": 24, "height": 16}

    test_run_data = run_io.read_csv(file=os.path.join(path_raw, TEST_RUN_ONE_WELL_PER_ROW), **TEST_RUN_ONE_WELL_PER_ROW_PARAMS)
    assert type(test_run_data) == list
    assert test_run_data[0].name.startswith("info_")
    test_data = [i for i in test_run_data if i.name == "info_0554"][0]
    assert test_data.readout.data["Data1"][0][0] == 17521
    assert test_data.readout.data["Data0"][2][1] == 11822
    assert test_data.meta_data.data["Data2"][5][7] == "8.35"

