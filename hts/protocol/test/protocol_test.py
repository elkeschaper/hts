import os
import pytest

from hts.protocol import protocol

# Test file names
TEST_PROTOCOL_CONFIG = "protocol_config_generic.txt"
TEST_PROTOCOL_CONFIG_dPIA = "protocol_config_dPIA_1.txt"
TEST_PROTOCOL_CONFIG_insulin = "protocol_config_insulin_1.txt"
TEST_PROTOCOL_CONFIG_muscle_miRNA = "protocol_config_muscle_miRNA_1.txt"
TEST_PROTOCOL_CONFIG_siRNA = "protocol_config_siRNA_1.txt"

TEST_PREPROCESSING = ["calculate_net"]
TEST_QC = ["heat_map", "ssmd", "zz"]



import logging
logging.basicConfig(level=logging.DEBUG)

notfixed = pytest.mark.notfixed

@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Protocols')

@pytest.mark.no_external_software_required
def test_protocol_insuling(path):
    test_protocol = protocol.Protocol.create(os.path.join(path, TEST_PROTOCOL_CONFIG_insulin), format="config")
    assert test_protocol.name == TEST_PROTOCOL_CONFIG_insulin
    assert test_protocol.type == "Insulin"
    assert test_protocol.qc == {'1': {"methods": ["heat_map_multiple"], "filter": {"type": "run_wise", "tag": "(17,39)", "subset": ''}}, '2': {"methods": ["heat_map_multiple"], "filter": {"type": "plate_wise", "tag": "", "subset": "[(0,0), (17,39)]"}}}

@pytest.mark.no_external_software_required
def test_protocol(path):
    test_protocol = protocol.Protocol.create(os.path.join(path, TEST_PROTOCOL_CONFIG), format="config")
    assert test_protocol.name == TEST_PROTOCOL_CONFIG
    assert test_protocol.type == "siRNA_FRET"
    assert test_protocol.preprocessing == {"plate": TEST_PREPROCESSING}
    assert test_protocol.qc == {'1': {"methods": TEST_QC, "filter": {"type": "run_wise", "tag": "tag", "subset": ''}}}
