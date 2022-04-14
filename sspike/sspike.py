"""Command-line entry-point for `sspike`.

Parameters
----------
model : str
    Name of supernova model type or file path simulation specifications.
detector : str, optional
    Detector for simulations.  Default `kamland`.
distance : float, optional
    Distance to supernova in kpc.  Default 5.0.
transform : str, optional
    Type of transformation to apply.  Default `NoTransformation`.
mass : float or str, optional
    Progenitor mass in solar masses.  Required for several models.
metal : float, optional
    Progenitor metallicity.  Required for `Nakazato_2013`.
revival_time : str or int, optional
    Shock revival time. Required for `Nakazato_2013`.
omega: str, optional
    Rotation of progenitor.  Required for `Kuroda_2020`.
b_field : str or int, optional
    Magnetic field strength of progenitor.  Required for `Kuroda_2020`.
eos : str, optional
    Nuclear equation of state.  Required for `Sukhbold_2015`.
stir: str or float, optional
    Progenitor stirring parameter.  Required for `Warren_2020`.

Note
----
Supernova model and detector must be included in `snewpy` and `SNOwGLoBES`.
"""
from argparse import ArgumentParser  # TODO: output files using FileType
import json
import itertools

from sspike import pnut
from sspike import beer
from sspike.snowball import Snowball
from sspike.detectors import Detector
from .core.logging import getLogger, initialize_logging
from ._version import __version__

log = getLogger(__name__)


def main():
    # Description for -h, --help flag.
    description = 'simulated supernovae products inducing KamLAND events'

    # Command line arguments.
    parser = ArgumentParser(prog='sspike', description=description)

    # Supernova model type or file path.
    parser.add_argument('model',
                        help='name of supernova model type or file path')
    # Detector.
    parser.add_argument('-D', '--detector', default='kamland', metavar='',
                        help='Detector for simulations')
    # Distance to supernovae.
    parser.add_argument('-L', '--baseline',
                        default=5.0, metavar='', type=float,
                        help='supernovae distance in kpc (default 5.0)')
    # Neutrino transformation.
    parser.add_argument('-X', '--transform', default='NoTransformation',
                        metavar='', help='transformation type from snewpy')
    # Time bins
    parser.add_argument('-T', '--time-bins', default=1,
                    metavar='', help='number of time bins (default 1)')
    # Progenitor properties.
    parser.add_argument('-M', '--mass', metavar='',
                        help='progenitor mass in solar masses')
    parser.add_argument('-Z', '--metal', metavar='', type=float,
                        help='metallicity (Nakazato_2013)')
    parser.add_argument('-R', '--revival-time', metavar='',
                        help='revival time (Nakazato_2013)')
    parser.add_argument('-O', '--omega', metavar='',
                        help='rotation binary (Kuroda_2020)')
    parser.add_argument('-B', '--b-field', metavar='',
                        help='magnetic field (Kuroda_2020)')
    parser.add_argument('-N', '--eos', metavar='',
                        help='nuclear equation of state (Sukhbold_2015)')
    parser.add_argument('-S', '--stir', metavar='',
                        help='stirring parameter (Warren_2020)')
    # Other arguments.
    parser.add_argument('-f', '--file', metavar='',
                        help='file path to simulations dictionary')
    parser.add_argument('-v', '--version',
                        action='version', version=__version__)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='include all messages in log file')
    # TODO: add output options.
    # parser.add_argument('-o', '--output', dest='outfile', metavar='FILE',
    #                     default=stdout, type=FileType(mode='w'),
    #                     help='output file path (default <stdout>)')
    cmdline = parser.parse_args()

    # Logging level
    if cmdline.debug:
        initialize_logging('debug')
    else:
        initialize_logging('info')

    # Initial debugging message.
    log.debug('\n****\nBegin debugging!\n****\n')
    # Command line arguments and values for debugging.
    arg_msg = '\n- Command line arguments:\n'
    for arg in vars(cmdline):
        arg_msg += f"\t- {arg}: {getattr(cmdline, arg)}\n"
    log.debug(arg_msg)

    # Shorten variable names.  Better way to do this?
    model = cmdline.model
    detector = cmdline.detector
    distance = cmdline.baseline
    transform = cmdline.transform
    mass = cmdline.mass
    metal = cmdline.metal
    t_rev = cmdline.revival_time
    omega = cmdline.omega
    B0 = cmdline.b_field
    eos = cmdline.eos
    stir = cmdline.stir
    t_bins = cmdline.time_bins

    # Dictionary for progenitor properties.  Better way to do this?
    progenitor = {}
    prog_vals = [mass, metal, t_rev, omega, B0, eos, stir]
    prog_keys = ['mass', 'metal', 't_rev', 'omega', 'B0', 'eos', 'stir']

    # Debugging message.
    prog_msg = '\n- Allowed progenitor variables:\n'
    for i in range(len(prog_vals)):
        prog_msg += f"\t- {prog_keys[i]}:"\
                    f"\t {prog_vals[i]} {type(prog_vals[i])}\n"
        if prog_vals[i]:
            progenitor[prog_keys[i]] = prog_vals[i]
    log.debug(prog_msg)

    # Physics!!!
    # Model name for single simulation.
    if '.' not in model:
        print(f'Starting simulation: {model} \t {progenitor}.')
        run_sim(model, progenitor, transform, distance, detector, t_bins)

    # File name for (multiple) simulation(s).
    else:
        with open(model, 'r') as f:
            info = json.load(f)

        # List of (model-type, progenitor) tuples.
        sims = []
        for sim in info['sim']:
            for pair in itertools.product(sim['model'], sim['progenitor']):
                sims.append(pair)

        # List of (distance, transform, detector) tuples.
        params = itertools.product(info['transform'],
                                   info['distance'],
                                   info['detector'])

        # List of each simulation file with each set of parameters.
        runs = itertools.product(sims, params)

        # Run simulations in series.
        for run in runs:
            model = run[0][0]
            progenitor = run[0][1]
            transform = run[1][0]
            distance = run[1][1]
            detector = run[1][2]
            description = f"\tModel: {model}\n"\
                          f"\tProgenitor: {progenitor}\n"\
                          f"\tDistance: {distance} kpc\n"\
                          f"\tDetector: {detector}\n"
            
            # PHYSICS!!!
            print(f'Starting simulation:\n {description}')
            run_sim(model, progenitor, transform, distance, detector)
            print('\nSimulation complete.\n')

    # End of main()
    log.debug('\n****\nsspike.main complete.\n****\n')

    print("Job's done.")

    return 0


def run_sim(model, progenitor, transform, distance, detector, t_bins=1):
    """Process simulation file with `SNoGLoBES` and `sspike`.

    Parameters
    ----------
    model : str
        Model name from `snewpy`.
    progenitor : dict
        Model specific parameters for simulation file.
    transform : str
        Type of `snewpy` transformation to apply.
    distance : float
        Distance to supernova.
    detector : str
        Name of detector in `SNOwGLoBEs`.
    t_bins : int
        Number of time bins to divide simulation
    """
    # Log initial supernovae information.
    sn_info = f"\n- Running {model} model at {distance} kpc in {detector}.\n"
    sn_info += "- Progenitor properties:\n"
    for key in progenitor.keys():
        sn_info += f"\t- {key}: {progenitor[key]}\n"
    log.info(sn_info)

    # Load model.
    log.debug('\n- Generating Snowball.\n')
    sb = Snowball(model, progenitor, transform, distance)

    # Detector string to class.
    log.debug(f'\n- Initializing detector: {detector}.\n')
    detector = Detector(detector)

    # Process with SNOwGLoBES.
    log.debug('\n- Processing with SNOwGLoBES .\n')
    snowflakes = pnut.snowglobes_events(sb, detector)
    log.info(f'- SNOwGLoBES files:\n\t-{snowflakes[0]}\n\t-{snowflakes[1]}')

    # Process with sspike.
    log.debug('\n- Processing with sspike.\n')
    sspikes = pnut.sspike_events(sb, detector)
    log.info(f'- sspike files:\n\t-{sspikes[0]}\n\t-{sspikes[1]}')

    # Tabulate results
    log.debug('\n- Tabulating results.\n')
    tab = beer.tab(sb)
    log.info(f'- tab file:\n\t-{tab}')
