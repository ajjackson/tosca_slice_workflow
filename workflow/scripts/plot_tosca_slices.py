from euphonic.plot import plot_2d_to_axis
from euphonic.spectra import (
    Spectrum1DCollection,
    Spectrum2D,
)
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

cmap = snakemake.params["cmap"]

full = Spectrum2D.from_json_file(snakemake.input["full_spectrum"])
masked = Spectrum2D.from_json_file(snakemake.input["masked_spectrum"])
projected = Spectrum1DCollection.from_json_file(snakemake.input["projected_spectrum"])

full.y_data_unit = masked.y_data_unit = projected.x_data_unit = "1/cm"


def plot_spectra() -> None:
    subplot_kwargs = dict(
        ncols=4, sharey=True, width_ratios=[2, 2, 1, 1], figsize=(10, 3)
    )

    fig, axes = plt.subplots(**subplot_kwargs)

    if (v_max := snakemake.params.get("v_max")) is not None:
        norm = Normalize(vmin=0, vmax=v_max)
    else:
        norm = None

    plot_2d_to_axis(full, ax=axes[0], norm=norm, cmap=cmap)

    axes[0].set_title("2D powder average")
    axes[0].set_xlabel(r"$Q$ / Å")
    axes[0].set_ylabel(r"Energy transfer / cm$^{-1}$")

    plot_2d_to_axis(masked, ax=axes[1], cmap=cmap)
    axes[1].set_title("Kinematic constraints:\nTOSCA")
    axes[1].set_xlabel(r"$Q$ / Å")

    for bank in "forward", "backward":
        spectrum = projected.select(bank=bank, broadened="no").sum()
        axes[2].plot(spectrum.y_data.magnitude, spectrum.get_bin_centres(), label=bank)

        spectrum = projected.select(bank=bank, broadened="yes").sum()
        axes[3].plot(spectrum.y_data.magnitude, spectrum.get_bin_centres(), label=bank)

    # axes[2].set_xlabel(f"Intensity / {tosca_broadened.y_data.units:~P}")
    axes[2].set_title("Flatten to 1-D")

    axes[3].set_title("Instrumental\nresolution")
    fig.legend(
        handles=axes[3].lines, ncols=2, loc="upper center", bbox_to_anchor=(6 / 7, 0.15)
    )

    plt.tight_layout()
    plt.savefig(snakemake.output[0])


if __name__ == "__main__":
    plot_spectra()
