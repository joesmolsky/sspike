"""Detector specifications."""
import numpy as np
from .core.logging import getLogger

log = getLogger(__name__)


class Detector:
    """Detector specific information.

    Parameters
    ----------
    name: str
        Detector name in SNOwGLoBES (and sspike (copying SNOwGLoBES ( ;) ))).

    Attributes
    ----------
    N_p : float
        Number of target protons for 'kamland' or None.
    N_e : float
        Number of target electrons for 'kamland' or None.
    low_cut : float
        Low energy threshold [GeV].

    Note
    ----
    `name` is also an attribute.
    """
    def __init__(self, detector):
        self.name = detector
        self.N_e = None
        self.N_p = None
        if detector == 'kamland':
            # Calculate number of targets in fiducial volume of radius R_f.
            _R_f = 600  # Radial volume cut [cm].
            _rho_p = 6.66e22  # KamLAND proton density [cm^-3].
            # Number of protons in radius R_f.
            self.N_p = 4 * np.pi * _rho_p * _R_f**3 / 3
            # Number of electrons in radius R_f.
            self.N_e = self.N_p * 4.047
            # Low energy threshold for KamLAND [GeV].
            self.low_cut = 2e-4
            # File types to include in pnut.event_totals.
            self.total_files = ['snow-unsmeared_weighted.csv', 
                                'snow-smeared_weighted.csv',
                                'sspike-basic.csv', 
                                'sspike-elastic.csv']
    