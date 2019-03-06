"""
nanolib
~~~~~~~

nanolib is a Python library allowing to work with NANO cryptocurrency
functions such as block creation and manipulation, account generation and
proof-of-work validation and solving
"""
from .accounts import *
from .blocks import *
from .exceptions import *
from .units import *
from .work import *
from .util import *


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
