import configobj
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
    assert test_protocol.name == TEST_PROTOCOL_CONFIG
    assert test_protocol.type == "generic_test"
    assert test_protocol.format == "csv"
    assert type(test_protocol.preprocessing) == configobj.Section
    assert type(test_protocol.analysis) == configobj.Section
    assert type(test_protocol.qc) == dict
    assert "qc_methods" in test_protocol.qc
    assert "type" in test_protocol.qc


@pytest.mark.no_external_software_required
def test_protocol_insulin(path):
    test_protocol = protocol.Protocol.create(os.path.join(path, TEST_PROTOCOL_CONFIG_insulin), format="config")
    assert test_protocol.name == TEST_PROTOCOL_CONFIG_insulin
    assert test_protocol.type == "insulin"
    assert test_protocol.format == "csv"
    assert "qc_methods" in test_protocol.qc
    assert len(test_protocol.qc["qc_methods"]) == 2
