"""Class for model details and data storage."""

import tarfile
from os.path import isdir

import pandas as pd
from snewpy import snowglobes
from astropy import units as u

from sspike.env import models_dir, snowball_dir, snowglobes_dir, series_dir
from .core.logging import getLogger
log = getLogger(__name__)


class Snowball():
    """Simulation parameters and directory information.

    Parameters
    ----------
    model : str
        Name of supernova model type from `snewpy`.
    progenitor : dict
        Model specific simulation parameters.
    transform : str
        Name of transformation type for `snewpy` to apply.
    distance : float
        Distance to supernova in kpc.

    Attributes
    ----------
    models_dir : str
        Local `snewpy` models directory.
    snowglobes_dir : str
        Local `SNOwGLoBES` directory.
    sim_path : str
        Simulation file containing initial neutrino fluxes.
    snowball_dir : str
        sspike directory for simulation fluences and processed dataframes.
    sn_name : str
        Name indicating model type and progenitor parameters.
    tarball : str
        File path to tarball created by `snewpy`.
    fluence_dir : str
        Directory path to extracted `snewpy` tarball.
    """
    # TODO: Add time attributes to docstring.
    def __init__(self, model, progenitor, transform, distance, t_bins=1):
        # Install locations.
        # Location of snewpy models directory.
        self.models_dir = models_dir
        # SNOwGLoBES location.
        self.snowglobes_dir = snowglobes_dir
        # sspike snowball directory.
        self.snowball_dir = snowball_dir
        # sspike snowball directory.
        self.series_dir = series_dir
        # Simulation properties and fluence.
        self.model = model
        self.progenitor = progenitor
        self.transform = transform
        self.distance = distance
        self.t_bins = t_bins
        # Model/simulation specific variables.
        self._simulation_settings()
        # Integrate entire flux.
        if t_bins == 1:
            # Generate fluence if this has not been run before.
            if not isdir(f"{self.snowball_dir}{self.fluence_dir}"):
                self._gen_fluences()
            else:
                fluence_dir = f"{self.snowball_dir}{self.fluence_dir}"
                with open(f"{fluence_dir}tarball_path.txt", 'r') as f:
                    self.tarball = f.readline()
        else:
            self._gen_series()

    def _simulation_settings(self):
        """Paths to supernovae simulation file and output directory."""
        if self.model == 'Nakazato_2013':
            # Nakazato parameters: mass, metallicity, shock-revival time.
            mass = self.progenitor['mass']
            metal = self.progenitor['metal']
            t_rev = self.progenitor['t_rev']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'N13-{mass}-{int(metal*1e3):02d}-{t_rev}'
            # Supernovae model filename.
            sim_file = f'nakazato-shen-z{metal}-t_rev{t_rev}ms-s{mass}.0.fits'
            # Simulation times.
            self.t_start = -0.05
            self.t_end = 20.

        if self.model == 'Fornax_2021':
            # Fornax 2019 models only vary by mass.
            mass = self.progenitor['mass']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'F21-{mass}'
            sim_file = f'lum_spec_{mass}M_r10000_dat.h5'
            # Simulation times.
            self.t_start = -0.2135
            self.t_end = 4.4885

        if self.model == 'Warren_2020':
            # Warren 2020 models vary by mass and stirring parameter.
            mass = self.progenitor['mass']
            stir = self.progenitor['stir']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'W20-{mass}-{stir}'
            sim_file = f'stir_a{stir}/stir_multimessenger_a{stir}_m{mass}.h5'
            # Simulation times.
            self.t_start = -1.5788003
            self.t_end = 1.6835847

        if self.model == 'Tamborra_2014':
            # Tamborra model includes 2 different simulations 20.0, 27.0 S.M.
            mass = self.progenitor['mass']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'T14-{mass}'
            sim_file = f's{mass}c_3D_dir1'

        if self.model == 'Sukhbold_2015':
            # Sukhbold model has 2 masses and 2 equations of state.
            mass = self.progenitor['mass']
            EoS = self.progenitor['eos']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'S15-{mass}-{EoS}'
            # Naming convention varies with mass by 1 letter.
            if mass == 27.0:
                sim_file = f'sukhbold-{EoS}-s{mass}.fits'
            if mass == 9.6:
                sim_file = f'sukhbold-{EoS}-z{mass}.fits'

        # Walk models are 1 for each year.
        if self.model == 'Walk_2018':
            self.sn_name = 'W18'
            sim_file = 's15.0c_3D_nonrot_dir1'
        if self.model == 'Walk_2019':
            self.sn_name = 'W19'
            sim_file = 's40.0c_3DBH_dir1'

        # Kuroda models have spin and magnetic field.
        # Allowed combinations for (Omega, B0): (00, 00), (10, 12), (10, 13).
        if self.model == 'Kuroda_2020':
            Omega = self.progenitor['omega']
            B0 = self.progenitor['B0']
            self.sn_name = f'K20-{Omega}-{B0}'
            sim_file = f'LnuR{Omega}B{B0}.dat'
            # Simulation times.
            self.t_start = -0.00482311
            self.t_end = 0.316403
            
            

        self.sim_path = f'{self.models_dir}/{self.model}/{sim_file}'
        fluence_specs = f'{self.distance}kpc-{self.transform}'
        self.fluence_dir = f"{self.sn_name}/{fluence_specs}/"

    def _gen_fluences(self):
        """Generate fluence tarball with `snewpy` and extract for `sspike`."""
        # Debugging message
        flu_msg = '\n- Generating fluences:\n'
        flu_msg += f'\t- sim_path: {self.sim_path} {type(self.sim_path)}\n'
        flu_msg += f'\t- model: {self.model} {type(self.model)}\n'
        flu_msg += f'\t- transform: {self.transform} {type(self.transform)}\n'
        flu_msg += f'\t- distance: {self.distance} {type(self.distance)}\n'
        flu_msg += f'\t- sn_name: {self.sn_name} {type(self.sn_name)}\n'
        log.debug(flu_msg)

        # Generate fluence with snewpy and get path to output.
        self.tarball = snowglobes.generate_fluence(self.sim_path,
                                                   self.model,
                                                   self.transform,
                                                   self.distance,
                                                   self.sn_name)

        # Extract snewpy output in sspike snowball directory.
        fluence_path = f"{self.snowball_dir}{self.fluence_dir}"
        with tarfile.open(self.tarball) as tb:
            tb.extractall(fluence_path)
        tarball_path = f"{fluence_path}tarball_path.txt"
        # Save path name for skipping this step later.
        with open(tarball_path, 'w') as f:
            f.write(self.tarball)

    def fluences(self):
        """Read fluence file and return dataframe.

        Note
        ----
        Energy in 0.2 MeV bins and fluences are number per square centimeter.
        """
        log.debug('\n- Reading fluences.\n')
        file_dir = f'{self.snowball_dir}{self.fluence_dir}'
        file_name = f'{self.sn_name}.dat'
        fluence_file = f'{file_dir}{file_name}'
        names = ['E', 'NuE', 'NuMu', 'NuTau', 'aNuE', 'aNuMu', 'aNuTau']
        fluences = pd.read_csv(fluence_file, sep='   ', skiprows=2,
                               names=names, engine='python')

        return fluences

    def _gen_series(self):
        """Generate times tarball with `snewpy` and extract for `sspike`."""
        # Debugging message
        flu_msg = '\n- Generating time series:\n'
        flu_msg += f'\t- sim_path: {self.sim_path} {type(self.sim_path)}\n'
        flu_msg += f'\t- model: {self.model} {type(self.model)}\n'
        flu_msg += f'\t- transform: {self.transform} {type(self.transform)}\n'
        flu_msg += f'\t- distance: {self.distance} {type(self.distance)}\n'
        flu_msg += f'\t- sn_name: {self.sn_name} {type(self.sn_name)}\n'
        log.debug(flu_msg)

        # Generate fluence with snewpy and get path to output.
        self.tarball = snowglobes.generate_time_series(self.sim_path,
                                                       self.model,
                                                       self.transform,
                                                       self.distance,
                                                       self.sn_name,
                                                       self.t_bins)

        # Extract snewpy output in sspike snowball directory.
        self.series_path = f"{self.series_dir}{self.fluence_dir}"
        with tarfile.open(self.tarball) as tb:
            tb.extractall(self.series_path)
        tarball_path = f"{self.series_path}tarball_path.txt"
        # Save path name for skipping this step later.
        with open(tarball_path, 'w') as f:
            f.write(self.tarball)
