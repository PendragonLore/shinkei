import logging

from .client import Client
from .exceptions import *
from .objects import Version
from .querybuilder import QueryBuilder

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, _):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
