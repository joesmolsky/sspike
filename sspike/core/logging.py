"""
Modified python 201 logger (by letner) for logging to `log_file`.
Ref: https://python-tutorial.dev/201/tutorial/logging.html
"""
from datetime import date as dt
from socket import gethostname
from logging import (getLogger, NullHandler, Formatter, FileHandler,
                     DEBUG, INFO, WARNING, ERROR, CRITICAL)

HOST = gethostname()

log_date = dt.today().strftime('%Y-%m-%d')
log_file = f'/Users/joe/src/gitjoe/sspike/log/{log_date}.log'
fh = FileHandler(log_file)

formatter = Formatter(f'%(asctime)s on {HOST}\n'
                      f'  %(levelname)s [%(name)s] %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

fh.setFormatter(formatter)

logger = getLogger('sspike')
logger.addHandler(NullHandler())

levels = {'debug': DEBUG, 'info': INFO, 'warning': WARNING,
          'error': ERROR, 'critical': CRITICAL}


def initialize_logging(level):
    """Initialize top-level logger with the file handler and a `level`."""
    if fh not in logger.handlers:
        logger.addHandler(fh)
        logger.setLevel(levels.get(level))
        logger.propagate = False