sspike
======

sspike uses 2 classes and 1-3 modules to explore supernova event rates.

Classes
-------

The classes are implemented to simplify syntax differences between models and handling of processed data.

Supernova
^^^^^^^^^

The `Supernova` class is for information relevant to neutrino flux arriving at earth.  It requires 4 arguments:

1. `model`: name of model from `snewpy`.
2. `progenitor`: specifies which simulation to use for given `model`.
3. `transformation`: transformation type from `snewpy`. (Only tested for `NoTransformation` so far.)
4. `distance`: distance to supernova in kpc.

Detector
^^^^^^^^

The `Detector` class only takes the detector name as an argument.  The detector must be available in `SNOwGLoBES` and `snewpy`.  Detectors other than `kamland` are all handled the same.  For `kamland`, additional information is included for proton-neutrino elastic-scattering (and bench-marking).

Modules
-------

The modules are split into (primarily) processing and (primarily) plotting.

pnut
^^^^

Process neutrino underground telemetry.  Functions to load SN models and process event rates.

beer
^^^^

Back-end event reader.  Make plots and tables of pnut outputs.

comp
^^^^

Compare SN models... in progress.
