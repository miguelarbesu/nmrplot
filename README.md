# nmrplot

![CI](https://github.com/miguelarbesu/nmrplot/actions/workflows/CI.yaml/badge.svg)
![Linting](https://github.com/miguelarbesu/nmrplot/actions/workflows/linting.yaml/badge.svg)
![Doc](https://github.com/miguelarbesu/nmrplot/actions/workflows/doc.yaml/badge.svg)


[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![License](https://img.shields.io/github/license/miguelarbesu/nmrplot)

---

A Python tool for plotting NMR spectra using [`nmrglue`](https://nmrglue.readthedocs.io/en/latest/).

Full documentation at [this website](https://miguelarbesu.github.io/nmrplot/).

## Installation

- Download (and uncompress), clone, or fork this repository in your computer.
- Open a command line terminal and go into the repository folder.
- Run `python setup.py install`.

If you would like to have an editable installation for development, see [the developers README](devtools/README-dev.md).

## Basic usage

You can call `nmrplot` for basic plotting 1D or 2D spectra from the command line:

```bash
python -m nmrplot [OPTIONS] PATH
```

where PATH is the path to a particular Bruker NMR experiment number. Use the `--help` flag to see the possible options.

*Note*: If you do not see any contour level in a 2D spectrum, pass `-t 0.1` or lower as
an option. The threshold is by default t=1.0 times the noise in the spectrum, defined as
its [variance](https://en.wikipedia.org/wiki/Signal-to-noise_ratio).

## Advanced usage

You import `nmrplot` as a module and it to compose complex figures using `matplotlib` in Python scripts or jupyter notebooks.

The `core.Spectrum` class is a wrapper for `nmrglue` functions to create a simplified
object that holds data and spectral parameters for easy access.

## Copyright

Copyright (c) 2021, Miguel Arbesú

## Acknowledgements

This module is a wrapper around `nmrglue`. If you use `nmrplot`, you must acknowledge
`nmrglue` too.
 
Project based on the [Reproducible Science Cookiecutter](https://github.com/miguelarbesu/cookiecutter-reproducible-science).

