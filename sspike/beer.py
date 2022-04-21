"""Back-end event reader.

Make plots and tables of pnut outputs.
"""

from os.path import isfile

import pandas as pd
from matplotlib import rcParams
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u

from .core.logging import getLogger
log = getLogger(__name__)

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Times']
rcParams['font.size'] = 22


def draw(events_path, channels, nc_flavors=False, save=False, test=False):
    """Plot event rates.

    Parameters
    ----------
    events_path : str
        Location of dataframe csv.
    channels : list of str
        Interaction channels to plot.

    Note
    ----
        Proton neutral rates cannot be combined with other rates yet.
    """
    events = pd.read_csv(events_path, sep=' ')
    if 'nc_nue_p' in events:
        N_bins = len(events['T_p'])
    else:
        N_bins = len(events['E'])

    # Combine similar channels before plotting.
    combos = sort_channels(channels)

    # Add together channels as needed.
    rates = pd.DataFrame()
    for combo in combos:
        rates[combo] = np.zeros(N_bins)
        for chan in combos[combo]:
            rates[combo] += events[chan]

    N_flavor = {}
    if nc_flavors:
        for flavor in combos['p-nc']:
            N_flavor[flavor] = events[flavor]

    # Plotting time.
    fig, ax = plt.subplots(1, figsize=(16, 8), facecolor='white')
    # Title plot based on file name.
    title = events_path.split('/')[-1][:-4]
    fig.suptitle(title)
    # Neutral current proton events require 2 axes.
    set_twins = False

    for rate in rates:
        log.debug(f"Drawing {rate}.")
        # Proton elastic scattering.
        if rate == "p-nc":
            if not set_twins:
                # ax.set_xlim(right=0.7)
                ax.set_xlabel(r'$T_p\ [MeV]$')
                ax.set_ylabel(r'$Events\ [T_p\ 0.1\ MeV^{-1}]$')
                ax.set_yscale('log')
                # ax.set_ylim(bottom=1e-2)
                twax = ax.twiny()
                twax.set_xlabel(r'$E_{vis}\ [MeV]$')
                set_twins = True
                # ax.set_aspect(1)

            if nc_flavors:
                for flavor in N_flavor:
                    ax.plot(events['T_p']*1e3, events[flavor],
                            label=flavor, linestyle=':')
                    twax.plot(events['E_vis']*1e3, events[flavor],
                              label=flavor)
                continue

            ax.plot(events['T_p']*1e3, rates[rate], label=rate, linestyle=':')
            twax.plot(events['E_vis']*1e3, rates[rate], label=rate)

            continue

        ax.plot(events['E']*1e3, rates[rate], label=rate)
        ax.set_xlim(right=60)
        ax.set_xlabel(r'$E\ [MeV]$')

    plt.tight_layout(pad=1.0)
    plt.legend()
    if save:
        plt.savefig(save, dpi=600, facecolor='white')
        if test:
            return 0
    plt.show()


def get_tab(sn, detector, save=True):
    """Count binned event rates and create a table.

    Parameters
    ----------
    sn : sspike.Supernova

    Return
    ------
    tab : pd.DataFrame
        3 column dataframe: file_type, channel, events.
    """
    # record = sn.get_record()
    data_files = ['snow-unsmeared_weighted.csv', 'snow-smeared_weighted.csv',
                  'sspike-basic.csv', 'sspike-elastic.csv']

    row_list = []
    for file in data_files:
        # Path to processed data files.
        path = f'{sn.bin_dir}/{file}'
        # Load data.
        data = pd.read_csv(path, sep=' ')
        file_type = file.split('-')[1][:-4]

        # sspike data have different format than SNOwGLoBES data.
        if file == 'sspike-elastic.csv':
            # Uncut data
            N_total = np.sum(data['nc_p'])
            row = {'file': file_type, 'channel': 'nc_p', 'events': N_total}
            row_list.append(row)

            # Low energy cut
            nc_vis = data['nc_p'].where(data['E_vis'] >= detector.low_cut)
            N_cut = np.sum(nc_vis)
            row = {'file': file_type, 'channel': 'nc_p_cut', 'events': N_cut}
            row_list.append(row)

        else:
            chans = list(data.keys())[1:]
            for chan in chans:
                N = np.sum(data[chan])
                row = {'file': file_type, 'channel': chan, 'events': N}
                row_list.append(row)

    df = pd.DataFrame(row_list)

    if save:
        tab_file = f'{sn.bin_dir}/totals.csv'
        df.to_csv(tab_file, sep=' ', index=False)

    return df


def bin_times(bliz):
    """Return array of times for plotting."""

    window_start = bliz.t_start
    window_end = bliz.t_end
    window_bins = bliz.t_bins
    t_left = np.linspace(window_start, window_end, window_bins, endpoint=False) * u.s
    t_right = t_left + (window_end - window_start) / window_bins * u.s
    t_mid = (t_left + t_right) * 0.5

    return t_mid

def series_plot(bliz, sno, times, plot_type):
    """Plot channels from tables."""
    K = list(sno.keys())
    old_name = K[1].split('tbin')

    n_chan = pd.DataFrame()
    t_bins = bliz.t_bins
    n_chan['time'] = np.zeros(t_bins)

    for i in range(t_bins):
        n_chan['time'][i] = times[i]
        key = f"{old_name[0]}tbin{i+1}.{'.'.join(old_name[1].split('.')[1:])}"

        if i == 0:
            cols = sno[key]['header'].split()
            n_cols = len(cols)
        
        for j in range(1, n_cols):
            if i == 0:
                n_chan[cols[j]] = np.zeros(t_bins)
            n_chan[cols[j]][i] += sum(sno[key]['data'][j])

    sno_pd = f'{bliz.series_path}sno_pd.csv'
    n_chan.to_csv(path_or_buf=sno_pd, sep=' ')

        # nevents is per bin per s
    factor = bliz.t_bins / (bliz.t_end - bliz.t_start)

    fig, ax = plt.subplots(1, figsize=(16, 8), facecolor='white')
    for chan in n_chan.keys():
        if chan == 'time':
            continue
        ax.plot(times * u.s, n_chan[chan] * factor, label=chan)

    ax.set_xlabel("$t$ [s]")
    ax.set_ylabel("Counts [s$^{-1}$]")
    ax.set_yscale('log')
    ax.set_ylim(bottom=1e-2)
    ax.legend(bbox_to_anchor=(1.02, 1.))
    plt.title(f'{bliz.sn_name} {plot_type[1:]}')
    plt.show()
