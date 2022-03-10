"""Detector specifications."""
import numpy as np
from .core.logging import getLogger

log = getLogger(__name__)


class Target:
    """KamLAND specific information."""
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
