import json
import os
import sys

from richinclude import *

#TODO:  Should this replace the inputParameters file?
def readConfig(key, file="xcfdv.json"):
    """
    Reads a value to the specified configuration file.

    Parameters
    ----------

    key : str
        The dictionary entries to read from the config file

    file : str 
        The ini file to write the data in.

    """

    if file[-5:] != ".json":
        file = file+".json"

    filepath = os.path.join(".xcfd", file)

    config = {}

    #convert the entry to string
    #entry = {str(key): str(value) for key, value in entry.items()}

    if os.path.isfile(filepath) is False:
        log.error("Config file not found!:\n"+filepath)
        sys.exit()
    else:
        config = json.load(open(filepath))
        return config[key]
