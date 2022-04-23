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
    det_dir : str
        Directory path for sspike outputs.
    det_bin : str
        Name of time series output directory.
    record : str
        Path to file for keeping track of processing history.

    Note
    ----
    `name` is also an attribute.
    """
    def __init__(self, name):
        self.name = name
        self.N_e = None
        self.N_p = None
        if name == 'kamland':
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
    
    def keep_vis(self, totals):
        """Final event selection from processed file totals.
        
        Parameters
        ----------
        totals : pd.DataFrame
            Results of pnut.get_totals()
        
        Returns
        -------
        vis: pd.DataFrame
            Selected results based on detector processing types.
        """
        if self.name == 'kamland':
            keep = (totals['file'] == 'smeared_weighted') |\
                   (totals['channel'] == 'nc_p_cut')
            vis = totals.where(keep).dropna().drop(columns='file')
            vis.replace('nc_p_cut', 'nc_p', inplace=True)
        else:
            keep = (totals['file'] == 'smeared_weighted')
            vis = totals.where(keep).dropna().drop(columns='file')

        return vis
