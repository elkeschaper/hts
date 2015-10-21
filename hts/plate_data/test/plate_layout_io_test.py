import os
import pytest

from hts.plate_data import plate_layout_io

# Test file names
TEST_LAYOUT_siRNA = 'plate_layout_siRNA_1.csv'
TEST_LAYOUT_dpia = 'plate_layout_dPIA_1.csv'
TEST_LAYOUT_insulin = 'plate_layout_insulin_1.csv'

import logging
logging.basicConfig(level=logging.INFO)

TEST_LAYOUT_MUSCLE = [['medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'medium', 'medium'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'fluorophore_donor', 'fluorophore_donor'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'fluorophore_donor', 'fluorophore_donor'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'fluorophore_acceptor', 'fluorophore_acceptor'], ['medium', 'medium', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'pos', 'neg_1', 'neg_2', 's_1', 'neg_3', 'neg_3', 'medium', 'medium', 'fluorophore_acceptor', 'fluorophore_acceptor'], ['medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'buffer', 'buffer'], ['medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'medium', 'buffer', 'buffer']]


notfixed = pytest.mark.notfixed

@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Plate_layouts')

@pytest.mark.no_external_software_required
def test_read_plate_layout_siRNA(path):
    test_plate_layout = plate_layout_io.read_csv(os.path.join(path, TEST_LAYOUT_siRNA))
    assert test_plate_layout == TEST_LAYOUT_MUSCLE


@pytest.mark.no_external_software_required
def test_read_plate_layout_insulin(path):
    test_plate_layout = plate_layout_io.read_csv(os.path.join(path, TEST_LAYOUT_insulin))


@pytest.mark.no_external_software_required
def TEST_LAYOUT_dpia(path):
    test_plate_layout = plate_layout_io.read_csv(os.path.join(path, TEST_LAYOUT_dpia))

