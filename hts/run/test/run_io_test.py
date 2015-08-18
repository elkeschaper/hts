import os
import pytest

from hts.run import run, run_io

# Test file names
TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"
TEST_RUN_CONFIG_INSULIN = "run_config_insulin_1.txt"
TEST_RUN_CONFIG_SIRNA = "run_config_siRNA_1.txt"

notfixed = pytest.mark.notfixed

@pytest.fixture
def path_run():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Runs')



@pytest.mark.no_external_software_required
def test_write_run_csv_insulin(path_run):
    test_run = run.Run.create(origin="config",
                        path=os.path.join(path_run, TEST_RUN_CONFIG_INSULIN))
    test_serial = run_io.serialize_run_for_r(test_run)
    assert type(test_serial) == list
    assert len(test_serial[0]) == len(test_serial[1])


@pytest.mark.no_external_software_required
def test_write_run_csv_insulin(path_run):
    test_run = run.Run.create(origin="config",
                        path=os.path.join(path_run, TEST_RUN_CONFIG_SIRNA))
    test_serial = run_io.serialize_run_for_r(test_run)
    assert type(test_serial) == list
    assert len(test_serial[0]) == len(test_serial[1])



