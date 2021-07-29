"""
Unit and regression test for the nmrplot package.
"""

import sys

# Import package, test suite, and other packages as needed
import nmrplot
import pytest


def test_nmrplot_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "nmrplot" in sys.modules
