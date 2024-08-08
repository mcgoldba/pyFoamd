import json
import os
import sys
from pathlib import Path

import logging

log = logging.getLogger("pf")

#TODO:  Should this replace the inputParameters file?
def readConfig(key=None, file="pyfoamd.json", caseDir=Path.cwd()):
    """
    Reads a value to the specified configuration file, or returns the 
    configuration file as a python dictionary.

    Parameters
    ----------

    key : str
        The dictionary entries to read from the config file

    file : str
        The ini file to write the data in.

    """

    if file[-5:] != ".json":
        file = file+".json"

    # filepath = os.path.join(".params", file)
    filepath = str(Path(caseDir) / ".params" /file)

    config = {}

    #convert the entry to string
    #entry = {str(key): str(value) for key, value in entry.items()}

    if os.path.isfile(filepath) is False:
        log.warning("Config file not found!: "+filepath)
        return None
    else:
        config = json.load(open(filepath))
        if key:
            if key in config:
                return config[key]
            else:
                keyStr = ""
                for k in config.keys():
                    keyStr+= k+', '
                keyStr = keyStr[:-2]+"."
                log.warning("Key '"+str(key)+"' not found in file.  Found keys "
                "are: "+keyStr)
        else:
            return config
