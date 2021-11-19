from pathlib import Path
import sys
import re

from .isCase import isCase

from pyfoamd.config import DEBUG
DEBUG=False

from pyfoamd.richinclude import *

def listCases(path=Path.cwd(), absolutePath=False):
    if isinstance(path, str):
        path = Path(path)
    if isCase(path): #is the root directory an OpenFOAM case?
        if absolutePath:
            return [Path]
        else:
            return [path.relative_to(path)]

    cases = []

    for p in path.rglob('*'):
        if isCase(p):
            if absolutePath:
                cases.append(p)
            else:
                cases.append(p.relative_to(path))
    return cases
