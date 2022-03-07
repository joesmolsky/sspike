"""Back-end event reader.

Process events saved by pnut.
"""

from matplotlib import lines
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rc('font', size=18)

snowball_dir = '/Users/joe/src/gitjoe/sspike/snowballs/'


def display(events, channels=['ibd', 'e']):
    """Display event rates."""
    # Ensure file list type.
    if not type(events) == list:
        events = [events]

    # Create text file for summary of results.
    # Example file name:
    # '/Users/joe/src/gitjoe/sspike/snowballs/Nak-20-20-300/snow-smeared.csv'
    snow_dir, filename = events[0].split('/')[-2:]
    distance = snow_dir.split('-')[-1]
    label = filename.split('-')[1][:-4]
    sum_file = f"{snowball_dir}{snow_dir}/{distance}kpc.txt"

    # Plot results from each file.
    fig, ax = plt.subplots(1, figsize=(8, 6), facecolor='white')

    sf = open(sum_file, 'w')
    for file in events:
        # Get distance and labels from file name.
        # Example file name:
        # '~/src/gitjoe/sspike/snowballs/Nak-20-20-300/snow-smeared.csv'
        snow_dir, filename = file.split('/')[-2:]
        distance = snow_dir.split('-')[-1]
        label = filename.split('-')[1][:-4]
        sf.write(f"{label}\n")
        data = pd.read_csv(file, sep=' ')

        # NC events.
        if channels == ['nc']:
            cut = 0.0003
            for flav in ['nue', 'nueb', 'nux', 'nuxb']:
                ax.plot(data['E_vis'] * 1e3, data[flav], label=flav)
                sf.write(f"nc-{flav}: {np.sum(data[flav])}\n")
                vis = data['E_vis'].where(data['E_vis'] > cut)
                sf.write(f"nc-{flav}-cut-{cut*1e3}: {np.sum(vis)}\n")
            ax.hlines(1, 0, 0.8, linestyles=':', color='black')
            ax.vlines(0.3, 1e-4, 1e3, linestyles=':', color='black')

        # ibd events.
        if 'sspike-e' not in file:
            if 'ibd' in channels:
                ax.plot(data['E'], data['ibd'], label=f'ibd-{label}')
                sf.write(f"ibd: {np.sum(data['ibd'])}\n")

        # Electron scattering events.
        if 'snow-' in file:
            chans = ['nue_e', 'nuebar_e', 'numu_e',
                     'numubar_e', 'nutau_e', 'nutaubar_e']
            e_tot = pd.Series(np.zeros(len(data['E'])))
            for chan in chans:
                n_chan = np.sum(data[chan])
                e_tot += data[chan]
                sf.write(f"{chan} events: {n_chan}\n")
                ax.plot(data['E'], data[chan], label=f'e-{label}')
            ax.plot(data['E'], e_tot)
            sf.write(f"e: {np.sum(e_tot)}\n")

        if 'sspike-e' in file:
            chans = ['nue_e', 'nueb_e', 'nux_e']
            e_tot = 0
            for chan in chans:
                n_chan = np.sum(data[chan])
                e_tot += n_chan
                sf.write(f"{chan} events: {n_chan}\n")
                ax.plot(data['E'], data[chan], label=f'sspike-{chan}')
            sf.write(f"sspike-e: {np.sum(e_tot)}\n")

    ax.set_yscale('log')
    sf.close()
    plt.legend()
    plt.show()
