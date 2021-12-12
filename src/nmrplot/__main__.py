"""Entrypoint module, in case you use `python -m nmrplot`.
"""

import click
from nmrplot import core


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "-p",
    "--pdata",
    type=str,
    default=1,
    help="Number of processing in the Bruker experiment",
)
@click.option(
    "-t",
    "--threshold",
    type=float,
    help="How many times the noise level is the lowest contour above the baseline",
)
@click.option(
    "-c",
    "--cmap",
    type=str,
    default="viridis",
    help="The colormap to use. Options are: viridis, red, blue, green, purple, orange, grey, light_red, light_blue. Only with sign=both: coolwarm",
)
@click.option(
    "-n", "--nlevs", type=int, default=42, help="Number of contour levels to draw"
)
@click.option(
    "-f",
    "--factor",
    type=float,
    default=1.1,
    help="Increment factor between contour levels",
)
@click.option(
    "-s",
    "--sign",
    type=str,
    default="positive",
    help="Whether to draw positive, negative or both contours. Options are: positive, negative, both",
)
def main(path, pdata, threshold, cmap, nlevs, sign, factor):
    """Plot a 1D or 2D Bruker NMR spectrum in a given path"""
    spectrum = core.Spectrum(path, pdata)
    spectrum.sign = sign
    if threshold:
        spectrum.threshold = threshold
    print(f"Loaded {spectrum.ndim}D spectrum {spectrum.label}")
    spectrum.plot_spectrum(cmap=cmap, nlevs=nlevs, factor=factor)


if __name__ == "__main__":
    main()
