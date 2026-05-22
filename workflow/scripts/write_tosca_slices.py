#! /usr/bin/env python3

from pathlib import Path

import numpy as np
from euphonic import ureg
from euphonic.spectra import (
    Spectrum1D,
    Spectrum1DCollection,
    Spectrum2D,
    apply_kinematic_constraints,
)
from numpy.polynomial import Polynomial

# Instrument parameters
TOSCA_E_F = 3.97 * ureg("meV")
TOSCA_FORWARD_ANGLE = 45
TOSCA_BACKWARD_ANGLE = 135
ANGLE_PADDING = 2


def tosca_resolution(energy):
    poly_in_wavenumber = Polynomial([2.5, 0.005, 1e-7])
    return poly_in_wavenumber(energy.to("1/cm").magnitude) * ureg("1/cm")


def flatten(spectrum: Spectrum2D) -> Spectrum1D:
    """Collect non-NaN values along x-axis to average 1D spectrum from 2D"""
    flattened = Spectrum1D(
        spectrum.get_bin_edges("y"), np.nanmean(spectrum.z_data, axis=0)
    )
    flattened._y_data[np.isnan(flattened._y_data)] = 0.0
    return flattened


def combine_masked_spectra(first: Spectrum2D, second: Spectrum2D) -> Spectrum2D:
    mask = np.logical_not(np.isnan(second._z_data))
    result = first.copy()

    result._z_data[mask] = second._z_data[mask]
    return result


def main(filename: Path, prefix: Path) -> None:
    """Slice TOSCA-constrained spectra from 2-D JSON

    Args:
        filename: input JSON file
        prefix: prefix for output files
        energy_unit: energy unit for output files
    """

    spectrum = Spectrum2D.from_json_file(filename)

    constrained_spectra = {}
    projected_spectra = []

    for angle_range, bank in [
        (
            (
                TOSCA_BACKWARD_ANGLE - ANGLE_PADDING,
                TOSCA_BACKWARD_ANGLE + ANGLE_PADDING,
            ),
            "backward",
        ),
        (
            (TOSCA_FORWARD_ANGLE - ANGLE_PADDING, TOSCA_FORWARD_ANGLE + ANGLE_PADDING),
            "forward",
        ),
    ]:
        tosca_2d = apply_kinematic_constraints(
            spectrum, e_f=TOSCA_E_F, angle_range=angle_range
        )
        constrained_spectra[bank] = tosca_2d

        tosca_projected = flatten(tosca_2d)

        tosca_projected.metadata["bank"] = bank
        tosca_projected.metadata["broadened"] = "no"
        projected_spectra.append(tosca_projected)

        tosca_broadened = tosca_projected.broaden(
            tosca_resolution, shape="gauss", width_convention="STD"
        )
        tosca_broadened.metadata["broadened"] = "yes"
        projected_spectra.append(tosca_broadened)

    projected_spectra = Spectrum1DCollection.from_spectra(projected_spectra)
    projected_spectra.to_text_file(prefix.with_suffix(".projected.txt"))
    projected_spectra.to_json_file(prefix.with_suffix(".projected.json"))

    combined_2d_spectrum = combine_masked_spectra(
        constrained_spectra["forward"], constrained_spectra["backward"]
    )
    # flatten(combined_2d_spectrum).to_json_file(prefix.with_suffix(".json"))
    combined_2d_spectrum.to_json_file(prefix.with_suffix(".json"))


if __name__ == "__main__":
    main(filename=Path(snakemake.input[0]), prefix=Path(snakemake.params["prefix"]))
