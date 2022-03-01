"""Process neutrino underground telemetry.

Load models and process event rates with snewpy, SNoGLoBES, and sspike.
"""


import tarfile

from snewpy import snowglobes

# File paths.
# Location of snewpy models directory.
models_dir = '/Users/joe/src/snewpy/models/'
# SNOwGLoBES location.
snowglobes_path = "/Users/joe/src/gitjoe/snowglobes/"
# sspike snowball directory.
snowball_path = "/Users/joe/src/gitjoe/sspike/snowballs/"


def get_fluence(model, progenitor, transform, distance):
    """Save integrated fluence and return filepath."""
    # Simulation properties
    mass = progenitor['mass']
    metal = progenitor['metal']
    t_rev = progenitor['rev']
    # Supernovae model filename.
    model_file = f'nakazato-shen-z{metal}-t_rev{t_rev}ms-s{mass}.0.fits'
    model_path = f'{models_dir}/{model}/{model_file}'
    # Path for snowball.
    out_file = f"{model[:3]}-{mass}-{int(metal*1e3)}-{t_rev}-{distance}"

    # Generate fluence with snewpy and get path to output.
    snowball = snowglobes.generate_fluence(model_path, model, transform,
                                           distance, out_file)
    # Extract snewpy output in sspike snowball directory.
    with tarfile.open(snowball) as sb:
        sb.extractall(f"{snowball_path}{out_file}")

    return snowball, out_file


def snowglobes_events(snowball, out_file, detector):
    """Save events predicted using snewpy and SNOwGLoBES and
    return filepath.
    """
    # Simulate via snewpy and make a table of the results.
    snow = snowglobes.simulate(snowglobes_path, snowball,
                               detector_input=detector)

    # Save results
    smears = ['unsmeared', 'smeared']
    snowflakes = []
    for smear in smears:
        snow_path = f"{snowball_path}{out_file}/snow-{smear}.csv"
        data = snow[detector][out_file]['weighted', smear]
        data.to_csv(path_or_buf=snow_path, sep=' ')
        snowflakes.append(snow_path)

    return snowflakes


def elastic_events(snowball, detector):
    """Save events predicted using sspike return filepath."""
    pass
