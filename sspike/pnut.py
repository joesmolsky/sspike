"""Process neutrino underground telemetry.

Load models and process event rates with snewpy, SNoGLoBES, and sspike.
"""


import tarfile

from snewpy import snowglobes

# File paths.
# Location of snewpy models directory.
models_dir = '/Users/joe/src/snewpy/models/'
# SNOwGLoBES location.
SNOwGLoBES_path = "/Users/joe/src/gitjoe/snowglobes/"
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
    out_file = f"{model[:3]}-{mass}-{int(metal*1e3)}-{t_rev}"

    # Generate fluence with snewpy and get path to output.
    snowball = snowglobes.generate_fluence(model_path, model, transform,
                                           distance, out_file)
    # Extract snewpy output in sspike snowball directory.
    with tarfile.open(snowball) as sb:
        sb.extractall(f"{snowball_path}{out_file}")

    return snowball


def snowglobes_events(snowball, detector):
    """Save events predicted using snewpy and SNOwGLoBES and
    return filepath.
    """
    pass


def elastic_events(snowball, detector):
    """Save events predicted using sspike return filepath."""
    pass
