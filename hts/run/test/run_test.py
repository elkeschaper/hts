import os
import pytest

from hts.run.run import Run

# Test file names
TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_QC"
TEST_FOLDER_LUMINESCENCE_CSV_FIRST_FILE_PARAMTERS = {'Ambient temperature at end': 'N/A', 'Humidity at end': 'N/A', 'Measured height': 'N/A', 'Formula': 'Calc 1: Crosstalk = Crosstalk correction where Label : US LUM 384 (cps)(1) channel 1', 'Chamber temperature at end': 'N/A', 'Measurement date': '5/23/2015 16:33:33', 'Plate': '1', 'Humidity at start': 'N/A', 'Repeat': '1', 'Chamber temperature at start': 'N/A', 'Barcode': '', 'Ambient temperature at start': 'N/A'}

notfixed = pytest.mark.notfixed

@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data')


#@notfixed
@pytest.mark.no_external_software_required
def test_read_entire_assay(path):
    test_data = Run.create(origin="envision", format="csv",  dir=True,
                        path=os.path.join(path, TEST_FOLDER_LUMINESCENCE_CSV))
    assert type(test_data) == list
    assert len(test_data[0].plate_read) == 2
    assert test_data[0].parameters == TEST_FOLDER_LUMINESCENCE_CSV_FIRST_FILE_PARAMETERS
