"""Back-end event reader.

Make plots and tables of pnut outputs.
"""
import matplotlib.pyplot as plt
from matplotlib import rcParams
import plotly.express as px

from . import pnut
from .core.logging import getLogger
log = getLogger(__name__)

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Times']
rcParams['font.size'] = 22
rcParams['legend.fontsize'] = 18


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
    fig, ax = plt.subplots(figsize=(10,5), tight_layout=True, facecolor='white')
    for flavor in flavors:
        ax.plot(lum['time'], lum[flavor], label=flavor)
    ax.set(xscale='log',
           xlim=(5e-3, 12),
           xlabel='Time [s]',
           ylabel='Luminosity [$10^{53}$ erg s$^{-1}$]',
           title=sn.sn_name)
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    fig.tight_layout()

    if save:
        path = f'{sn.sn_dir}/luminosity.png'
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_fluences(sn, flu=None, save=True, show=True):
    """Plot fluences at earth for a single model.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    flu : pd.DataFrame, optional
        Fluences from `pnut.get_luminosities(sn)`.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    if flu is None:
        flu = pnut.get_fluences(sn)
    
    time = sn.t_end - sn.t_start
    title = f'{sn.sn_name} ({time} s)'
    
    flavors = list(flu.keys())[1:]
    fig, ax = plt.subplots(figsize=(10,5), tight_layout=True, facecolor='white')
    for flavor in flavors:
        ax.plot(flu['E']*1e3, flu[flavor], label=flavor)
    ax.set(xlim=(-0.1, 40),
           xlabel='Energy [MeV]',
           ylabel='Fluence [cm$^{-2}$]',
           title=title)
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    fig.tight_layout()

    if save:
        path = f'{sn.bin_dir}/fluences.png'
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_snowglobes_events(sn, detector, snow_events=None,
                           save=True, show=True):
    """Plot SNOwGLoBES unsmeared and smeared event rates.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    snow_events : dict of pd.DataFrame, optional
        Events dictionary from `pnut.get_snowglobes_events(sn, detector)`.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    if snow_events is None:
        snow_events = pnut.snowglobes_events(sn, detector)
    log.debug(f'\nsnow_events: {snow_events}\n')
    
    title = f'{sn.sn_name} @ {sn.distance} kpc in {detector.name}'
    fig, ax = plt.subplots(figsize=(10,5), tight_layout=True, facecolor='white')
    
    df = snow_events['unsmeared_weighted']
    flavors = list(df.keys())[1:]
    for flavor in flavors:
        ax.plot(df['Energy']*1e3, df[flavor], linestyle='--')

    plt.gca().set_prop_cycle(None)

    df = snow_events['smeared_weighted']
    for flavor in flavors:
        ax.plot(df['Energy']*1e3, df[flavor], label=flavor)

    ax.set(xlim=(-0.1, 40),
           xlabel='Energy [MeV]',
           yscale='log',
           ylim=(1e-4, None),
           ylabel='Events [0.5 MeV$^{-1}$]',
           title=title)
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    fig.tight_layout()

    if save:
        path = f'{sn.bin_dir}/snow-events.png'
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def plot_sspike_events(sn, detector, sspike_events=None, save=True, show=True):
    """Plot sspike event rates.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    snow_events : dict of pd.DataFrame, optional
        Events dictionary from `pnut.get_sspike_events(sn, detector)`.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    if sspike_events is None:
        sspike_events = pnut.sspike_events(sn, detector)
    
    title = f'{sn.sn_name} @ {sn.distance} kpc in {detector.name}'
    fig, ax = plt.subplots(figsize=(10,6), tight_layout=True, facecolor='w')
    ax.set(xlabel='E$_{vis}$ [MeV]',
           yscale='log',
           ylim=(1e-4, None),
           ylabel='Events [0.1 MeV$^{-1}$ (T$_p$)]',
           title=title)
    
    df = sspike_events['elastic']
    flavors = list(df.keys())[3:]
    for flavor in flavors:
        ax.plot(df['E_vis']*1e3, df[flavor], label=flavor)

    plt.gca().set_prop_cycle(None)

    ax2 = ax.twiny()
    for flavor in flavors:
        ax2.plot(df['T_p']*1e3, df[flavor], linestyle='--')

    ax2.set(xlabel='T$_p$ [MeV]', xlim=(None, 10))
    ax2.xaxis.set_ticks_position("bottom")
    ax2.xaxis.set_label_position("bottom")
    ax2.spines["bottom"].set_position(("axes", -0.25))

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    fig.tight_layout()

    if save:
        path = f'{sn.bin_dir}/sspike-events.png'
        plt.savefig(path, dpi=600)

    if show:
        plt.show()


def bar_totals(sn, detector, totals=None, save=True, show=True):
    """Bar graph of all event totals for a single model.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    snow_events : dict of pd.DataFrame, optional
        Events dictionary from `pnut.get_snowglobes_events(sn, detector)`.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    if totals is None:
        totals = pnut.event_totals(sn, detector)
    title = f'{sn.sn_name} @ {sn.distance} kpc in {detector.name}'
    labels={'channel': 'Channel', 'events': 'Events', 'file': 'Type'}

    bars = px.bar(totals, x='channel', y='events', color='file', 
                  barmode='group', labels=labels, log_y=True)
    bars.layout.bargap = 0.05
    bars.layout.bargroupgap = 0.03
    bars.layout.title = title
    bars.layout.font = dict(size=18, family="Times New Roman")
    bars.layout.width = 800
    bars.layout.height = 400

    if save:
        path = f'{sn.bin_dir}/totals'
        bars.write_image(f'{path}.png', width=1100, height=500, scale=3)
        bars.write_html(f'{path}.html')
    if show:
        bars.show()


def bar_vis(sn, detector, totals=None, save=True, show=True):
    """Bar graph of visible event totals for a single model.

    Parameters
    ----------
    sn : sspike.Supernova
        Simulation specifications.
    detector : sspike.Detector
        Detector specifications.
    snow_events : dict of pd.DataFrame, optional
        Events dictionary from `pnut.get_snowglobes_events(sn, detector)`.
    save : bool, default True
        Save plot in sn.bin_dir.
    show : bool, default True
        Display plot.
    """
    if totals is None:
        totals = pnut.event_totals(sn, detector)

    title = f'{sn.sn_name} @ {sn.distance} kpc in {detector.name}'
    labels={'channel': 'Channel', 'events': 'Events', 'file': 'Type'}
    
    if detector.name == 'kamland':
        keep = (totals['file'] == 'smeared_weighted') |\
               (totals['channel'] == 'nc_p_cut')
        vis = totals.where(keep).dropna()
        vis.replace('nc_p_cut', 'nc_p', inplace=True)
    else:
        msg = f'Error: need to update for {detector.name}'
        log.error(msg)
        return msg

    bars = px.bar(vis,  x='channel', y='events', color='channel',
                  labels=labels, log_y=True)
    bars.layout.font = dict(size=18, family="Times New Roman")
    bars.layout.width = 700
    bars.layout.height = 400
    bars.layout.title = title
    bars.layout.showlegend = False
    
    if save:
        path = f'{sn.bin_dir}/bar_vis'
        bars.write_image(f'{path}.png', scale=3)
        bars.write_html(f'{path}.html')
    if show:
        bars.show()


# def bin_times(bliz):
#     """Return array of times for plotting."""

#     window_start = bliz.t_start
#     window_end = bliz.t_end
#     window_bins = bliz.t_bins
#     t_left = np.linspace(window_start, window_end, window_bins, endpoint=False) * u.s
#     t_right = t_left + (window_end - window_start) / window_bins * u.s
#     t_mid = (t_left + t_right) * 0.5

#     return t_mid

# def series_plot(bliz, sno, times, plot_type):
#     """Plot channels from tables."""
#     K = list(sno.keys())
#     old_name = K[1].split('tbin')

#     n_chan = pd.DataFrame()
#     t_bins = bliz.t_bins
#     n_chan['time'] = np.zeros(t_bins)

#     for i in range(t_bins):
#         n_chan['time'][i] = times[i]
#         key = f"{old_name[0]}tbin{i+1}.{'.'.join(old_name[1].split('.')[1:])}"

#         if i == 0:
#             cols = sno[key]['header'].split()
#             n_cols = len(cols)
        
#         for j in range(1, n_cols):
#             if i == 0:
#                 n_chan[cols[j]] = np.zeros(t_bins)
#             n_chan[cols[j]][i] += sum(sno[key]['data'][j])

#     sno_pd = f'{bliz.series_path}sno_pd.csv'
#     n_chan.to_csv(path_or_buf=sno_pd, sep=' ')

#         # nevents is per bin per s
#     factor = bliz.t_bins / (bliz.t_end - bliz.t_start)

#     fig, ax = plt.subplots(1, figsize=(16, 8), facecolor='white')
#     for chan in n_chan.keys():
#         if chan == 'time':
#             continue
#         ax.plot(times * u.s, n_chan[chan] * factor, label=chan)

#     ax.set_xlabel("$t$ [s]")
#     ax.set_ylabel("Counts [s$^{-1}$]")
#     ax.set_yscale('log')
#     ax.set_ylim(bottom=1e-2)
#     ax.legend(bbox_to_anchor=(1.02, 1.))
#     plt.title(f'{bliz.sn_name} {plot_type[1:]}')
#     plt.show()
