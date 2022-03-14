"""Back-end event reader.

Make plots and tables of pnut outputs.
"""

from os.path import isfile

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rc('font', size=18)


def draw(events_path, channels, save=False, test=False):
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
    combos = {}
    for chan in channels:
        # SNOwGLoBES naming convention is based on '_'.
        vals = chan.split('_')
        n = len(vals)

        # Inverse beta decay.
        if n == 1:
            combos[chan] = [chan]
            continue

        # SNOwGLoBES naming convention is target last and neutrino 2nd to last.
        target = vals[-1]

        # Electron scattering and charged-current interactions have n = 2.
        if n == 2:
            # Add neutrino flavor to nucleus charged-current interations.
            if target != 'e':
                target = f'{target}-{vals[-2]}'
        # Neutral current events (not or electrons) have n = 3.
        if n == 3:
            # Plot proton elastic scattering channels separately.
            if target == 'p':
                combos[chan] = [chan]
                continue

            target = f'{target}-{vals[0]}'

        # A few other SNOwGLoBES v1.2 cross-sections have n = 4.
        if n == 4:
            target = f'{target}-{vals[0]}-{vals[1]}'

        if target not in combos:
            combos[target] = []
        combos[target].append(chan)

    # Add together channels as needed.
    rates = pd.DataFrame()
    for combo in combos:
        rates[combo] = np.zeros(N_bins)
        for chan in combos[combo]:
            rates[combo] += events[chan]

    # Plotting time.
    fig, ax = plt.subplots(1, figsize=(16, 8), facecolor='white')
    # Title plot based on file name.
    title = events_path.split('/')[-1][:-4]
    fig.suptitle(title)
    # Neutral current proton events require 2 axes.
    set_twins = False

    for rate in rates:
        # Proton elastic scattering.
        if rate[-2:] == '_p':
            if not set_twins:
                ax.set_xlim(right=5)
                ax.set_xlabel(r'$T_p\ [MeV]$')
                ax.set_ylabel(r'$Events\ [T_p\ 0.1\ MeV^{-1}]$')
                twax = ax.twiny()
                twax.set_xlabel(r'$E_{vis}\ [MeV]$')
                set_twins = True

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


def tab(snowball):
    """Count binned event rates and create a table.

    Parameters
    ----------
    snowball : Snowball

    Return
    ------
    tab : str
        File path to results.
    """
    sb = snowball

    # Location of event rates.
    data_dir = f'{sb.snowball_dir}{sb.fluence_dir}'
    data_files = ['snow-smeared.csv', 'snow-unsmeared.csv',
                  'sspike-basic.csv', 'sspike-nc.csv']
    # Output file of tabulated events.
    tab_file = f'{data_dir}totals.txt'
    tab = open(tab_file, 'w')

    for file in data_files:
        # Path to processed data files.
        path = f'{data_dir}{file}'

        # Detectors other than kamland may not have all for file types.
        if not isfile(path):
            continue

        # Load data.
        data = pd.read_csv(path, sep=' ')

        # Write file name and some dashes to improve readability.
        name = file[:-4]
        dashes = '-' * len(name)
        tab.write(f'{name}\n')
        tab.write(f'{dashes}\n')

        # sspike data have different format than SNOwGLoBES data.
        if name == 'sspike-nc':
            # Event rates with no energy threshold.
            tab.write('No energy cut\n')
            tab.write('-------------\n')
            for nu in ['nue', 'nuebar', 'nux', 'nuxbar']:
                chan = f'nc_{nu}_p'
                N = np.sum(data[chan])
                tab.write(f'{chan}: \t{N}\n')

            # 20 keV cut.
            tab.write('\n')
            tab.write('20 kev energy cut\n')
            tab.write('-----------------\n')
            cut = 2e-5
            for nu in ['nue', 'nuebar', 'nux', 'nuxbar']:
                chan = f'nc_{nu}_p'
                vis = data[chan].where(data['E_vis'] >= cut)
                N = np.sum(vis)
                tab.write(f'{chan}: \t{N}\n')

            # 100 keV cut.
            tab.write('\n')
            tab.write('100 kev energy cut\n')
            tab.write('------------------\n')
            cut = 1e-4
            for nu in ['nue', 'nuebar', 'nux', 'nuxbar']:
                chan = f'nc_{nu}_p'
                vis = data[chan].where(data['E_vis'] >= cut)
                N = np.sum(vis)
                tab.write(f'{chan}: \t{N}\n')

            # 200 keV cut.
            tab.write('\n')
            tab.write('200 kev energy cut\n')
            tab.write('------------------\n')
            cut = 2e-4
            for nu in ['nue', 'nuebar', 'nux', 'nuxbar']:
                chan = f'nc_{nu}_p'
                vis = data[chan].where(data['E_vis'] >= cut)
                N = np.sum(vis)
                tab.write(f'{chan}: \t{N}\n')

            # 300 keV cut.
            tab.write('\n')
            tab.write('300 kev energy cut\n')
            tab.write('------------------\n')
            cut = 3e-4
            for nu in ['nue', 'nuebar', 'nux', 'nuxbar']:
                chan = f'nc_{nu}_p'
                vis = data[chan].where(data['E_vis'] >= cut)
                N = np.sum(vis)
                tab.write(f'{chan}: \t{N}\n')

        elif name == 'sspike-basic':
            for chan in ['ibd', 'nue_e', 'nuebar_e', 'nux_e']:
                N = np.sum(data[chan])
                tab.write(f'{chan}: \t{N}\n')
            tab.write('\n\n')

        else:
            chans = data.keys()[1:]
            for chan in chans:
                N = np.sum(data[chan])
                tab.write(f'{chan}: \t{N}\n')
            tab.write('\n\n')

    tab.close()

    return tab_file


def bar(tabs):
    """TODO: Bar graph comparing event rates."""
    pass


def pay(tabs):
    """TODO: Print astrophysical yields.  (Show rates from tabs.)"""
    pass
