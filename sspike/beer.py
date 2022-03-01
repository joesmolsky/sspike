"""Back-end event reader.

Process events saved by pnut.
"""

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rc('font', size=18)

snowball_dir = '/Users/joe/src/gitjoe/sspike/snowballs/'


def combo(sspiked, snowflakes):
    """Combine sspike and snewpy results and return as dataframe."""
    pass


def display(events, channels=['ibd', 'e']):
    """Display event rates."""
    # Ensure file list type.
    if not type(events) == list:
        events = [events]

    # Create text file for summary of results.
    # Example file name:
        #   '/Users/joe/src/gitjoe/sspike/snowballs/Nak-20-20-300/snow-smeared.csv'
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
        # '/Users/joe/src/gitjoe/sspike/snowballs/Nak-20-20-300/snow-smeared.csv'
        snow_dir, filename = file.split('/')[-2:]
        distance = snow_dir.split('-')[-1]
        label = filename.split('-')[1][:-4]
        sf.write(f"{label}\n")

        # ibd events.
        data = pd.read_csv(file, sep=' ')
        ax.plot(data['E'], data['ibd'], label=f'ibd-{label}')
        sf.write(f"ibd: {np.sum(data['ibd'])}\n")

        # electron scattering events.
        e_tot = data['nue_e'] + data['nuebar_e'] + data['numu_e']\
            + data['numubar_e'] + data['nutau_e'] + data['nutaubar_e']
        ax.plot(data['E'], e_tot, label=f'e-{label}')
        sf.write(f"e: {np.sum(e_tot)}\n")

    plt.legend()
    plt.show()
