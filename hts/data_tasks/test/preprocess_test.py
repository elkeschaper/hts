import os
import pytest

from hts.run.run import Run

# Test file names
TEST_RUN_CONFIG_SIRNA = "run_config_siRNA_1.txt"


notfixed = pytest.mark.notfixed

@pytest.fixture
def path_run():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Runs')


@pytest.fixture
def path_raw_data():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Raw_data')


@pytest.mark.no_external_software_required
def test_do_qc_siRNA(path_run):
    test_run = Run.create(origin="config", path=os.path.join(path_run, TEST_RUN_CONFIG_SIRNA))
    test_run.preprocess()
    assert len(test_run.plates['12593'].readout.data) == 3
    assert "net_fret" in test_run.plates['12593'].readout.data
