import os
import pytest

from hts.protocol import protocol

# Test file names
TEST_PROTOCOL_CONFIG = "protocol_config_generic.txt"
TEST_PROTOCOL_CONFIG_insulin = "protocol_config_insulin_1.txt"


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
def test_protocol_generic(path):
    test_protocol = protocol.Protocol.create(os.path.join(path, TEST_PROTOCOL_CONFIG), format="config")
    assert test_protocol.file == TEST_PROTOCOL_CONFIG
    assert test_protocol.name == "generic_test"
    assert type(test_protocol.tasks) == list
    assert type(test_protocol.tasks[0]) == protocol.ProtocolTask
    assert len(test_protocol.tasks) == 4

    # Test ProtocolTask
    assert test_protocol.tasks[0].name == "Hey, let's calculate net fret"
    assert test_protocol.tasks[0].tags == ['preprocessing']
    assert test_protocol.tasks[0].type == 'preprocessing'
    assert test_protocol.tasks[0].method == 'calculate_net_fret'
    assert test_protocol.tasks[0].config == {'donor_channel': '2', 'acceptor_channel': '1', 'net_fret_key': 'net_fret'}


@pytest.mark.no_external_software_required
def test_protocol_insulin(path):
    test_protocol = protocol.Protocol.create(os.path.join(path, TEST_PROTOCOL_CONFIG_insulin), format="config")
    assert test_protocol.file == TEST_PROTOCOL_CONFIG_insulin
    assert test_protocol.name == "insulin_1"
    assert type(test_protocol.tasks) == list
    assert type(test_protocol.tasks[0]) == protocol.ProtocolTask
    assert len(test_protocol.tasks) == 3
