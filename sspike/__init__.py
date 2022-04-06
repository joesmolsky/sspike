# from .core import logging
from rich.traceback import install
from ._version import __version__

install(show_locals=False)
