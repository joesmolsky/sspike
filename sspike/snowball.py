"""Class for model details and data storage."""

import tarfile

from snewpy import snowglobes

from .core.logging import getLogger
log = getLogger(__name__)


class Snowball():
    """Simulation parameters and directory information.

    Parameters
    ----------
    model : str
        Name of supernova model type from snewpy.
    progenitor : dict
        Model specific simulation parameters.
    transform : str
        Name of transformation type for snewpy to apply.
    distance : float
        Distance to supernova in kpc.

    Attributes
    ----------
    models_dir : str
        Local snewpy models directory.
    snowglobes_dir : str
        Local SNOwGLoBES directory.
    snowball_dir : str
        sspike directory for simulation fluences and processed dataframes.
    sim_path : str
        Simulation file containing initial neutrino fluxes.
    sn_name : str
        Name indicating model type and progenitor parameters.
    tarball : str
        File path to tarball created by snewpy.
    fluence : str
        File path to extracted snewpy tarball.
    """
    def __init__(self, model, progenitor, transform, distance):
        # Install locations.
        # Location of snewpy models directory.
        self.models_dir = '/Users/joe/src/snewpy/models/'
        # SNOwGLoBES location.
        self.snowglobes_dir = "/Users/joe/src/gitjoe/snowglobes/"
        # sspike snowball directory.
        self.snowball_dir = "/Users/joe/src/gitjoe/sspike/snowballs/"
        # Simulation properties and fluence.
        self.model = model
        self.progenitor = progenitor
        self.transform = transform
        self.distance = distance
        # Model/simulation specific variables.
        self._simulation_settings()
        # Transformed terrestrial fluence.
        self._gen_fluence()

    def _simulation_settings(self):
        """Paths to supernovae simulation file and output directory."""
        if self.model == 'Nakazato_2013':
            # Simulation properties
            try:
                mass = self.progenitor['mass']
                metal = self.progenitor['metal']
                t_rev = self.progenitor['t_rev']
            except Exception:
                log.error('ERROR: given properties do not match model.\n')
                log.error(Exception)
                exit()
            # Supernovae model filename.
            sim_file = f'nakazato-shen-z{metal}-t_rev{t_rev}ms-s{mass}.0.fits'
            self.sn_name = f'{self.model[:3]}-{mass}-{int(metal*1e3)}-{t_rev}'

        self.sim_path = f'{self.models_dir}/{self.model}/{sim_file}'
        fluence_specs = f'{self.distance}kpc-{self.transform}'
        self.fluence_dir = f"{self.sn_name}/{fluence_specs}/"

    def _gen_fluence(self):
        """Generate fluence tarball with snewpy and extract for sspike."""
        # Generate fluence with snewpy and get path to output.
        self.tarball = snowglobes.generate_fluence(self.sim_path,
                                                   self.model,
                                                   self.transform,
                                                   self.distance,
                                                   self.sn_name)
        # Extract snewpy output in sspike snowball directory.
        with tarfile.open(self.tarball) as tb:
            tb.extractall(f"{self.snowball_dir}{self.fluence_dir}")
