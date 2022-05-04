"""Back-end event reader.

Make plots and tables of pnut outputs.
"""
import matplotlib.pyplot as plt
from matplotlib import rcParams
import plotly.express as px
import pandas as pd
import numpy as np

from . import pnut
from .core.logging import getLogger

log = getLogger(__name__)

rcParams["font.family"] = "sans-serif"
rcParams["font.sans-serif"] = ["Times"]
rcParams["font.size"] = 22
rcParams["legend.fontsize"] = 18


def plot_luminosities(sn, lum=None, save=True, show=True):
    """Plot initial luminosities for a single model.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    lum : pd.DataFrame, optional
        Luminosities from `pnut.get_luminosities(sn)`.
    save : bool, default True
        Save plot in sn.sn_dir.
    show : bool, default True
        Display plot.
    """
    if lum is None:
        lum = pnut.get_luminosities(sn)

    flavors = list(lum.keys())[1:]

    fig, ax = plt.subplots(figsize=(10, 5), tight_layout=True, facecolor="white")
    for flavor in flavors:
        ax.plot(lum["time"], lum[flavor], label=flavor)

    ax.set(
        xscale="log",
        xlabel="Time [s]",
        ylabel="Luminosity [$10^{53}$ erg s$^{-1}$]",
        title=sn.sn_name,
    )
    if sn.model == "Nakazato_2013":
        ax.set(xlim=(5e-3, 12),)
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    fig.tight_layout()

    if save:
        path = f"{sn.prog_dir}/luminosity.png"
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_fluences(sn, index=0, cut=0, save=True, show=True):
    """Plot fluences at earth for a single model.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    flu = pnut.get_fluences(sn, index=index)

    time = sn.t_end - sn.t_start
    title = f"{sn.sn_name} ({time:.4f} s)"

    if cut:
        title = f"{title} (cut: {cut})"

    flavors = list(flu.keys())[1:]
    fig, ax = plt.subplots(figsize=(10, 5), tight_layout=True, facecolor="white")
    for flavor in flavors:
        ax.plot(flu["E"][cut:] * 1e3, flu[flavor][cut:], label=flavor)
    ax.set(
        xlim=(-0.1, 40),
        xlabel="Energy [MeV]",
        ylabel="Fluence [cm$^{-2}$]",
        title=title,
    )
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    fig.tight_layout()

    if save:
        path = f"{sn.bin_dir}/fluences_{index}.png"
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_snowglobes_events(
    sn, detector, index=0, with_unsmeared=True, save=True, show=True
):
    """Plot SNOwGLoBES unsmeared and smeared event rates.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    log.debug("\nPlotting SNOwGLoBES events.\n")
    snow_events = pnut.snowglobes_events(sn, detector, index)

    title = f"{sn.sn_name} @ {sn.distance} kpc in {detector.name}"
    fig, ax = plt.subplots(figsize=(10, 5), tight_layout=True, facecolor="white")

    if with_unsmeared:
        df = snow_events[f"unsmeared_weighted_{index}"]
        flavors = list(df.keys())[1:]
        for flavor in flavors:
            ax.plot(df["Energy"] * 1e3, df[flavor], linestyle="--")

    plt.gca().set_prop_cycle(None)

    df = snow_events[f"smeared_weighted_{index}"]
    flavors = list(df.keys())[1:]
    for flavor in flavors:
        ax.plot(df["Energy"] * 1e3, df[flavor], label=flavor)

    ax.set(
        xlim=(-0.1, 40),
        xlabel="Energy [MeV]",
        yscale="log",
        ylim=(1e-4, None),
        ylabel="Events [0.5 MeV$^{-1}$]",
        title=title,
    )
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    fig.tight_layout()

    if save:
        path = f"{detector.get_save_dir(sn)}/snow-events_{index}.png"
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_sspike_events(sn, detector, index=0, save=True, show=True):
    """Plot sspike event rates.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    sspike_events = pnut.sspike_events(sn, detector, index)

    title = f"{sn.sn_name} @ {sn.distance} kpc in {detector.name}"
    fig, ax = plt.subplots(figsize=(10, 6), tight_layout=True, facecolor="w")
    ax.set(
        xlabel="E$_{vis}$ [MeV]",
        yscale="log",
        ylim=(1e-4, None),
        ylabel="Events [0.1 MeV$^{-1}$ (T$_p$)]",
        title=title,
    )

    df = sspike_events[f"elastic_{index}"]
    flavors = list(df.keys())[3:]
    for flavor in flavors:
        ax.plot(df["E_vis"] * 1e3, df[flavor], label=flavor)

    plt.gca().set_prop_cycle(None)

    ax2 = ax.twiny()
    for flavor in flavors:
        ax2.plot(df["T_p"] * 1e3, df[flavor], linestyle="--")

    ax2.set(xlabel="T$_p$ [MeV]", xlim=(None, 10))
    ax2.xaxis.set_ticks_position("bottom")
    ax2.xaxis.set_label_position("bottom")
    ax2.spines["bottom"].set_position(("axes", -0.25))

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    fig.tight_layout()

    if save:
        path = f"{detector.get_save_dir(sn)}/sspike-events_{index}.png"
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def bar_totals(sn, detector, index=0, save=True, show=True):
    """Bar graph of all event totals for a single model.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    totals = pnut.event_totals(sn, detector, index)

    title = f"{sn.sn_name} @ {sn.distance} kpc in {detector.name}"
    labels = {"channel": "Channel", "events": "Events", "file": "Type"}

    bars = px.bar(
        totals,
        x="channel",
        y="events",
        color="file",
        barmode="group",
        labels=labels,
        log_y=True,
    )
    bars.layout.bargap = 0.05
    bars.layout.bargroupgap = 0.03
    bars.layout.title = title
    bars.layout.font = dict(size=18, family="Times New Roman")
    bars.layout.width = 700
    bars.layout.height = 400

    if save:
        path = f"{detector.get_save_dir(sn)}/totals"
        bars.write_image(f"{path}.png", width=1100, height=500, scale=3)
        bars.write_html(f"{path}.html")
    if show:
        bars.show()


def bar_vis(sn, detector, index=0, save=True, show=True):
    """Bar graph of visible event totals for a single model.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    vis = pnut.vis_totals(sn, detector, index)

    title = f"{sn.sn_name} @ {sn.distance} kpc in {detector.name}"
    labels = {"channel": "Channel", "events": "Events"}

    bars = px.bar(
        vis, x="channel", y="events", color="channel", labels=labels, log_y=True
    )
    bars.layout.font = dict(size=18, family="Times New Roman")
    bars.layout.width = 700
    bars.layout.height = 400
    bars.layout.title = title
    bars.layout.showlegend = False

    if save:
        path = f"{detector.get_save_dir(sn)}/totals_vis"
        bars.write_image(f"{path}.png", scale=3)
        bars.write_html(f"{path}.html")
    if show:
        bars.show()


def plot_series(sn, detector, save=True, show=True):
    """Plot channels from chan_time.csv
    
    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    totals = pd.read_csv(f"{detector.get_save_dir(sn)}/chan_time.csv", sep=" ")

    channels = list(totals.keys())[1:]

    dt = (sn.t_end - sn.t_start) / sn.t_bins

    fig, ax = plt.subplots(1, figsize=(16, 8), facecolor="white")

    for chan in channels:
        ax.plot(totals["time"], totals[chan], label=chan)

    ax.set_xlabel("$t$ [s]")
    ax.set_ylabel("Counts")
    ax.set_yscale("log")
    ax.set_ylim(bottom=1e-3)
    ax.legend(bbox_to_anchor=(1.02, 1.0))

    plt.title(
        f"{sn.sn_name} @ {sn.distance} kpc in {detector.name} with {round(dt, 4)} s bins"
    )
    fig.tight_layout()

    if save:
        path = f"{detector.get_save_dir(sn)}/chan_time.png"
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_N_chan(sn, detector, chan, events=False, save=True, show=True):
    """Display counts binned by time and energy for given channel using plt.imshow().

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    chan : str
        Name of channel to display or 'random'.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    save_dir = detector.get_save_dir(sn)

    if chan == "random":
        title = "Random bins"
        N_chan = sn.random_df()

    else:
        title = f"{chan} rates"
        N_chan = pd.read_csv(f"{save_dir}/N_{chan}.csv", sep=" ", index_col=0)

    times = N_chan.index.values
    energy = pnut.snow_energy()
    t0, t1 = times[0], times[-1]
    e0, e1 = energy[0] * 1e3, energy[-1] * 1e3

    if events:
        rand = sn.random_df()
        N_chan.index = rand.index
        N_chan.columns = rand.columns
        N_chan = rand > np.exp(-N_chan)
        N = np.sum(np.sum(N_chan))
        title = f"{N} {chan} events"

    plt.imshow(
        N_chan,
        origin="lower",
        extent=[e0, e1, t0, t1],
        aspect="auto",
        interpolation="none",
    )

    plt.title(title)
    plt.xlabel("Energy [MeV]")
    plt.ylabel("Time [s]")
    clb = plt.colorbar()
    clb.ax.set_title("N(E, t)")

    if save:
        path = f"{save_dir}/N_{chan}.png"
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_distance_rates(sn, detector, save=True, show=True):
    """Plot event rates as a function of distance for each channel.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    vis = pnut.vis_totals(sn, detector)

    x = np.arange(0.1, 1e2, 0.1)
    d = sn.distance

    fig, ax = plt.subplots(1, figsize=(10, 5), facecolor="white")

    for chan in vis["channel"]:
        N = vis[vis["channel"] == chan]["events"].values[0]
        y = N * d ** 2 / x ** 2
        ax.plot(x, y, label=chan)

    ax.set_xlabel("Distance [kpc]")
    ax.set_ylabel("Events")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.legend(bbox_to_anchor=(1.02, 1))

    plt.title(f"{sn.sn_name} rates in {detector.name}")
    fig.tight_layout()

    if save:
        path = f"{detector.get_save_dir(sn)}/N_distance.png"
        plt.savefig(path, dpi=600)

    if show:
        plt.show()
