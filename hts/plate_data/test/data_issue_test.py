import os
import pytest
from hts.plate_data import data_issue

# Test file names
TEST_DATA_ISSUE = "manual.csv"
TEST_DATA_ISSUE_DATA = [[None]*24 for i in range(16)]
TEST_DATA_ISSUE_DATA[2][3] = "The pipette tip broke."
TEST_DATA_ISSUE_DATA[4][1] = "I spat in this well."
TEST_DATA_ISSUE_DATA[8][4] = "The Unispital was on fire."
TEST_DATA_ISSUE_DATA[10][0] = "Found chewing gum in this well."

import logging
logging.basicConfig(level=logging.INFO)

notfixed = pytest.mark.notfixed


@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data', 'Data_issues')


@pytest.mark.no_external_software_required
def test_read_manual_data_issue(path):
    test_data_issue = data_issue.DataIssue.create(formats=["csv"], paths=[os.path.join(path, "Manual", TEST_DATA_ISSUE)], remove_empty_row=False)
    assert test_data_issue.height == 16
    assert test_data_issue.width == 24
    assert test_data_issue.data[TEST_DATA_ISSUE] == TEST_DATA_ISSUE_DATA

