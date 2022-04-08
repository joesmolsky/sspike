# sspike: simulated supernovae products inducing KamLAND events

Spike is Snoopy's brother.  `sspike` uses `snewpy` and `SNOwGLoBES` to determine supernova event rates in KamLAND.  Additionally, `sspike` includes neutrino-proton elastic-scattering.

Modules:

1. `pnut`: process neutrino underground telemetry.
2. `beer`: back-end event reader.

Class:

1. `Snowball`: supernovae model specific properties.
2. `Detector`: KamLAND specifics.

## pnut

Functions for loading and processing supernovae model fluences.

## beer

Make plots and tables of processed models.

## Snowball

Handle model specific information and data storage paths.

## Detector

Detector configuration specifics.
