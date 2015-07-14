import os
import pytest

from hts.qc.qc import QualityControl

# Test file names
TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"

notfixed = pytest.mark.notfixed

@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data')


@notfixed
@pytest.mark.no_external_software_required
def test_create_heatmap(path):
    # 1. Read a plate_map.
    # 2. Read some random data.
    # 3. Create a QC instance.
    test_qc = 1
    assert type(test_qc) == list
    assert len(test_qc[0].plate_read) == 2
    assert test_qc[0].parameters == TEST_FOLDER_LUMINESCENCE_CSV_FIRST_FILE_PARAMETERS
