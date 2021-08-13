"""Entrypoint module, in case you use `python -m nmrplot`.
"""

import click
from nmrplot import core


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("-t", "--threshold", type=float)
@click.option("-c", "--cmap", type=str, default="viridis")
@click.option("-n", "--nlevs", type=int, default=42)
@click.option("-s", "--sign", type=str, default="positive")
def main(path, threshold, cmap, nlevs, sign):
    """Plot a 1D or 2D NMR spectrum"""
    spectrum = core.Spectrum(path)
    print(f"Loaded {spectrum.ndim}D spectrum {spectrum.label}")
    spectrum.plot_spectrum(threshold=threshold, cmap=cmap, nlevs=nlevs, sign=sign)


if __name__ == "__main__":
    main()
