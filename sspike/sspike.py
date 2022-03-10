"""Command-line entry-point for `sspike`."""
from argparse import ArgumentParser, FileType

from .core.logging import getLogger, initialize_logging

log = getLogger(__name__)


def main():
    """Parse arguments and run."""
    # Description for -h, --help flags
    description = 'simulated supernovae products inducing KamLAND events.'
    parser = ArgumentParser(description=description)

    # Flag options
    parser.add_argument('-v', '--version',
                        action='version', version='0.0.2')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='include all messages in log file')
    parser.add_argument('-i', '--info', action='store_true',
                        help='include info messages in log file')
    parser.add_argument('-o', '--output', dest='outfile', metavar='FILE',
                        default='../out/default.txt', type=FileType(mode='w'),
                        help='output file path (default <stdout>)')
    parser.add_argument('-m', '--model', default='Nakazato_2013',
                        help='model options: Nakazato_2013')
    parser.add_argument('-D', '--distance', default='10',
                        help='supernovae distance in kpc (default 10)')

    cmdline = parser.parse_args()

    # Logging level
    if cmdline.debug:
        initialize_logging('debug')
    elif cmdline.info:
        initialize_logging('info')
    else:
        initialize_logging('warning')

    log.debug('\n****\nBegin Processing.\n****\n')

    model = cmdline.model
    distance = cmdline.distance

    # Physics!!!
    log.info(f"\n+++ Running {model} model at {distance} kpc:+++\n")

    # End of main()
    log.debug('\n****\nsspike.main complete.\n****\n')
    print("Job's done.")
    return 0
