import os
import pytest

from hts.protocol import protocol

# Test file names
TEST_PROTOCOL_CONFIG = 'protocol_1_config.txt'

TEST_PREPROCESSING = ["calculate_net"]
TEST_QC = ["heat_map", "ssmd", "zz"]


import logging
logging.basicConfig(level=logging.DEBUG)

notfixed = pytest.mark.notfixed

@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data')

@pytest.mark.no_external_software_required
def test_read_envision_csv(path):
    test_protocol = protocol.protocol.create(os.path.join(path, TEST_PROTOCOL_CONFIG))
    assert test_protocol.type = "siRNA_FRET"
    assert test_protocol.name = TEST_PROTOCOL_CONFIG
    assert test_protocol.preprocessing = {"plate": TEST_PREPROCESSING}
    assert test_protocol.QC = {"methods": TEST_QC}

