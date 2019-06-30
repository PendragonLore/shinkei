# -*- coding: utf-8 -*-

__title__ = "discord"
__author__ = "Rapptz"
__license__ = "MIT"
__copyright__ = "Copyright 2019 Lorenzo"
__version__ = "0.0.1a"

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
