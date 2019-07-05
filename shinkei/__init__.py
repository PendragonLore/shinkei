# -*- coding: utf-8 -*-

__title__ = "shinkei"
__author__ = "Lorenzo"
__license__ = "MIT"
__copyright__ = "Copyright 2019 Lorenzo"
__version__ = "0.0.9"

import logging

from . import ext
from .client import Client, connect
from .exceptions import *
from .handlers import Handler, HandlerMeta, listens_to
from .objects import MetadataPayload, Version
from .querybuilder import Node, QueryBuilder

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, _):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
