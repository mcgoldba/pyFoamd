import sys
from pathlib import Path

from pyfoamd.types import _parseNameTag

import logging
logger = logging.getLogger('pf')



def parseNameTag(name):
    """
    Replace any special characters not allowed in python attribute names with a 
    suitable replacement, as specified in the `SPECIAL_CHARS` variable.
    """
    return _parseNameTag(name)