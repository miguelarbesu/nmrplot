# nmrplot

![License](https://img.shields.io/github/license/miguelarbesu/nmrplot)

![CI](https://github.com/miguelarbesu/nmrplot/actions/workflows/CI.yaml/badge.svg)
![Linting](https://github.com/miguelarbesu/nmrplot/actions/workflows/linting.yaml/badge.svg)
![Doc](https://github.com/miguelarbesu/nmrplot/actions/workflows/doc.yaml/badge.svg)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


---

A Python tool for plotting NMR spectra using [`nmrglue`](https://nmrglue.readthedocs.io/en/latest/).

Full documentation at [this website](https://miguelarbesu.github.io/nmrplot/).

## Installation & requirements


- You can use `pip` to directly install from this repository:
```bash
python -m pip install git+https://github.com/miguelarbesu/nmrplot
```
or
- Download (and uncompress), clone, or fork this repository in your computer.
- Open a command line terminal and go into the repository folder.
- Run `python setup.py install` or `python -m pip install -e .` for an editable installation (see [the developers README](devtools/README-dev.md)).

`nmrplot` requires Python >=3.6.

## Basic usage

You can call `nmrplot` for basic plotting 1D or 2D spectra from the command line:

```bash
nmrplot [OPTIONS] PATH
```
where PATH is the path to a particular Bruker NMR experiment number. Use the `--help` flag to see the possible options.

## Advanced usage

You import `nmrplot.core` as a module and it to compose complex figures using
`matplotlib` in Python scripts or jupyter notebooks.

The `core.Spectrum` class is a wrapper for `nmrglue` functions to create a simplified
object that holds data and spectral parameters for easy access.

## Copyright

Copyright (c) 2021, Miguel Arbesú

## Acknowledgements

This module is a wrapper around  [`nmrglue`](https://nmrglue.readthedocs.io/en/latest/). If you use `nmrplot`, you must acknowledge
([and cite](https://link.springer.com/article/10.1007/s10858-013-9718-x)) `nmrglue` too.
 
Project based on the [Reproducible Science Cookiecutter](https://github.com/miguelarbesu/cookiecutter-reproducible-science).

