import json
import pandas as pd
from copy import deepcopy
from pyfoamd.types import TAB_SIZE

from pyfoamd.richinclude import *

log.setLevel(logging.DEBUG)

#from: https://stackoverflow.com/a/33062932

class JSONPandasEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.reset_index().to_dict(orient='records')
        return json.JSONEncoder.default(self,obj)

def writeParams(params, filepath='inputParameters'):

    #Create temporary object
    params_ = deepcopy(params)

    with open(filepath, 'w')  as fp:
        json.dump(params_, fp, indent=TAB_SIZE,sort_keys=True,
                  cls=JSONPandasEncoder)

    del params_
