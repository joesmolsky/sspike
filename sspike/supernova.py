"""Class for model specifics."""
from os.path import isdir
from os import makedirs

from .env import sspike_dir
from .core.logging import getLogger
log = getLogger(__name__)


class Supernova():
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
    t_bins : int, default 1
        Number of time bins.
    t_start : float, optional
        Start time for simulation if not earliest model time.
    t_end : float, optional
        End time for simulation if not latest model time.

    Attributes
    ----------
    sn_name : str
        Name indicating model type and progenitor parameters.
    xform : str
        Transformation abbreviation for folders and plots.
    t_min : float
        Model specific simulation start time.
    t_max : float
        Model specific simulation end time.
    sim_file : str
        Supernova simulation file name for snewpy model.
    sn_dir : str
        Directory path for sspike outputs.

    Note
    ----
    All parameters are also set as attributes.
    """
    def __init__(self, model, progenitor, transform, distance,
                 t_bins=1, t_start=None, t_end=None):
        # Simulation properties.
        self.model = model
        self.progenitor = progenitor
        self.transform = transform
        self.xform = self._xform(transform)
        self.distance = distance
        self.t_bins = t_bins
        if t_start and t_end:
            self.t_start = t_start
            self.t_end = t_end
        # Model/simulation specific variables.
        self._simulation_settings()
        self.sn_dir = f'{sspike_dir}/{self.sn_name}/{distance}kpc-{self.xform}'
        if not isdir(self.sn_dir):
            makedirs(self.sn_dir)

    def _xform(self, transform):
        """Transformation abbreviation for directories and plots.
        
        Parameter
        ---------
        transform : str
            Name of transformation type from snewpy.

        Return
        ------
        xform : str
            Abbreviation of transformation type.
        """
        if transform == 'NoTransformation':
            xform = 'NT'

        return xform

    def _simulation_settings(self):
        """Parse progenitor dictionary; set simulation specific variables."""
        if self.model == 'Fornax_2021':
            # Fornax 2019 models only vary by mass.
            mass = self.progenitor['mass']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'F21-{mass}'
            self.sim_file = f'lum_spec_{mass}M_r10000_dat.h5'
            # Simulation time limits.
            self.t_min = -0.2135
            self.t_max = 4.4885

        if self.model == 'Kuroda_2020':
            # Kuroda models have spin and magnetic field.
            # Allowed combinations for (Omega, B0): (00, 00), (10, 12), (10, 13).
            Omega = self.progenitor['omega']
            B0 = self.progenitor['B0']
            self.sn_name = f'K20-{Omega}-{B0}'
            self.sim_file = f'LnuR{Omega}B{B0}.dat'
            # Simulation time limits.
            self.t_min = -0.00482311
            self.t_max = 0.316403

        if self.model == 'Nakazato_2013':
            # Nakazato parameters: mass, metallicity, shock-revival time.
            mass = self.progenitor['mass']
            metal = self.progenitor['metal']
            t_rev = self.progenitor['t_rev']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'N13-{mass}-{int(metal*1e3):02d}-{t_rev}'
            # Supernovae model filename.
            self.sim_file = f'nakazato-shen-'\
                            f'z{metal}-t_rev{t_rev}ms-s{mass}.0.fits'
            # Simulation time limits.
            self.t_min = -0.05
            self.t_max = 20.
            
        if self.model == 'Sukhbold_2015':
            # Sukhbold model has 2 masses and 2 equations of state.
            mass = self.progenitor['mass']
            EoS = self.progenitor['eos']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'S15-{mass}-{EoS}'
            # Naming convention varies with mass by 1 letter.
            if mass == 27.0:
                self.sim_file = f'sukhbold-{EoS}-s{mass}.fits'
            if mass == 9.6:
                self.sim_file = f'sukhbold-{EoS}-z{mass}.fits'

        if self.model == 'Tamborra_2014':
            # Tamborra model includes 2 different simulations 20.0, 27.0 S.M.
            mass = self.progenitor['mass']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'T14-{mass}'
            self.sim_file = f's{mass}c_3D_dir1'

        # Walk models are 1 for each year.
        if self.model == 'Walk_2018':
            self.sn_name = 'W18'
            self.sim_file = 's15.0c_3D_nonrot_dir1'
        if self.model == 'Walk_2019':
            self.sn_name = 'W19'
            self.sim_file = 's40.0c_3DBH_dir1'

        if self.model == 'Warren_2020':
            # Warren 2020 models vary by mass and stirring parameter.
            mass = self.progenitor['mass']
            stir = self.progenitor['stir']
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f'W20-{mass}-{stir}'
            self.sim_file = f'stir_a{stir}/'\
                            f'stir_multimessenger_a{stir}_m{mass}.h5'
            # Simulation time limits.
            self.t_min = -1.5788003
            self.t_max = 1.6835847
      