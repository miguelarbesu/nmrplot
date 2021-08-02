#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A module template
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
    "red": plt.cm.Reds_r,
    "blue": plt.cm.Blues_r,
    "green": plt.cm.Greens_r,
    "purple": plt.cm.Purples_r,
    "orange": plt.cm.Oranges_r,
    "grey": plt.cm.Greys_r,
    "light_red": plt.cm.YlOrRd_r,
    "light_blue": plt.cm.GnBu_r,
    "viridis": plt.cm.viridis,
}


def load_bruker(expno_path, pdata=1):
    """Load a processed spectrum in Bruker format

    Arguments:
        expno_path {str} -- Path to experiment folder (i.e. to experiment_name/expno)
        pdata {int} -- Number of proccessing (default: {1})
    Returns:
        udic {dic} -- Universal dictionary of NMR parameters.
        data {np.ndarray} -- Signal intensities in a.u.
    """
    pdata_path = path.join(expno_path, f"pdata/{pdata}")
    dic, data = ng.bruker.read_pdata(pdata_path)

    return dic, data


class Spectrum:
    def __init__(self, expno_path, pdata=1, normalize=True):
        self.dic, self.data = load_bruker(expno_path, pdata)
        self.udic = ng.bruker.guess_udic(self.dic, self.data)
        self.ndim = self.data.ndim
        self.normalized = False
        self.dimensions = tuple(self.udic[i]["label"] for i in range(self.ndim))
        self.sw = tuple(self.udic[i]["sw"] for i in range(self.ndim))
        self.obs = tuple(self.udic[i]["obs"] for i in range(self.ndim))
        self.freq = tuple(self.udic[i]["freq"] for i in range(self.ndim))
        self.get_ppm_ranges()
        self.calc_baseline()
        if normalize:
            self.normalize_data()
        self.calc_signal_to_noise()

    def get_ppm_ranges(self):
        """Return the ppm ranges of the spectrum"""
        self.ppm_ranges = []
        for i in range(self.ndim):
            converter = ng.fileiobase.uc_from_udic(self.udic, dim=i)
            self.ppm_ranges.append(converter.ppm_limits())
        # reverse the order of the ppm_ranges so it matches the dimensions
        self.ppm_ranges = self.ppm_ranges[::-1]
        # flatten the list
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
        """Return the signal to noise ratio of the spectrum"""
        self.signal = self.data.sum()
        self.noise = self.data.var()
        self.snr = self.signal / self.noise
        return self.snr, self.signal, self.noise

    def calc_clevs(self, threshold=0.1, nlevs=42, factor=1.1):
        """Return the contour levels for plotting"""
        startlev = threshold * self.noise
        self.clevs = startlev * factor ** np.arange(nlevs)
        return self.clevs

    def plot_histogram(self):
        """Plot the histogram of the spectrum"""
        bins, counts = self.calc_histogram()
        plt.hist(bins, counts)
        plt.show()

    def plot_spectrum(self, threshold=0.1, nlevs=42, factor=1.1, cmap="viridis"):
        """Plot the spectrum"""
        if self.ndim == 1:
            fig, ax = plt.subplots()
            ppm_scale = np.linspace(
                self.ppm_ranges[0], self.ppm_ranges[1], self.data.size
            )
            ax.plot(ppm_scale, self.data, linewidth=1.0)
            ax.set_xlim(*self.ppm_ranges)
            ax.set_xlabel(f"{self.dimensions[0]} ppm")
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
                vmin=self.clevs.min() * 1.2,
                vmax=self.clevs.max() * 0.8,
            )
            ax.set_xlim(*self.ppm_ranges[:2])
            ax.set_ylim(*self.ppm_ranges[2:])
            ax.set_xlabel(f"{self.dimensions[0]} ppm")
            ax.set_ylabel(f"{self.dimensions[1]} ppm")
            plt.show()
        else:
            print("The spectrum is not 1D or 2D")
