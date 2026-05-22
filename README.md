# Coherent INS simulation by numerical powder averaging

This workflow simulates spectrum for the ISIS-TOSCA neutron
spectrometer from DFT (or MLIP) force constants. It does this by
taking relevant slices from the fundamental coherent INS spectrum,
calculated as a spherical average by the Euphonic library.

This is not generally the recommended way to do it, but captures
certain dispersion effects which are neglected by the DOS-like
almost-isotropic approximations of AbINS and its predecessors.

The workflow is orchestrated using Snakemake.

- Configure system name(s) and force constants in config/sim_data.tsv. As well as
  .castep_bin files containing force constants it is possible to
  choose a phonopy.yaml file. If this doesn't contain force constants
  Euphonic will look for a corresponding FORCE_CONSTANTS or
  force_constants.hdf5 file.

- Configure sampling and plotting parameters in config/config.yml

  For test purposes the default values of q_spacing and npts are quite
  coarse. These should be cranked as low/high as you can afford to get
  a nice plot resolution in the end.

- Create a conda environment including Snakemake. (Snakemake will need
  to use Conda anyway to create the isolated/reproducible calculation
  environment.) e.g.

    conda create -c conda-forge -c bioconda -c nodefaults -n snakemake snakemake

- Activate the conda environment and install the namedtuple_table package from PyPI, i.e.

    conda activate snakemake
    pip install namedtuple_table

- Run the workflow with, e.g.

    snakemake -c 1 --sdm conda

  Note that while -c 1 will run a single job step at a time Euphonic
  will still automatically use all available cores for parallelism
  over q-points during Fourier interpolation.

  This step is significantly faster for force constants without
  long-range dipole-dipole corrections!