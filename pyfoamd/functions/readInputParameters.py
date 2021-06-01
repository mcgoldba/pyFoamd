import json
from pint import UnitRegistry

def readInputParameters(filepath):
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
        params = json.load(paramsFile, object_hook=__unitDecoder)

    return params

def __unitDecoder(dct):
    """
    Object hook function for the python 'json.load()' function.
    Reads in dimensional values as strings and converts to float value in SI units.

    Parameters
    ----------

    dct: dict
        The parsed json file as a python dictionary

    Returns
    -------

    dct: dict
        The parsed Python dictionary with converted units

    """

    ureg = UnitRegistry(system='SI')

    ###- Helper function 1
    def _decodeUnits(v):
        if isinstance(v, str):
            vList = v.split(" ")
            if len(vList) >= 2:
                try:
                    mag = float(vList[0])
                except:
                    #continue
                    return v
                try:
                    unit = (" ".join(vList[1:]))
                    #log.debug("trying unit conversion on "+str(v)+"...")
                    unit = ureg(unit)
                except:
                    unit = ureg(unit)
                    #log.debug("Failed.")
                    #continue
                    return v
                #log.debug("Success.")
                v = mag*unit
                return v.to_base_units().magnitude
            else:
                return v
        else:
            return v

    ###- Helper function 2
    #- from stackoverflow: 34615164
    def _parseOrDecode(obj):
        if isinstance(obj, dict):
            return {k:_parseOrDecode(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_parseOrDecode(v) for v in obj]
        return _decodeUnits(obj)

    return _parseOrDecode(dct)
