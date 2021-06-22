import os
import json
import pandas as pd

from.private._unitDecoder import _unitDecoder

def readInputs(filepath=os.path.join(os.getcwd(), 'inputParameters')):
    """
    Reads a JSON formatted parameters file, while interpreting units and converting values to standard OpenFOAM units (i.e. SI).

    Parameters
    ----------

    filepath: str
            The path of the JSON file location

    Returns: dict
            A Python dictionary of parameters

    """

    with open(filepath, "r") as paramsFile:
        params = json.load(paramsFile, object_hook=_unitDecoder)

    #- Convert list of dicts to Pandas dataframe
    for param in params.keys():
        if isinstance(params[param], list):
            if all([isinstance(item, dict) for item in params[param]]):
                df = pd.DataFrame(params[param])
                params[param] = df.set_index(df.columns[0])

    return params
