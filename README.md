# sspike: simulated supernovae products inducing KamLAND events

`sspike` uses `snewpy` and `SNOwGLoBES` to determine supernova event rates in KamLAND.  Additionally, `sspike` includes neutrino-proton elastic-scattering.

## Usage

A single simulation can be specified with command-line arguments.  Simulations an also be run by providing a file path containing a dictionary of models and progenitors.

### Single simulation

Event rates can be run integrated over the entire simulation time or processed as a series using snewpy.

#### Integrated rates

By default, fluences are integrated over the entire simulation time.

    sspike Nakazato_2013 -M 20 -Z 0.02 -R 100 -D kamland

The `Nakazato_2013` models require specifying mass, metallicity, and revival time.  More information is in the `Models` section.

#### Time series

A time series signal can be produced by specifying the number of time bins.

    sspike Nakazato_2013 -T 100 -M 20 -Z 0.02 -R 100 -D kamland

### Multiple simulation

sspike includes an option to run multiple simulations specified in a single file.  The file must have a `.` in the name.

## Supernova Models

### Nakazato_2013

Nakazato models require specifying mass, metallicity, and revival time.

#### Nakazato simulations

Mass: 13, 20, 30, 50.
Metallicity: 0.02, 0.004.
Revival time: 100, 200, 300.
Times: -0.05 - 20.0.

## Modules and classes

Modules:

1. `pnut`: process neutrino underground telemetry.
2. `beer`: back-end event reader.

Class:

1. `Snowball`: supernovae model specific properties.
2. `Detector`: KamLAND specifics.

### pnut

Functions for loading and processing supernovae model fluences.

### beer

Make plots and tables of processed models.

### Snowball

Handle model specific information and data storage paths.

### Detector

Detector configuration specifics.
