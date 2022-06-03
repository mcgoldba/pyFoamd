import os
from pathlib import Path

import logging

# def getLatestTime(directory=Path.cwd()):

#     #- Get the latest time directory
#     directories = [f.name for f in Path(directory).iterdir()]
#     latestTime = '0'
#     for directory in directories:
#         name = directory.replace('/', '')
#         if name.isdigit() is True:
#             if int(name) > int(latestTime):
#                 latestTime = name

#     return latestTime

def getLatestTime(caseDir=Path.cwd()):

    logger = logging.getLogger('xcfdv')
    
    #- Get the latest time directory for reconstructed case
    directories = [f.name for f in os.scandir(Path(caseDir).resolve()) if f.is_dir()]
    latestTime = '0'
    for directory in directories:
        name = directory.replace('/', '')
        if name.isdigit() is True:
            if int(name) > int(latestTime):
                latestTime = name

    #- Get the latest time for the decomposed case
    p0 = Path(caseDir) / 'processor0'
    platestTime = '0'
    if (p0).is_dir():
        directories = [f.name for f in os.scandir(p0) if f.is_dir()]
        for directory in directories:
            name = directory.replace('/', '')
            if name.isdigit() is True:
                if int(name) > int(platestTime):
                    platestTime = name

    latestTime = max(float(latestTime), float(platestTime)) 

    return latestTime