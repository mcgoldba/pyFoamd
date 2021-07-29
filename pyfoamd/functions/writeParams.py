import json
import pandas as pd
from copy import deepcopy
from pyfoamd.types import TAB_SIZE

def writeParams(params, filepath='inputParameters'):

    #Create temporary object
    params_ = deepcopy(params)

    #Convert all dataframes back to dictionaries
    for key, value in params_.items():
        if isinstance(value, pd.DataFrame):
            params_[key] = value.to_dict()

    with open(filepath, 'w')  as fp:
        json.dump(params_, fp, indent=TAB_SIZE)

    del params_
