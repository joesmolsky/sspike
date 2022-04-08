"""Process neutrino underground telemetry.

Functions to load SN models from and process event rates.
"""

import pandas as pd
import numpy as np
import scipy.constants as cns
from scipy.integrate import quad

from snewpy import snowglobes

from .core.logging import getLogger
log = getLogger(__name__)

# Physics constants.
# Proton mass in GeV.
M_p = cns.physical_constants['proton mass energy equivalent in MeV'][0] * 1e-3
Gf = cns.physical_constants['Fermi coupling constant'][0]  # GeV^-2
hbcu = cns.physical_constants['reduced Planck constant times c in MeV fm']
hbarc = hbcu[0] * 1e-13 * 1e-3  # Convert fm to cm and MeV to GeV
Cv = 0.04  # Vector coupling constant
Ca = 1.27 / 2  # Axial coupling constant

# Path to SNOeGLoBES cross-section files
xs_ibd = '/Users/joe/src/snowglobes/xscns/xs_ibd.dat'
xs_e = '/Users/joe/src/snowglobes/xscns/xs_nue_e.dat'


def snowglobes_events(snowball, detector, series=False):
    """Process fluences with SNOwGLoBES via `snewpy`.

    Parameters
    ----------
    snowball : Snowball
        Simulation details.
    detector : str
        Name of SNOwGLoBES detector.

    Returns
    -------
    snowflakes : list of str
        File path to processed dataframe.
    """
    log.debug('- Generating SNOwGLoBES events.')
    sb = snowball
    # Simulate via snewpy and make a table of the results.
    snow = snowglobes.simulate(sb.snowglobes_dir,
                               sb.tarball,
                               detector_input=detector.name)
    # return snow[detector.name][sb.sn_name]

    # Save results
    # Interesting rates are unsmeared_weighted and smeared_weighted.
    smearing = ['unsmeared', 'smeared']
    # Store filepaths for each smearing option.
    snowflakes = []
    for smear in smearing:
        snowflake = f"{sb.snowball_dir}{sb.fluence_dir}snow-{smear}.csv"
        events = snow[detector.name][sb.sn_name]['weighted', smear]
        events.to_csv(path_or_buf=snowflake, sep=' ')
        snowflakes.append(snowflake)

    return snowflakes


def sspike_events(snowball, detector):
    """Process event rates using sspike functions.

    Parameters
    ----------
    snowball : Snowball
        Simulation details.
    detector : list of str
        Name of SNOwGLoBES detector.

    Returns
    -------
    sspikes : list(str)
        File paths to processed dataframe.
    """
    sspikes = []
    sspikes.append(basic_events(snowball, detector))
    sspikes.append(elastic_events(snowball, detector))

    return sspikes


def basic_events(snowball, detector):
    """Estimate ibd and electron scatter events for cross-checking.

    Parameters
    ----------
    snowball : Snowball
        Simulation details.
    detector : list of str
        Name of SNOwGLoBES detector.

    Returns
    -------
    sspiked : str
        File path to processed dataframe.
    """
    sb = snowball
    # Location to save dataframe.
    basic_path = f"{sb.snowball_dir}{sb.fluence_dir}sspike-basic.csv"
    # Dataframes of event rates by detector type.
    ibd = ibd_events(snowball, detector)
    e_nu = e_scat(snowball, detector)

    events = pd.merge(ibd, e_nu, on='E')
    events.to_csv(path_or_buf=basic_path, sep=' ')

    return basic_path


def ibd_events(snowball, detector):
    """Inverse beta decay events.

    Parameters
    ----------
    snowball : Snowball
        Simulation details.
    detector : list of str
        Name of SNOwGLoBES detector.

    Returns
    -------
    sspiked : dataframe
        Pandas dataframe with electron events by flavor.
    """
    # Load fluences.
    fluences = snowball.fluences()

    # Load cross-sections
    xscn = np.genfromtxt(xs_ibd, skip_header=3).T
    # Energies [log(E GeV)] --> [GeV]
    x_E = 10**xscn[0]
    # Cross-sections [10^-38 cm^-2 GeV^-1] --> [cm^-2 GeV^-1]
    x_scale = 1e-38
    x_nueb = xscn[4] * x_scale

    # Number of events: fluence * xscn * bin-size * N_electrons.
    # Energy bins of 0.2 MeV in GeV.
    events = pd.DataFrame()
    # Use the same energy grid as SNOwGLoBES
    events['E'] = np.linspace(7.49e-4, 9.975e-2, 200)
    bin_size = events['E'][1] - events['E'][0]
    bin_scale = bin_size / 0.0002
    f_nueb = np.interp(events['E'], fluences['E'], fluences['aNuE'])
    xs_nueb = np.interp(events['E'], x_E, x_nueb)
    events['ibd'] = f_nueb * xs_nueb * events['E'] * detector.N_p * bin_scale

    return events


def e_scat(snowball, detector):
    """Electron-neutrino scattering events.

    Parameters
    ----------
    snowball : Snowball
        Simulation details.
    detector : list of str
        Name of SNOwGLoBES detector.

    Returns
    -------
    sspiked : dataframe
        Pandas dataframe with electron events by flavor.
    """
    fluences = snowball.fluences()
    # Load cross-sections.
    xscn = np.genfromtxt(xs_e, skip_header=3).T
    # Energies [log(E GeV)] --> [GeV].
    x_E = 10**xscn[0]
    # Cross-sections [10^-38 cm^-2 GeV^-1] --> [cm^-2 GeV^-1].
    x_scale = 1e-38
    x_nue = xscn[1] * x_scale
    x_nueb = xscn[4] * x_scale
    x_nux = xscn[2] * x_scale

    # Number of events: fluence * xscn * N_electrons.
    # Multiply cross-sections from file (in GLoBES formatting) by energy.
    events = pd.DataFrame()
    # Use the same energy grid as SNOwGLoBES.
    events['E'] = np.linspace(7.49e-4, 9.975e-2, 200)
    bin_size = events['E'][1] - events['E'][0]
    bin_scale = bin_size / 0.0002

    # Electron flavor neutrinos.
    f_nue = np.interp(events['E'], fluences['E'], fluences['NuE'])
    xs_nue = np.interp(events['E'], x_E, x_nue)
    events['nue_e'] = f_nue * xs_nue * events['E'] * detector.N_e * bin_scale
    # Positron flavor neutrinos.
    f_nueb = np.interp(events['E'], fluences['E'], fluences['aNuE'])
    xs_nueb = np.interp(events['E'], x_E, x_nueb)
    events['nuebar_e'] = f_nueb * xs_nueb * events['E']\
                                * detector.N_e * bin_scale
    # Extra factor of 4: nux = nu_mu + nu_mubar + nu_tau + nu_taubar.
    f_nux = np.interp(events['E'], fluences['E'], fluences['NuMu']) * 4
    xs_nux = np.interp(events['E'], x_E, x_nux)
    events['nux_e'] = f_nux * xs_nux * events['E'] * detector.N_e * bin_scale

    return events


def elastic_events(snowball, detector):
    """Proton-neutrino elastic scattering events.

    Parameters
    ----------
    snowball : Snowball
        Simulation details.
    detector : list of str
        Name of SNOwGLoBES detector.

    Returns
    -------
    sspiked : dataframe
        Pandas dataframe with neutral-current events by flavor.
    """
    sb = snowball
    fluences = sb.fluences()
    # Find differential cross-section as function of proton recoil energy.
    nc = pd.DataFrame()
    # Maximum proton recoil energy for 100 MeV neutrino is 17.5 MeV.
    nc['T_p'] = np.arange(1e-4, 0.0176, 1e-4)
    nc['E_vis'] = quench(nc['T_p'])
    # Kinematic threshold.
    nc['E_min'] = (nc['T_p'] + np.sqrt(nc['T_p'] * (nc['T_p'] + 2 * M_p))) / 2

    N_bins = len(nc['T_p'])
    nc['nc_nue_p'] = np.zeros(N_bins)
    nc['nc_nuebar_p'] = np.zeros(N_bins)
    nc['nc_nux_p'] = np.zeros(N_bins)
    nc['nc_nuxbar_p'] = np.zeros(N_bins)

    # Event rates.
    # Change from fluence bin width of 0.2 MeV.
    bin_scale = (nc['T_p'][1] - nc['T_p'][0]) / 2e-4
    for i in range(N_bins):
        nc['nc_nue_p'][i] = detector.N_p * quad(lambda x:
                                              dxs_nc(x, nc['T_p'][i])
                                              * np.interp(x, fluences['E'],
                                                          fluences['NuE']),
                                              nc['E_min'][i], 0.1)[0]\
                                       * bin_scale
        nc['nc_nuebar_p'][i] = detector.N_p * quad(lambda x:
                                                 dxs_nc(x, nc['T_p'][i])
                                                 * np.interp(x, fluences['E'],
                                                             fluences['aNuE']),
                                                 nc['E_min'][i], 0.1)[0]\
                                          * bin_scale
        nc['nc_nux_p'][i] = detector.N_p * quad(lambda x: dxs_nc(x, nc['T_p'][i])
                                              * np.interp(x, fluences['E'],
                                                          fluences['NuMu']),
                                              nc['E_min'][i], 0.1)[0]\
                                       * bin_scale
        nc['nc_nuxbar_p'][i] = detector.N_p * quad(lambda x:
                                                 dxs_nc(x, nc['T_p'][i])
                                                 * np.interp(
                                                    x, fluences['E'],
                                                    fluences['aNuMu']),
                                                 nc['E_min'][i], 0.1)[0]\
                                          * bin_scale

    nc_path = f"{sb.snowball_dir}{sb.fluence_dir}sspike-nc.csv"
    nc.to_csv(path_or_buf=nc_path, sep=' ')

    return nc_path


def dxs_nc(E, T_p, a=1):
    """Neutral-current double differential cross-section.

    Parameters
    ----------
    E : float
        Neutrino energy in GeV.
    T_p : float
        Proton recoil energy in GeV.

    Returns
    -------
    dsig : float
        Differential cross-section in with respect to proton recoil energy
        with units of cm^2 / GeV.
    """
    if E == 0 or T_p == 0:
        return 0

    # Cross-section has three terms with a shared coefficient.
    A = (Gf * hbarc)**2 * M_p / 2 / np.pi / E**2  # [GeV^-3 cm^2]
    nu2 = (Cv + a * Ca)**2 * E**2  # [GeV^2]
    p2 = (Cv**2 - Ca**2) * M_p * T_p  # [GeV^2]
    pnu = (Cv - a * Ca)**2 * (E - T_p)**2  # [GeV^2]

    dsig = A * (nu2 + pnu - p2)  # [cm^2 GeV^-1]

    return dsig


def quench(T_p):
    """
    Convert proton recoil energy to electron equivalent energy.

    Parameters
    ----------
    T_p : np.array
        Proton recoil energies of interest $[MeV]$.

    Return
    ------
    E : np.array
        Electron equivalent energy in KamLAND.

    Note:
        Quenching factors using WebPlotDigitizer on Fig. 6 in:
        https://www.sciencedirect.com/science/article/pii/S0168900210017018
    """
    quenching = '/Users/joe/src/gitjoe/sspike/sspike/aux/proton_quenching.csv'
    qE, qX = np.genfromtxt(quenching, delimiter=',').T
    E = T_p * np.interp(T_p, qE, qX)

    return E
