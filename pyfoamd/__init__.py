import os

from .richinclude import richLogger

richLogger("DEBUG")

from . import functions
from . import types


try:
    FOAM_VERSION = os.environ['WM_PROJECT_VERSION']
except:
    FOAM_VERSION = None
    print("OpenFOAM not found!")
