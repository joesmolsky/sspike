"""Class for model specifics."""
from os.path import isdir
from os import makedirs
import json

from astropy import units
import numpy as np
import pandas as pd

from .pnut import snow_energy
from .env import sspike_dir, models_dir, aux_dir
from ._version import __version__
from .core.logging import getLogger

log = getLogger(__name__)


class Supernova:
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
    model_dir : str
        Supernova simulation directory path.
    sim_file : str
        Path to simulation file: f"{models_dir}/{self.model}/{self.sim_path}"
    prog_dir : str
        Directory for sspike outputs varied by model, progenitor, and x-form.
    sn_dir : str
        Directory path for sspike outputs varied by distance and transform.
    bin_name : str
        Folder name for bin-dependent files: f'b{t_bins}s{t_start}e{t_end}'.
    bin_dir : str
        Directory for sspike outputs varied by binning.
    flu_name : str
        Fluence ID: f"{self.sn_name}_{self.distance}-{self.xform}_{self.bin_name}".
    tar_file : str
        File path to tarball created by snewpy: f"{models_dir}/{self.flu_name}{i}.tar.bz2".
    lum_file : str
        File path for model luminosities: f"{self.prog_dir}/luminosity.csv".
    flu_file : list of str
        File path(s) to extracted fluences: 
        f"{self.bin_dir}/{self.sn_name}-{self.bin_name}_{i}.dat".

    Notes
    -----
    All parameters are also set as attributes.
    """

    def __init__(
        self, model, progenitor, transform, distance, t_bins=1, t_start=None, t_end=None
    ):
        # Simulation properties.
        self.model = model
        self.progenitor = progenitor
        self.transform = transform
        self.xform = self._xform(transform)
        self.distance = float(distance)
        self.t_bins = t_bins
        # Model/simulation specific variables.
        self.model_dir = f"{models_dir}/{self.model}"
        self._simulation_settings()
        self.prog_dir = f"{sspike_dir}/supernova/{self.sn_name}"
        self.sn_dir = f"{self.prog_dir}/{self.distance}kpc-{self.xform}"
        # Separate directories based on time bins.
        if t_start is not None:
            self.t_start = t_start
        else:
            self.t_start = self.t_min
        if t_end is not None:
            self.t_end = t_end
        else:
            self.t_end = self.t_max
        self.bin_name = f"b{t_bins}s{self.t_start}e{self.t_end}"
        self.bin_dir = f"{self.sn_dir}/{self.bin_name}"
        if not isdir(self.bin_dir):
            makedirs(self.bin_dir)
        # Output files.
        self.flu_name = f"{self.sn_name}_{self.distance}-{self.xform}_{self.bin_name}"
        self.tar_file = f"{self.model_dir}/{self.flu_name}.tar.bz2"
        self.lum_file = f"{self.prog_dir}/luminosity.csv"

        self.flu_file = [
            f"{self.bin_dir}/fluence/{self.flu_name}_{i}.dat" for i in range(t_bins)
        ]

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
        if transform == "NoTransformation":
            xform = "NT"
        elif transform == "AdiabaticMSW_NMO":
            xform = "aMSW-N"
        elif transform == "AdiabaticMSW_IMO":
            xform = "aMSW-I"

        return xform

    def _simulation_settings(self):
        """Parse progenitor dictionary; set simulation specific variables."""
        if self.model == "Fornax_2021":
            # Fornax 2019 models only vary by mass.
            mass = float(self.progenitor["mass"])
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f"F21-{mass}"
            if mass == 26.99:
                self.sim_file = f"{self.model_dir}/lum_spec_{mass}M_r10000_dat.h5"
            else:
                self.sim_file = f"{self.model_dir}/lum_spec_{int(mass)}M_r10000_dat.h5"
            # Simulation time limits.
            f_masses = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 26.99]
            f_mins = [
                -0.2135,
                -0.2725,
                -0.2765,
                -0.2665,
                -0.2685,
                -0.2955,
                -0.2305,
                -0.2535,
                -0.3125,
                -0.3565,
                -0.3255,
                -0.3145,
                -0.3245,
                -0.3125,
                -0.3145,
            ]
            f_maxes = [
                4.4885,
                4.5955,
                4.5115,
                3.8355,
                4.4455,
                4.6645,
                4.4585,
                4.4525,
                4.6345,
                3.7615,
                4.7405,
                4.5495,
                3.1135,
                4.5955,
                4.5985,
            ]
            f_index = f_masses.index(mass)
            self.t_min = f_mins[f_index]
            self.t_max = f_maxes[f_index]

        if self.model == "Kuroda_2020":
            # Kuroda models have spin and magnetic field.
            # Allowed combinations for (Omega, B0): (00, 00), (10, 12), (10, 13).
            Omega = self.progenitor["omega"]
            B0 = self.progenitor["B0"]
            self.sn_name = f"K20-{Omega}-{B0}"
            self.sim_file = f"{self.model_dir}/LnuR{Omega}B{B0}.dat"
            # Simulation time limits.
            if B0 == "00":
                self.t_min = -0.00193548
                self.t_max = 0.476391
            if B0 == "12":
                self.t_min = -0.00065563
                self.t_max = 0.331805
            if B0 == "13":
                self.t_min = -0.00482311
                self.t_max = 0.316403

        if self.model == "Nakazato_2013":
            # Nakazato parameters: mass, metallicity, shock-revival time.
            mass = self.progenitor["mass"]
            metal = self.progenitor["metal"]
            t_rev = self.progenitor["t_rev"]
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f"N13-{mass}-{int(metal*1e3):02d}-{t_rev}"
            # Supernovae model filename.
            self.sim_file = (
                f"{self.model_dir}/nakazato-shen-z{metal}-t_rev{t_rev}ms-s{mass}.0.fits"
            )
            # Simulation time limits.
            self.t_min = -0.05
            self.t_max = 20.0

        if self.model == "Sukhbold_2015":
            # Sukhbold model has 2 masses and 2 equations of state.
            mass = self.progenitor["mass"]
            EoS = self.progenitor["eos"]
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f"S15-{mass}-{EoS}"
            # Naming convention varies with mass by 1 letter.
            if mass == 9.6:
                self.sim_file = f"{self.model_dir}/sukhbold-{EoS}-z{mass}.fits"
            if mass == 27.0:
                self.sim_file = f"{self.model_dir}/sukhbold-{EoS}-s{mass}.fits"
            # Simulation time limits.
            if mass == 9.6 and EoS == "LS220":
                self.t_min = -0.23338102
                self.t_max = 11.999932
            if mass == 9.6 and EoS == "SFHo":
                self.t_min = -0.24226689
                self.t_max = 13.622597
            if mass == 27.0 and EoS == "LS220":
                self.t_min = -0.34945536
                self.t_max = 15.439294
            if mass == 27.0 and EoS == "SFHo":
                self.t_min = -0.29291019
                self.t_max = 11.168845

        if self.model == "Tamborra_2014":
            # Tamborra model includes 2 different simulations 20.0, 27.0 S.M.
            mass = self.progenitor["mass"]
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f"T14-{mass}"
            self.sim_file = f"{self.model_dir}/s{mass}c_3D_dir1"
            # Simulation time limits.
            if mass == 20.0:
                self.t_min = 0.0065017
                self.t_max = 0.33801
            if mass == 27.0:
                self.t_min = 0.0105
                self.t_max = 0.55162

        # Walk models are 1 for each year.
        if self.model == "Walk_2018":
            self.sn_name = "W18"
            self.sim_file = f"{self.model_dir}/s15.0c_3D_nonrot_dir1"
            # Simulation time limits.
            self.t_min = 0.01
            self.t_max = 0.32939
        if self.model == "Walk_2019":
            self.sn_name = "W19"
            self.sim_file = f"{self.model_dir}/s40.0c_3DBH_dir1"
            # Simulation time limits.
            self.t_min = 0.01
            self.t_max = 0.57159

        if self.model == "Warren_2020":
            # Warren 2020 models vary by mass and stirring parameter.
            mass = float(self.progenitor["mass"])
            stir = self.progenitor["stir"]
            # Extra directory level for stirring parameter.
            self.model_dir = f"{self.model_dir}/stir_a{stir}"
            # Name for sub-directory of fluences produced by this model file.
            self.sn_name = f"W20-{mass}-{stir}"
            self.sim_file = f"{self.model_dir}/stir_multimessenger_a{stir}_m{mass}.h5"
            # Simulation time limits.
            # Warren_2020 has too many to list here.
            time_file = f"{aux_dir}/warren_times.json"
            with open(time_file, "r") as f:
                warren_times = json.load(f)
            times = warren_times[f"{stir}"][f"{mass}"]
            self.t_min = times[0]
            self.t_max = times[1]

    def bin_times(self):
        """Create arrays of start, mid, and end times.

        Returns
        -------
        (ts, tm, te) : np.array
        """
        ts = (
            np.linspace(self.t_start, self.t_end, num=self.t_bins, endpoint=False)
            * units.s
        )

        dt = (self.t_end - self.t_start) / self.t_bins * units.s
        te = ts + dt
        if te[-1].value > self.t_max:
            te[-1].value == self.t_max
        tm = (ts + te) / 2.0

        return (ts, tm, te)

    def random_df(self):
        """Dataframe of random values matching simulation energy and time bins."""
        _, times, _ = self.bin_times()
        energy = snow_energy()
        size = (len(times), len(energy))
        N_chan = pd.DataFrame(
            np.random.random(size=size), index=times.value, columns=energy
        )

        return N_chan
