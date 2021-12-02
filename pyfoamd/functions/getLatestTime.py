import os
from pathlib import Path

from richinclude import *

def getLatestTime(directory=Path.cwd()):

    #- Get the latest time directory
    directories = [f.name for f in Path(directory).iterdir()]
    latestTime = '0'
    for directory in directories:
        name = directory.replace('/', '')
        if name.isdigit() is True:
            if int(name) > int(latestTime):
                latestTime = name

    return latestTime
