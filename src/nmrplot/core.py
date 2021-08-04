#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The core module of nmrplot.
Contains the Spectrum class, which is the main class of nmrplot, and a number of extras.
"""
from locale import normalize
from math import prod
from os import path

import matplotlib.pyplot as plt
import nmrglue as ng
import numpy as np
from matplotlib import cm
from skimage.exposure.exposure import histogram
from sklearn.preprocessing import RobustScaler

cmapdict = {
    # sequential colormaps for only positive values
    "red": plt.cm.Reds_r,
    "blue": plt.cm.Blues_r,
    "green": plt.cm.Greens_r,
    "purple": plt.cm.Purples_r,
    "orange": plt.cm.Oranges_r,
    "grey": plt.cm.Greys_r,
    "light_red": plt.cm.YlOrRd_r,
    "light_blue": plt.cm.GnBu_r,
    "viridis": plt.cm.viridis,
    # diverging colormaps for positive/negative values
    "coolwarm": plt.cm.coolwarm,
    "earth": plt.cm.gist_earth,
}


def load_bruker(expno_path, pdata=1):
    """Load a processed spectrum in Bruker format and return data and spectral parameters.

    Args:
        expno_path (str): Path to experiment folder (i.e. to experiment_name/expno)
        pdata (int, optional): Number of proccessing. Defaults to 1.

    Returns:
        dic (dic): Dictionary of Bruker NMR parameters.
        data (np.ndarray): Processed NMR spectum as an array of intensities.
    """

    pdata_path = path.join(expno_path, f"pdata/{pdata}")
    dic, data = ng.bruker.read_pdata(pdata_path)

    return dic, data


class Spectrum:
    """An object contiaining a spectrum and its parameters"""

    def __init__(self, expno_path, pdata=1, normalize=True):
        self.dic, self.data = load_bruker(expno_path, pdata)
        self.udic = ng.bruker.guess_udic(self.dic, self.data)
        self.ndim = self.data.ndim
        self.normalized = False
        # go through each dimension inversely to keep the right order.
        # last dimension is the directly detected, goes to X axis
        self.label = tuple(self.udic[i]["label"] for i in reversed(range(self.ndim)))
        self.sw = tuple(self.udic[i]["sw"] for i in reversed(range(self.ndim)))
        self.obs = tuple(self.udic[i]["obs"] for i in reversed(range(self.ndim)))
        self.freq = tuple(self.udic[i]["freq"] for i in reversed(range(self.ndim)))
        self.get_ppm_ranges()
        self.calc_baseline()
        if normalize:
            self.normalize_data()
        self.calc_signal_to_noise()

    def get_ppm_ranges(self):
        """Return the ppm ranges of the spectrum"""
        self.ppm_ranges = []
        # go through each dimension inversely to keep the right order.
        for i in reversed(range(self.ndim)):
            converter = ng.fileiobase.uc_from_udic(self.udic, dim=i)
            self.ppm_ranges.append(converter.ppm_limits())
        # flatten the range list
        self.ppm_ranges = [item for sublist in self.ppm_ranges for item in sublist]
        return self.ppm_ranges

    def calc_histogram(self):
        """Return the histogram of the spectrum"""
        counts, bins = histogram(self.data.flatten())
        return counts, bins

    def calc_baseline(self):
        """Determine the spectral baseline using the mode"""
        counts, bins = self.calc_histogram()
        self.baseline = bins[np.argmax(counts)]
        return self.baseline

    def normalize_data(self):
        """Normalize the data to the baseline and make it zero"""
        self.data = (self.data - self.baseline) / abs(self.baseline)
        self.calc_baseline()
        self.normalized = True

    def calc_signal_to_noise(self):
        """Return the signal to noise ratio of the spectrum
        Based on SNR definition by Hyberts et al. (2013)
        https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3570699/
        """
        # define signal as the maximum intensity in the spectrum
        self.signal = self.data.max()
        # define an empty region as the lowest decile of the spectrum
        empty = self.data[self.data < np.quantile(self.data, 0.1)]
        # define the noise as the standard deviation of the empty region
        self.noise = empty.std()
        # calculate the signal to noise ratio
        self.snr = self.signal / self.noise
        return self.snr, self.signal, self.noise

    def calc_clevs(self, threshold, nlevs, factor):
        """Return the contour levels for plotting

        Args:
            threshold (float, optional): Lowest contour drawn as a multiple of the spectral noise.
            nlevs (int, optional): Number of contour levels.
            factor (float, optional): exponential increment between contours.

        Returns:
            self.clevs (np.array): An array of intensities.
        """
        if threshold is None:
            # A good guess is the lowest contour should be 1/100 of the maximum intensity
            startlev = self.baseline + self.signal * 0.01
            # Calculate the corresponding threshold
            threshold = (self.signal * 0.01) / self.noise
        else:
            startlev = self.baseline + (threshold * self.noise)
        print(f"Lowest contour level is at {threshold:.1f}*noise above the baseline")
        self.clevs = startlev * factor ** np.arange(nlevs)
        return self.clevs

    def plot_histogram(self):
        """Plot the histogram of the spectrum"""
        bins, counts = self.calc_histogram()
        plt.hist(bins, counts)
        plt.show()

    def plot_spectrum(self, threshold, nlevs=42, factor=1.1, cmap="viridis"):
        """Plot the spectrum.
        WARNING: Only shows the positive values.

        Args:
            threshold (float, optional): Lowest contour drawn as a multiple of the spectral noise.
            nlevs (int, optional): Number of contour levels.
            factor (float, optional): exponential increment between contours.
            cmap (str, optional): Colormap to be used. Other options are: "red", "blue", "green", "purple", "orange", "grey", "light_red", "light_blue", "coolwarm", "gist_earth".
        """

        if self.ndim == 1:
            fig, ax = plt.subplots()
            ppm_scale = np.linspace(
                self.ppm_ranges[0], self.ppm_ranges[1], self.data.size
            )
            ax.plot(ppm_scale, self.data, linewidth=1.0)
            ax.set_xlim(*self.ppm_ranges)
            ax.set_xlabel(f"{self.label[0]} ppm")
            ax.set_ylabel("Intensity (A.U.)")
            plt.show()

        elif self.ndim == 2:
            self.calc_clevs(threshold, nlevs, factor)
            fig, ax = plt.subplots()
            ax.contour(
                self.data,
                self.clevs,
                extent=self.ppm_ranges,
                linewidths=0.5,
                cmap=cmapdict[cmap],
                # cut down the extremes of the color scale
                # the dynamic range is very large, otherwise extremes are too dark/light
                vmin=self.clevs.min() * 1.2,
                vmax=self.clevs.max() * 0.8,
            )
            ax.set_xlim(*self.ppm_ranges[:2])
            ax.set_ylim(*self.ppm_ranges[2:])
            ax.set_xlabel(f"{self.label[0]} ppm")
            ax.set_ylabel(f"{self.label[1]} ppm")
            plt.show()
        else:
            print("The spectrum is not 1D or 2D")
