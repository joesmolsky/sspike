"""Predict neutrino underground telemetry.

Functions to load SN models and process event rates.
"""
from os.path import isdir, isfile
from os import makedirs, listdir, rename
import tarfile

import pandas as pd
import numpy as np
import scipy.constants as cns
from scipy.integrate import quad

import snewpy.models.ccsn
from snewpy.neutrino import Flavor
from snewpy import snowglobes

from .env import models_dir, snowglobes_dir
from .core.logging import getLogger

log = getLogger(__name__)

# Physics constants.
# Proton mass in GeV.
M_p = cns.physical_constants["proton mass energy equivalent in MeV"][0] * 1e-3
Gf = cns.physical_constants["Fermi coupling constant"][0]  # GeV^-2
hbcu = cns.physical_constants["reduced Planck constant times c in MeV fm"]
hbarc = hbcu[0] * 1e-13 * 1e-3  # Convert fm to cm and MeV to GeV
Cv = 0.04  # Vector coupling constant
Ca = 1.27 / 2  # Axial coupling constant

# Path to SNOwGLoBES cross-section files used for cross-checking sspike.
xs_ibd = "/Users/joe/src/snowglobes/xscns/xs_ibd.dat"
xs_e = "/Users/joe/src/snowglobes/xscns/xs_nue_e.dat"


def get_luminosities(sn, save=True):
    """Save luminosity vs. time for each flavor in dataframe format.

    Parameters
    ----------
    sn : sspike.Supernova
        Supernova simulation specifics.

    Return
    ------
    df : pd.DataFrame
        Simulation times [s] and flavor luminosities [erg / s].
    """
    if isfile(sn.lum_file):
        df = pd.read_csv(sn.lum_file, sep=" ")

        return df

    # Initialize model using snewpy.
    model_type = getattr(snewpy.models.ccsn, sn.model)
    sn_sim = model_type(sn.sim_file)

    # Luminosity vs. time dataframe.
    df = pd.DataFrame()
    df["time"] = sn_sim.time.value

    if sn.xform == "NT":
        for flavor in Flavor:
            df[flavor.name] = sn_sim.luminosity[flavor].value
    else:
        msg = "Error: transformed luminosities not yet available in sspike! :("
        log.error(msg)
        return msg

    if save:
        df.to_csv(sn.lum_file, sep=" ", index=False)

    return df


def get_fluences(sn, index=0):
    """Get fluences generated by snewpy and update record.

    Parameters
    ----------
    sn : sspike.Supernova
        Supernova specifics.
    i : int
        Index of fluences file list.

    Return
    ------
    df : pd.Dataframe
        Energy [GeV] and fluence by flavor [cm^-2].
    """
    if not isfile(sn.tar_file):
        fluence_tarball(sn)

    names = ["E", "NuE", "NuMu", "NuTau", "aNuE", "aNuMu", "aNuTau"]
    df = pd.read_csv(
        sn.flu_file[index], sep="   ", skiprows=2, names=names, engine="python"
    )

    return df


def fluence_tarball(sn, t_start=None, t_end=None):
    """Generate fluences tarball via snewpy and extract in sn.bin_dir.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifics
    ts : astropy.Quantity or None
        Bin start times.
    te : astropy.Quantity or None
        Bin end times.

    Notes
    -----
    Runs snewpy and extracts returned tarball into fluence output directory.
    """
    log.info(f"\nGenerating fluences for {sn.sn_name} in {sn.sn_dir}.\n")
    log.debug(f"\nt_start: {t_start}\nt_end: {t_end}\n")

    # Generate tarball with snewpy.
    tarball = snowglobes.generate_fluence(
        sn.sim_file,
        sn.model,
        sn.transform,
        sn.distance,
        output_filename=f"{sn.flu_name}",
        tstart=t_start,
        tend=t_end,
    )

    # Extract snewpy output in sspike snowball directory.
    with tarfile.open(tarball) as tb:
        flu_dir = f"{sn.bin_dir}/fluence/"
        if not isdir(flu_dir):
            makedirs(flu_dir)
        tb.extractall(flu_dir)

        # snewpy does not include an index in single bin file names (but sspike does).
        if sn.t_bins == 1:
            new_path = sn.flu_file[0]
            snewpy_path = new_path[:-6] + new_path[-4:]
            rename(snewpy_path, new_path)


def snowglobes_events(sn, detector, index=0, save=True):
    """Process fluences with SNOwGLoBES via `snewpy`.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation details.
    detector : sspike.Detector
        Detector for simulations.

    Returns
    -------
    dfs : dict of pd.Dataframe
        Events for each type of SNOwGLoBES data.
    """
    log.debug("- Generating SNOwGLoBES events.")

    if not isfile(sn.tar_file):
        fluence_tarball(sn)

    dfs = {}
    snow_dir = f"{detector.get_save_dir(sn)}/snow-files"

    if isdir(snow_dir):
        for file in listdir(snow_dir):
            key = file.split("snow-")[1][:-4]
            dfs[key] = pd.read_csv(f"{snow_dir}/{file}", sep=" ")

        return dfs

    makedirs(snow_dir)

    # Simulate via snewpy.
    snowglobes.simulate(snowglobes_dir, sn.tar_file, detector_input=detector.name)
    snow_sim = snowglobes.collate(snowglobes_dir, sn.tar_file, skip_plots=True)

    # First key is detector.  The rest indicate smearing and weighting.
    keys = list(snow_sim.keys())[1:]
    header = snow_sim[keys[0]]["header"].split(" ")

    # Save event dataframes by smearing and weighting.
    for key in keys:
        data = snow_sim[key]["data"].T
        df = pd.DataFrame(data, columns=header)
        df_key = key.split("_events_")[1][:-4]
        dfs[df_key] = df

        if save:
            snow_file = f"{snow_dir}/snow-{df_key}_{index}.csv"
            df.to_csv(snow_file, sep=" ", index=False)

    return dfs


def sspike_events(sn, detector, index=0, save=True):
    """Process event rates using sspike functions.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation details.
    detector : sspike.detector
        Detector for simulations.

    Returns
    -------
    dfs : dict of pd.Dataframe
        Event rates for sspike data types.
    """
    log.debug("- Generating sspike events.")

    if not isfile(sn.tar_file):
        fluence_tarball(sn)

    dfs = {}

    sspike_dir = f"{detector.get_save_dir(sn)}/sspike-files"

    if isdir(sspike_dir):
        for file in listdir(sspike_dir):
            key = file.split("sspike-")[-1][:-4]
            dfs[key] = pd.read_csv(f"{sspike_dir}/{file}", sep=" ")

        return dfs

    makedirs(sspike_dir)

    for name in detector.sspike_functions:
        try:
            key = name.split("_")[0]
        except Exception:
            key = name
        dfs[key] = eval(name + f"(sn, detector, {index})")

    if save:
        for file in dfs:
            path = f"{sspike_dir}/sspike-{file}_{index}.csv"
            dfs[file].to_csv(path, sep=" ", index=False)

    return dfs


def basic_events(sn, detector, index=0):
    """Estimate ibd and electron scatter events for cross-checking.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation details.
    detector : sspike.detector
        Detector for simulations.

    Returns
    -------
    df : pd.Dataframe
        IBD and electron event rates for cross-checking with SNOwGLoBES rates.
    """
    ibd = ibd_events(sn, detector, index)
    e_nu = e_scat(sn, detector, index)
    df = pd.merge(ibd, e_nu, on="E")

    return df


def ibd_events(sn, detector, index=0):
    """Inverse beta decay events.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation details.
    detector : sspike.Detector
        Name of SNOwGLoBES detector.

    Returns
    -------
    df : pd.Dataframe
        Inverse beta decay event rates for cross-checking with SNOwGLoBES.
    """
    # Load fluences.
    # Energy bins 0.2 MeV and fluences cm^-2.
    fluences = get_fluences(sn, index)

    # Load cross-sections in GLoBES format.
    xscn = np.genfromtxt(xs_ibd, skip_header=3).T
    # Energies [log(E GeV)] --> [GeV].
    x_E = 10 ** xscn[0]
    # Cross-sections [10^-38 cm^-2 GeV^-1] --> [cm^-2 GeV^-1].
    x_scale = 1e-38
    x_nueb = xscn[4] * x_scale

    # Number of events: fluence * xscn * bin-size * N_electrons.
    # Energy bins of 0.2 MeV in GeV.
    df = pd.DataFrame()
    # Use the same energy grid as SNOwGLoBES
    df["E"] = np.linspace(7.49e-4, 9.975e-2, 200)
    bin_size = df["E"][1] - df["E"][0]
    bin_scale = bin_size / 0.0002
    f_nueb = np.interp(df["E"], fluences["E"], fluences["aNuE"])
    xs_nueb = np.interp(df["E"], x_E, x_nueb)
    df["ibd"] = f_nueb * xs_nueb * df["E"] * detector.N_p * bin_scale

    return df


def e_scat(sn, detector, index=0):
    """Electron-neutrino scattering events.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation details.
    detector : sspike.Detector
        Name of SNOwGLoBES detector.

    Returns
    -------
    df : pd.Dataframe
        Summed neutrino-electron events for cross-checking with SNOwGLoBES.
    """
    fluences = get_fluences(sn, index)
    # Load cross-sections.
    xscn = np.genfromtxt(xs_e, skip_header=3).T
    # Energies [log(E GeV)] --> [GeV].
    x_E = 10 ** xscn[0]
    # Cross-sections [10^-38 cm^-2 GeV^-1] --> [cm^-2 GeV^-1].
    x_scale = 1e-38
    x_nue = xscn[1] * x_scale
    x_nueb = xscn[4] * x_scale
    x_nux = xscn[2] * x_scale

    # Number of events: fluence * xscn * N_electrons.
    # Multiply cross-sections from file (in GLoBES formatting) by energy.
    df = pd.DataFrame()
    # Use the same energy grid as SNOwGLoBES.
    df["E"] = np.linspace(7.49e-4, 9.975e-2, 200)
    bin_size = df["E"][1] - df["E"][0]
    bin_scale = bin_size / 0.0002

    # Electron flavor neutrinos.
    f_nue = np.interp(df["E"], fluences["E"], fluences["NuE"])
    xs_nue = np.interp(df["E"], x_E, x_nue)
    nue_e = f_nue * xs_nue * df["E"] * detector.N_e * bin_scale

    # Positron flavor neutrinos.
    f_nueb = np.interp(df["E"], fluences["E"], fluences["aNuE"])
    xs_nueb = np.interp(df["E"], x_E, x_nueb)
    nuebar_e = f_nueb * xs_nueb * df["E"] * detector.N_e * bin_scale
    # Extra factor of 4: nux = nu_mu + nu_mubar + nu_tau + nu_taubar.
    f_nux = np.interp(df["E"], fluences["E"], fluences["NuMu"]) * 4
    xs_nux = np.interp(df["E"], x_E, x_nux)
    nux_e = f_nux * xs_nux * df["E"] * detector.N_e * bin_scale

    df["e"] = nue_e + nuebar_e + nux_e

    return df


def elastic_events(sn, detector, index=0):
    """Proton-neutrino elastic scattering events.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation details.
    detector : sspike.Detector
        Name of SNOwGLoBES detector.

    Returns
    -------
    sspiked : dataframe
        Neutrino-proton neutral-current event rates by flavor.
    """
    # Get fluences at detector.
    fluences = get_fluences(sn, index)

    # Assign local variables for simplicity and naming conventions.
    E = fluences["E"]
    f = {
        "nc_nue_p": fluences["NuE"],
        "nc_nuebar_p": fluences["aNuE"],
        "nc_nux_p": fluences["NuMu"],
        "nc_nuxbar_p": fluences["aNuMu"],
    }
    # Find differential cross-section as function of proton recoil energy.
    df = pd.DataFrame()
    # Maximum proton recoil energy for 100 MeV neutrino is 17.5 MeV.
    df["T_p"] = np.arange(1e-4, 0.0176, 1e-4)
    df["E_vis"] = quench(df["T_p"])
    # Kinematic threshold.
    df["E_min"] = (df["T_p"] + np.sqrt(df["T_p"] * (df["T_p"] + 2 * M_p))) / 2

    N_bins = len(df["T_p"])
    channels = f.keys()
    for chan in channels:
        df[chan] = np.zeros(N_bins)

    # Event rates.
    # Change from fluence bin width of 0.2 MeV.
    bin_scale = (df["T_p"][1] - df["T_p"][0]) / 2e-4
    # Scale including number of targets.
    scale = detector.N_p * bin_scale
    # Cross-section depends on proton recoil energy.
    for i in range(N_bins):
        T_p = df["T_p"][i]
        E_min = df["E_min"][i]
        # Intergrate fluences to get event rates for each flavor.
        for chan in channels:
            df[chan][i] = nc_events(T_p, E, f[chan], E_min, scale)

    df["nc_p"] = np.zeros(N_bins)
    for chan in channels:
        df["nc_p"] += df[chan]

    return df


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
    A = (Gf * hbarc) ** 2 * M_p / 2 / np.pi / E ** 2  # [GeV^-3 cm^2]
    nu2 = (Cv + a * Ca) ** 2 * E ** 2  # [GeV^2]
    p2 = (Cv ** 2 - Ca ** 2) * M_p * T_p  # [GeV^2]
    pnu = (Cv - a * Ca) ** 2 * (E - T_p) ** 2  # [GeV^2]

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
    quenching = "/Users/joe/src/gitjoe/sspike/sspike/aux/proton_quenching.csv"
    qE, qX = np.genfromtxt(quenching, delimiter=",").T
    E = T_p * np.interp(T_p, qE, qX)

    return E


def nc_events(T_p, E, f, E_min, scale=1):
    """
    Integrate neutrino differential cross-section and fluence w.r.t. energy.

    Parameters
    ----------
    T_p : float
        Proton recoil energy $[MeV]$.
    E : np.array
        Neutrino energies $[MeV]$.
    f : np.array
        Neutrino fluence $$

    Return
    ------
    E : np.array
        Electron equivalent energy in KamLAND.
    """
    N = quad(lambda x: dxs_nc(x, T_p) * np.interp(x, E, f), E_min, 0.1)[0]
    return N * scale


def event_totals(sn, detector, index=0, save=True):
    """Sum event totals from snowglobes_events() and sspike_events().

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifics.
    detector : sspike.Detector
        Detector specifics.

    Return
    ------
    df : pd.DataFrame
        3 column dataframe: file_type, channel, events.
    """
    bin_dir = detector.get_save_dir(sn)
    tot_file = f"{bin_dir}/totals_all_{index}.csv"

    # if isfile(tot_file):
    #     df = pd.read_csv(tot_file, sep=" ")

    #     return df

    row_list = []
    total_files = detector.total_files
    detector_dir = detector.get_save_dir(sn)

    for file in total_files:
        # Path to processed data files.
        path = f"{detector_dir}/{file}_{index}.csv"
        if not isfile(path):
            msg = f"\nWarning!\nFile not found. Skipping:\n{path}"
            log.warning(msg)
            continue

        # Load data.
        data = pd.read_csv(path, sep=" ")
        file_type = f"{file.split('-')[-1]}"

        # sspike-elastic data have different format than other data.
        if "sspike-elastic" in file:
            # Uncut data
            N_total = np.sum(data["nc_p"])
            row = {"file": file_type, "channel": "nc_p", "events": N_total}
            row_list.append(row)

            # Low energy cut
            nc_vis = data["nc_p"].where(data["E_vis"] >= detector.low_cut)
            N_cut = np.sum(nc_vis)
            row = {"file": file_type, "channel": "nc_p_cut", "events": N_cut}
            row_list.append(row)

        else:
            chans = list(data.keys())[1:]
            for chan in chans:
                N = np.sum(data[chan])
                row = {"file": file_type, "channel": chan, "events": N}
                row_list.append(row)

    df = pd.DataFrame(row_list)

    if save:
        df.to_csv(tot_file, sep=" ", index=False)

    return df


def vis_totals(sn, detector, index=0, save=True):
    """Select visible events from all totals.

    Parameters
    ----------
    sn : sspike.Supernova
        Supernova simulation specifics.
    detector: sspike.Detector
        Detector information.
    
    Return
    ------
    df : pd.DataFrame
        DataFrame of event totals and progenitor properties.
    """
    bin_dir = detector.get_save_dir(sn)
    vis_file = f"{bin_dir}/totals_vis_{index}.csv"

    if isfile(vis_file):
        df = pd.read_csv(vis_file, sep=" ")

        return df

    totals = event_totals(sn, detector)
    vis = detector.keep_vis(totals)

    prog_list = list(sn.progenitor.values())
    row_list = []
    for row in vis.to_numpy():
        new_row = [sn.model] + prog_list + row.tolist()
        row_list.append(new_row)

    prog_columns = list(sn.progenitor.keys())
    column_names = ["model"] + prog_columns + ["channel", "events"]

    df = pd.DataFrame(row_list, columns=column_names)

    if save:
        detector_dir = detector.get_save_dir(sn)
        vis_file = f"{detector_dir}/totals_vis_{index}.csv"
        df.to_csv(vis_file, sep=" ", index=False)

    return df


def time_events(sn, detector):
    """Process time series with snowglobes.

    Parameters
    ----------
    sn : sspike.Supernova
        Supernova simulation specifics.
    detector: sspike.Detector
        Detector information.
    
    Return
    ------
    df : pd.DataFrame
        DataFrame of event totals and progenitor properties.
    """
    ts, tm, te = sn.bin_times()

    save_dir = f"{detector.get_save_dir(sn)}/snow-files"
    if isfile(sn.tar_file):
        df = pd.read_csv(f"{save_dir}/chan_time.csv", sep=' ')

        return df

    if not isdir(save_dir):
        makedirs(save_dir)
    
    fluence_tarball(sn, t_start=ts, t_end=te)
    snowglobes.simulate(snowglobes_dir, sn.tar_file, detector_input=detector.name)
    tables = snowglobes.collate(snowglobes_dir, sn.tar_file, skip_plots=True)

    files = list(tables.keys())[1:]

    row_list = [[] for _ in range(sn.t_bins)]
    header = tables[files[0]]['header'].split(' ')

    for file in files:
        feather = f"{save_dir}/{file[:-4]}.feather"
        df = pd.DataFrame(tables[file]['data'].T, columns=header)
        df.to_feather(feather)

        if '_smeared_weighted' not in file:
            continue

        index = int(file.split(f"_{detector.name}_")[0].split('_')[-1])
        row = [tm[index].value]
        for chan in header[1:]:
            row.append(np.sum(df[chan]))
        row_list[index] = row

    columns = ['time'] + header[1:]
    totals = pd.DataFrame(row_list, columns=columns)
    totals.to_csv(f"{save_dir}/chan_time.csv", sep=' ', index=False)

    return totals
