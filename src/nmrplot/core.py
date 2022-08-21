#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The core module of nmrplot.
Contains the Spectrum class, which is the main class of nmrplot, and a number of extras.
"""
from os import path

import matplotlib.pyplot as plt
import nmrglue as ng
import numpy as np
from matplotlib.colors import LogNorm, SymLogNorm
from skimage.exposure.exposure import histogram

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
    # "earth": plt.cm.gist_earth,
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
    """An object containing a spectrum and its parameters"""

    def __init__(self, expno_path, pdata=1, normalize=True, sign="positive"):
        self.dic, self.data = load_bruker(expno_path, pdata)
        self.udic = ng.bruker.guess_udic(self.dic, self.data)
        self.ndim = self.data.ndim
        self.sign = sign
        self.normalized = False
        # go through each dimension inversely to keep the right order.
        # last dimension is the directly detected, goes to X axis
        self.label = tuple(self.udic[i]["label"] for i in reversed(range(self.ndim)))
        self.sw = tuple(self.udic[i]["sw"] for i in reversed(range(self.ndim)))
        self.obs = tuple(self.udic[i]["obs"] for i in reversed(range(self.ndim)))
        self.freq = tuple(self.udic[i]["freq"] for i in reversed(range(self.ndim)))
        self.get_ppm_ranges()
        self.get_points()
        self.calc_baseline()
        # data is normalized by default
        if normalize is True:
            self.normalize_data()
        self.calc_signal_to_noise()
        self.calc_threshold()
        self.calc_ppm_meshgrid()

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

    def get_points(self):
        """Return the number of points of the spectrum in each dimension"""
        # order is reversed to be consistent with the ppm_ranges
        # reverse data.shape to get the right order
        self.points = tuple(self.data.shape[i] for i in reversed(range(self.ndim)))
        return self.points

    def calc_ppm_meshgrid(self):
        """Return the ppm grid of the spectrum for plotting"""

        if self.ndim == 1:
            self.ppm_meshgrid = np.linspace(
                self.ppm_ranges[0], self.ppm_ranges[1], self.points[0]
            )

        elif self.ndim > 1:
            ppm_ranges = [tuple(i) for i in np.array_split(self.ppm_ranges, 2)]
            ppm_arrays = []
            for points, ranges in zip(self.points, ppm_ranges):
                ppm_arrays.append(np.linspace(ranges[0], ranges[1], points))
            self.ppm_meshgrid = np.meshgrid(*ppm_arrays)

        return self.ppm_meshgrid

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
        # define signal as the maximum intensity in the spectrum (positive or negative)
        self.signal = abs(self.data).max()
        # define an empty region as the lowest decile of the spectrum
        # FIXME: Review this definition for spectra with negative peaks
        # E.g. NOESY
        empty = self.data[self.data < np.quantile(self.data, 0.1)]
        # define the noise as the standard deviation of the empty region
        self.noise = empty.std()
        # calculate the signal to noise ratio
        self.snr = self.signal / self.noise
        return self.snr, self.signal, self.noise

    def calc_threshold(self, signal_fraction=0.01):
        """Return the threshold for the spectrum contour level based on a given
        signal fraction

        Args:
            sign (str, optional): Sign of the intensities to draw.
            signal_fraction (float, optional): Fraction of the maximum intensity as lower contour. Defaults to 0.01.

        Raises:
            ValueError: Error message if no correct sign is given.

        Returns:
            self.threshold: How many times the noise level is the lower contour above the baseline.
        """
        if self.sign == "both":
            # A good guess is the lowest contour should be 1/100 of the signal
            # Calculate the corresponding threshold
            self.threshold = (self.signal * signal_fraction) / self.noise
        elif self.sign == "positive":
            # Same but on the positive side
            self.threshold = (self.data.max() * signal_fraction) / self.noise
        elif self.sign == "negative":
            # Same but on the negative side
            self.threshold = abs(self.data.min() * signal_fraction) / self.noise
        else:
            raise ValueError(
                f"Unknown sign: {self.sign}\nPlease choose a valid sign: negative, positive or both"
            )
        return self.threshold

    def calc_clevs(self, nlevs=42, factor=1.1):
        """Calculate the contour levels for the spectrum given a series of parameters.

        Args:
            threshold (float): How many times the noise level is the lower contour above the baseline.
            nlevs (int): How many contour levels to use.
            factor (float): Increment factor between the contour levels.
            sign (string): Sign of the signals to use. Can be 'positive', 'negative' or 'both'.

        Raises:
            ValueError: If no correct sign is given, an error message is raised.
        """
        # calculate starting contour level from threshold
        start_clev = self.baseline + self.threshold * self.noise
        if self.sign == "both":
            positive_clevs = start_clev * factor ** np.arange(nlevs)
            negative_clevs = -np.flip(positive_clevs)
            self.clevs = np.concatenate((negative_clevs, positive_clevs))
            print(
                f"Highest negative/lowest positive contour levels are at {self.threshold:.1f}*noise below/above the baseline"
            )
        elif self.sign == "positive":
            self.clevs = start_clev * factor ** np.arange(nlevs)
            print(
                f"Lowest positive contour level is at {self.threshold:.1f}*noise above the baseline"
            )
        elif self.sign == "negative":
            self.clevs = -np.flip(start_clev * factor ** np.arange(nlevs))
            print(
                f"Highest negative contour level is at {self.threshold:.1f}*noise below the baseline"
            )
        else:
            raise ValueError(
                f"Unknown sign: {self.sign}\nPlease choose a valid sign: negative, positive or both"
            )

    def plot_histogram(self):
        """Plot the histogram of the spectrum"""
        bins, counts = self.calc_histogram()
        plt.hist(bins, counts)
        plt.show()

    def plot_spectrum(
        self, xlims="", ylims="", nlevs=42, factor=1.1, linewidth=1.0, cmap="viridis"
    ):
        """Plot the spectrum.
        Args:
           threshold (float, optional): Lowest contour drawn as a multiple of the spectral noise.
           xlims(tuple, optional): x axis ppm limit. Keep in mind that ppm decrease left to right.
           ylims(tuple, optional): y axis ppm limit. Keep in mind that ppm decrease left to right.
           nlevs (int, optional): Number of contour levels.
           factor (float, optional): Exponential increment between contours.
           linewidth (float, optional). Contour level linewidth
           cmap (str, optional): Colormap to be used. Options are: "viridis, "red", "blue", "green", "purple", "orange", "grey", "light_red", "light_blue". Only with sign="both":"coolwarm".
           sign (str, optional): Sign of the intensities to draw. Defaults to 'positive'.
        """

        if self.ndim == 1:
            fig, ax = plt.subplots()

            ax.plot(self.ppm_meshgrid, self.data, linewidth=linewidth)
            if xlims is False:
                ax.set_xlim(xlims)
            else:
                ax.set_xlim(*self.ppm_ranges)
            ax.set_xlabel(f"{self.label[0]} ppm")
            ax.set_ylabel("Intensity (A.U.)")
            plt.show()

        elif self.ndim == 2:
            self.calc_clevs(nlevs, factor)
            fig, ax = plt.subplots()
            # Set the limits of the color map to the calculated contour levels
            vmin = self.clevs.min()
            vmax = self.clevs.max()
            # Colormaps need to be lognormalized to fit the contour levels
            if self.sign == "both":
                cmap = cmapdict["coolwarm"]
                # We have positive and negative contours
                norm = SymLogNorm(
                    linthresh=self.threshold * self.noise, vmin=vmin, vmax=vmax, base=10
                )
                data = norm(self.data)
                clevs = norm(self.clevs)
                print(f"Plotting {nlevs} negative and {nlevs} positive contour levels")
            elif self.sign == "positive":
                norm = LogNorm(vmin=vmin, vmax=vmax)
                cmap = cmapdict[cmap]
                data = norm(self.data)
                clevs = norm(self.clevs)
                print(f"Plotting {nlevs} positive contour levels")
            elif self.sign == "negative":
                # Because contours are negative we need to make it positive to calculate
                # the norm, and apply it flipped to the data and clevs
                # FIXME: It raises a RuntimeWarning, but it works.
                # Also, it is not very efficient to make copies of the data and clevs
                norm = LogNorm(vmin=abs(vmax), vmax=abs(vmin))
                cmap = cmapdict[cmap]
                data = norm.inverse(self.data)
                clevs = norm.inverse(self.clevs)
                print(f"Plotting {nlevs} negative contour levels")
            else:
                pass
            ax.contour(
                *self.ppm_meshgrid,
                data,
                clevs,
                extent=self.ppm_ranges,
                linewidths=linewidth,
                cmap=cmap,
            )
            if xlims == "":
                ax.set_xlim(*self.ppm_ranges[:2])
            else:
                ax.set_xlim(xlims)
            if ylims == "":
                ax.set_ylim(*self.ppm_ranges[2:])
            else:
                ax.set_ylim(ylims)
            ax.set_xlabel(f"{self.label[0]} ppm")
            ax.set_ylabel(f"{self.label[1]} ppm")
            plt.show()
        else:
            print("The spectrum is not 1D or 2D")

        return fig, ax
