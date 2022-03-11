"""Detector specifications."""
import numpy as np
from .core.logging import getLogger

log = getLogger(__name__)


class Target:
    """Target/detector specific information.

    Parameters
    ----------
    name: str
        Detector name in SNOwGLoBES (and sspike (copying SNOwGLoBES ( ;) ))).
    N_p : float
        Number of target protons.
    N_e : float
        Number of target electrons.
    snow_channels : list of  str
        Channels used in SNOwGLoBES simulations.
    basic_channels : list of str
        Channels for cross-checking sspike with SNOwGLoBES.
    nc_channels : list of str
        Neutrino-proton neutral-current interaction channels by flavor.
    """
    def __init__(self, target):
        self.name = target
        if target == 'kamland':
            # Calculate number of targets in fiducial volume of radius R_f.
            _R_f = 600  # Radial volume cut [cm].
            _rho_p = 6.66e22  # KamLAND proton density [cm^-3].
            # Number of protons in radius R_f.
            self.N_p = 4 * np.pi * _rho_p * _R_f**3 / 3
            # Number of electrons in radius R_f.
            self.N_e = self.N_p * 4.047
            # SNOwGLoBES channels.
            self.snow_channels = [
                                  'ibd',
                                  'nue_e', 'nuebar_e', 'numu_e',
                                  'numubar_e', 'nutau_e', 'nutaubar_e',
                                  'nue_C12', 'nuebar_C12', 'nc_nue_C12',
                                  'nc_nuebar_C12', 'nc_numu_C12',
                                  'nc_numubar_C12', 'nc_nutau_C12',
                                  'nc_nutaubar_C12',
                                  'nue_C13',
                                  'nc_nue_C13', 'nc_numu_C13', 'nc_nutau_C13',
                                  'nc_nuebar_C13', 'nc_numubar_C13',
                                  'nc_nutaubar_C13'
                                  ]
            # sspike channels.
            self.nc_channels = ['nc_nue_p', 'nc_nuebar_p',
                                'nc_nux_p', 'nc_nuxbar_p']
            self.basic_channels = ['ibd', 'nue_e', 'nuebar_e', 'nux_e']
