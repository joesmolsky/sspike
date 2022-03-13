"""Command-line entry-point for `sspike`."""
from argparse import ArgumentParser  # TODO: output files using FileType

from sspike import pnut
from sspike.snowball import Snowball
from sspike.targets import Target
from .core.logging import getLogger, initialize_logging

log = getLogger(__name__)


def main():
    """Parse arguments and run."""
    # Description for -h, --help flags
    description = 'simulated supernovae products inducing KamLAND events'
    parser = ArgumentParser(prog='sspike', description=description)

    # Command line arguments.
    # Supernova model type.
    parser.add_argument('model',
                        help='name of supernova model type from snewpy')
    # Target/detector.
    parser.add_argument('-T', '--detector', default='kamland', metavar='',
                        help='target/detector for simulations')
    # Distance to supernovae.
    parser.add_argument('-D', '--distance', default=5, metavar='', type=float,
                        help='supernovae distance in kpc (default 5)')
    # Neutrino transformation.
    parser.add_argument('-X', '--transform', default='NoTransformation',
                        metavar='', help='transformation type from snewpy')
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
    parser.add_argument('-v', '--version',
                        action='version', version='0.0.4')
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

    # Shorten variable names.  Do you know a better way to do this?
    model = cmdline.model
    detector = cmdline.detector
    distance = cmdline.distance
    transform = cmdline.transform
    mass = cmdline.mass
    metal = cmdline.metal
    t_rev = cmdline.revival_time
    omega = cmdline.omega
    B0 = cmdline.b_field
    eos = cmdline.eos
    stir = cmdline.stir

    # Dictionary for progenitor properties.
    progenitor = {}
    prog_vals = [mass, metal, t_rev, omega, B0, eos, stir]
    prog_keys = ['mass', 'metal', 't_rev', 'omega', 'B0', 'eos', 'stir']
    prog_msg = '\n- Possible progenitor variables:\n'
    for i in range(len(prog_vals)):
        prog_msg += f"\t- {prog_keys[i]}:"\
                    f"\t {prog_vals[i]} {type(prog_vals[i])}\n"
        if prog_vals[i]:
            progenitor[prog_keys[i]] = prog_vals[i]
    log.debug(prog_msg)

    # Log initial supernovae information.
    sn_info = f"\n- Running {model} model at {distance} kpc in {detector}.\n"
    sn_info += "- Progenitor properties:\n"
    for key in progenitor.keys():
        sn_info += f"\t- {key}: {progenitor[key]}\n"
    log.info(sn_info)

    # Physics!!!
    log.debug('\n- Generating Snowball.\n')
    sb = Snowball(model, progenitor, transform, distance)
    log.debug(f'\n- Assigning target: {detector}.\n')
    target = Target(detector)
    log.debug('\n- Processing with SNOwGLoBES .\n')
    snowflakes = pnut.snowglobes_events(sb, target)
    log.info(f'- SNOwGLoBES files:\n\t-{snowflakes[0]}\n\t-{snowflakes[1]}')
    log.debug('\n- Processing with sspike.\n')
    sspikes = pnut.sspike_events(sb, target)
    log.info(f'- sspike files:\n\t-{sspikes[0]}\n\t-{sspikes[1]}')
    # End of main()
    log.debug('\n****\nsspike.main complete.\n****\n')

    print("Job's done.")

    return 0
