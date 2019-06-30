# -*- coding: utf-8 -*-

__title__ = "shinkei"
__author__ = "Lorenzo"
__license__ = "MIT"
__copyright__ = "Copyright 2019 Lorenzo"
__version__ = "0.0.1a"

import logging

from .client import Client, _ClientMixin
from .exceptions import *
from .objects import Version, MetadataPayload
from .querybuilder import Node, QueryBuilder


def connect(*args, **kwargs):
    return _ClientMixin(*args, **kwargs)


try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, _):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
