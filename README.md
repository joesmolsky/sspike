[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# sspike: simulating supernovae products inducing KamLAND events

`sspike` uses `snewpy` and `SNOwGLoBES` to determine supernova event rates in KamLAND (or other detectors).  Additionally, `sspike` includes neutrino-proton elastic-scattering and additional functions for comparing models in a single detector.

## Installation

`SNOwGLoBES` and `snewpy` must both be installed first.  Additional requirements are in `requirements.txt`, but I may have forgotten some.  `sspike` should be installable by cloning the repository using `pip install .` or `pip install -e .` in main folder.  Feel free to email, Slack, or raise an issue if you are actually trying to use `sspike` and want some help.

`SNOwGLoBES`: <https://webhome.phy.duke.edu/~schol/snowglobes/>
`snewpy`: <https://github.com/SNEWS2/snewpy>

## Basic usage

Integrated event totals for a single simulation can be run from the command line.  Here is an example:

    sspike Fornax_2021 -D kamland -L 10 -M 13

The model name can be replaced by a `.json` file path containing multiple models and progenitors.  More usage information can be found using `sspike -h`, checking the documentation, or in `example.ipynb`.  

## Time series

Simulation start time, end time, and the number of time bins can all be set.  This cannot yet be done from the command line, but can be done as demonstrated in `time_series.ipynb`

## Documentation

Please see `non-existent link` for documentation, example plots for each model, and model comparison examples.
