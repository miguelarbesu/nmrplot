"""
Unit and regression test for the nmrplot package.
"""

import glob
import sys
from locale import normalize

# Import package, test suite, and other packages as needed
import nmrplot
import pytest
from nmrplot.core import Spectrum


def test_nmrplot_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "nmrplot" in sys.modules


def test_spectrum():
    """
    Test the spectrum class for ndim = {1, 2}, hetero or homonuclear
    """
    for path in glob.glob("..src/data/*"):
        Spectrum = nmrplot.core.Spectrum("path")
        # Check if dimensions are correct for all parameters
        for length in [
            len(x)
            for x in [Spectrum.data.shape, Spectrum.label, Spectrum.sw, Spectrum.freq]
        ]:
            assert length == Spectrum.ndim
        Spectrum.get_ppm_ranges
        assert len(Spectrum.ppm_ranges) == 2 * Spectrum.ndim
        # assert x>y for each pair in spectrum.ppm_ranges
        assert all(
            Spectrum.ppm_ranges[i] > Spectrum.ppm_ranges[i + 1]
            for i in range(Spectrum.ndim, step=2)
        )
        # assert baseline is near zero
        if Spectrum.normalize is True:
            assert Spectrum.baseline == pytest.approx(0, abs=1e-3)
        # check data
        assert Spectrum.signal > Spectrum.noise
