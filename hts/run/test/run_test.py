import os
import pytest

from hts.run.run import Run
from hts.plate_data.plate_layout import PlateLayout
from hts.protocol.protocol import Protocol

# Test file names
TEST_FOLDER_LUMINESCENCE_CSV = "luminescence_cell_viability_for_QC"
TEST_RUN_CONFIG_INSULIN = "run_config_insulin_1.txt"
TEST_RUN_CONFIG_SIRNA = "run_config_siRNA_1.txt"
TEST_RUN_CONFIG_SIRNA_MULTIPLE = "run_config_siRNA_2.txt"
TEST_RUN_CONFIG_XLSX = "run_config_siRNA_Marc_2015_08_17_Multiflo_5plates.txt"


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
def test_read_run_from_readouts(path_raw_data):
    test_run = Run.create(origin="envision", format="csv", dir=True,
                          path=os.path.join(path_raw_data, TEST_FOLDER_LUMINESCENCE_CSV))
    assert type(test_run) == Run
    assert len(test_run.plates) == 5


@pytest.mark.no_external_software_required
def test_read_run_from_single_file(path_run):
    test_run = Run.create(origin="config", path=os.path.join(path_run, TEST_RUN_CONFIG_XLSX))
    assert type(test_run) == Run
    assert len(test_run.plates) == 5


@pytest.mark.no_external_software_required
def test_read_run_from_config_insulin(path_run):
    test_run = Run.create(origin="config", path=os.path.join(path_run, TEST_RUN_CONFIG_INSULIN))
    assert type(test_run) == Run
    assert len(test_run.plates) == 2
    test_plate = test_run.plates["1"]
    test_height = 16
    assert test_plate.height == test_height
    assert test_run.height == test_height
    test_width = 24
    assert test_plate.width == test_width
    assert test_run.width == test_width
    assert len(test_plate.readout.data) == 481
    test_protocol = test_run.protocol()
    assert type(test_protocol) == Protocol
    test_plate_layout = test_run.plates["1"].plate_layout
    assert type(test_plate_layout) == PlateLayout


@pytest.mark.no_external_software_required
def test_do_qc_insulin(path_run):
    test_run = Run.create(origin="config", path=os.path.join(path_run, TEST_RUN_CONFIG_INSULIN))
    test_qc = test_run.qc()


@pytest.mark.no_external_software_required
def test_do_qc_siRNA(path_run):
    test_run = Run.create(origin="config", path=os.path.join(path_run, TEST_RUN_CONFIG_SIRNA))
    test_qc = test_run.qc()


@pytest.mark.no_external_software_required
def test_load_siRNA_multiple(path_run):
    test_run = Run.create(origin="config", path=os.path.join(path_run, TEST_RUN_CONFIG_SIRNA_MULTIPLE))

    assert len(test_run.plates) == 10
    assert len(test_run.plates["1"].readout.data) == 5

    test_qc = test_run.qc()

