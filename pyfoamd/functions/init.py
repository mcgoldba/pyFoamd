from pyfoamd import getPyFoamdConfig, setLoggerLevel
from pyfoamd.types import ofCase
from pathlib import Path

# from pyfoamd.config import DEBUG

def init(path=Path.cwd()):
    """
    Read an OpenFOAM case and store as a Python dictionary.
    """
    setLoggerLevel("DEBUG" if bool(getPyFoamdConfig('debug')) else "INFO")

    return ofCase(path=path)
