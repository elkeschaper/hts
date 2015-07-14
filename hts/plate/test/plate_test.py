import os
import pytest

from hts.plate import plate


import logging
logging.basicConfig(level=logging.INFO)


notfixed = pytest.mark.notfixed

@pytest.fixture
def path():
    """Return the path to the test data files.
    """
    return os.path.join(os.path.abspath('.'), '../', 'test_data')



