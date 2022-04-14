from pyfoamd.functions import readConfig
import json
from pathlib import Path

def readCaseFromCache(name='_case.json'):
    """
    Reads in a case from the cached data (stored as `.pyfoamd/_case.json`).
    """

    if name[-5:] != '.json':
        name+='.json'

    filepath = Path('.pyfoamd') / name

    return json.load(open(filepath))