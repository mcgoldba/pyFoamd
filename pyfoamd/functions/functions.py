import sys

#- Check the python version:
if  sys.version_info < (3,7):
    sys.exit('Sorry, Python < 3.7 is not supported.')

from pyfoamd.types import ofDictFile, ofDict, ofNamedList, ofNamedSplitList, ofInt, ofFloat, ofStr, ofBool, ofDimensionedScalar, ofVector, ofNamedVector, ofDimensionedVector, TAB_STR

import os
from shutil import copyfile
import re
import math
#import numpy as np
import subprocess
import tempfile

from pint import UnitRegistry
import json
import pandas as pd
# from functools import reduce
# import operator
# from collections.abc import Mapping

from .private.readDict import readDict
from .private.dictUtil import _appendBlockEntryWithBlockName, _replaceStringEntry,\
_replaceSingleLineEntry, _findBlockEntryStartStop, _findEndOfDict,\
_appendBlockEntryWithLineNum, _readOFDictFile, _ofDictFindBlockEntryStartStop,\
_findEndOfHeader

from rich import print
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
        level="NOTSET",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

from rich.traceback import install
install()

#Define padding for blockMeshDict
PAD = 1 / 12 / 3.281 # 1 inch


def getLatestTime(directory):

    #- Get the latest time directory
    directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    latestTime = '0'
    for directory in directories:
        name = directory.replace('/', '')
        if name.isdigit() is True:
            if int(name) > int(latestTime):
                latestTime = name

    return directory

def appendEntry(value, blockList=None, lineNum=None, searchValues=False,
                insert=False, whitespace=False):
    """
    Append an ofType into a dictoinary file.

    Parameters
    ----------

    value: ofType
        The OpenFOAM value to append.

    blockList: list(str)
        The list of sub dictionaries into which the value is to appended.

    lineNum: int
        The line number at which to append the value.  This argument is ignored
        if 'blockList' is specified.

    insert: bool
        If `True`, the `value` is inserted at the beggining of the dictionary
        instead of appending to the end.

    """
    if blockList is not None:
        _appendBlockEntryWithBlockName(value, blockList,
                                       searchValues=searchValues,
                                       whitespace=whitespace)
    elif lineNum is not None:
        _appendBlockEntryWithLineNum(value, lineNum,
                                     searchValues=searchValues,
                                     whitespace=whitespace)
    else:
        #log.warning("Neither 'blockList' or 'lineNum' was specified."\
        #            "  Appending entry to end of dict")
        if insert:
            _appendBlockEntryWithLineNum(value,
                            _findEndOfHeader(os.path.join(
                                value.location, value.filename)),
                            searchValues=searchValues,
                            whitespace=whitespace
                            )
        else:
            _appendBlockEntryWithLineNum(value,
                    _findEndOfDict(os.path.join(value.location, value.filename)),
                    searchValues=searchValues,
                    whitespace=whitespace
                    )
        #sys.exit()
def insertBlockEntry(value, blockList=None, lineNum=16):
    pass

def replaceEntry(ofValue, rType='singleLine', silent=False):
    #- Base function for ofDict replacements
    #- rType = Replacement type.  One of:  ['string', 'singleLine']

    file = os.path.join(
            os.getcwd(),
            ofValue.location,
            ofValue.filename
    )

    #- Check if the file exists
    open(file)

    copyfile(file, file+"_old")

    if rType == 'string':
        found = _replaceStringEntry(
            ofValue.name,
            ofValue.value,
            file,
            silent=silent
        )
    elif rType == 'singleLine':
        #found = _replaceSingleLineEntry(
        #    ofValue.name,
        #    ofValue.value,
        #    ofValue.asString(),
        #    file,
        #    silent=silent
        #)
        found = _replaceSingleLineEntry(
            ofValue,
            file,
            silent=silent
        )
    else:
        raise ValueError("Unrecognized replace type: "+str(rType))

    if found == False:
        copyfile(file+"_old", file)
        raise ValueError("Key "+ str(ofValue.name)+ \
                     " not found in file:  "+ \
                     os.path.join(ofValue.location,ofValue.filename)+'\n')

def removeEntry(file, blockList, searchValues=False):
    #- Removes lists or dicts in an OpenFOAM dictionary that are split between
    #   many lines.
    #- blockList = list heiarchy to be searched
    #-   e.g.  ['geometry', 'wetwell'] removes everything within:
    #-      geometry{ wetwell{*delete_everything_here}}
    #- searchValues = switch to search within a line for block start / stop
    #-  (not yet implemented)

    entryName = blockList[len(blockList)-1]

    print("Deleting entry '"+entryName+"' in file: "+file)

    start, stop = _ofDictFindBlockEntryStartStop(
        file,
        blockList,
        searchValues=searchValues
    )

    if any([s is None for s in [start,stop]]):
        print("\tBlock entry '"+entryName+"' not found.  Nothing to delete.")
        return None

    #- Correct start and stop locations to delete entry including names and
    #   brackets or parenthesis
    start -= 2
    stop+=1

    file = os.path.join(os.getcwd(), file)

    if start>= stop:
        print("\tNo lines to delete.")
    else:
        print("\tDeleting values for block '"+entryName+"', between lines "\
              +str(start+1)+" and "+str(stop)+".")
        #- delete lines in file
        with open(file, 'r+') as new:
            lines = new.readlines()
            del lines[start:stop]
            new.seek(0)
            new.truncate()
            new.writelines(lines)



    return start # return the line where the block ends, so values can be
                 # written here with _ofDictAppendBlockEntryWithLineNum

def removeBlockEntries(file, blockList, searchValues=False):
    #TODO:  Merge this method with _ofDictRemoveBlockEntry() (only 2 lines are
    #  different)
    #- Removes entries in an OpenFOAM dictionary block
    #- blockList = list heiarchy to be searched
    #-   e.g.  ['geometry', 'wetwell'] removes everything within:
    #-      geometry{ wetwell{*delete_everything_here}}
    #- searchValues = switch to search within a line for block start / stop
    #-  (not yet implemented)

    print("Deleting block '"+blockList[len(blockList)-1]+"' in file: "+file)

    start, stop = _ofDictFindBlockEntryStartStop(
        file,
        blockList,
        searchValues=searchValues
    )

    file = os.path.join(os.getwd(), file)


    if start>= stop:
        print("\tNo lines to delete.")
    else:
        print("\tDeleting values for block '"+blockList[len(blockList)-1]+"', between lines "+str(start+1)+" and "+str(stop)+".")
        #- delete lines in file
        with open(file, 'r+') as new:
            lines = new.readlines()
            del lines[start:stop]
            new.seek(0)
            new.truncate()
            new.writelines(lines)



    return start # return the line where the block ends, so values can be
                 # written here with _ofDictAppendBlockEntryWithLineNum

def readOFDictFile(file):

    #from of.ofTypes import ofDictFile, ofDict, ofNamedList, ofIntValue, ofFloatValue, ofStrValue

    #- Function assumes:
    #   - All entries start on a new line
    #   - Comments on line after C++ code are ignored

    pyOFDict = ofDictFile(os.path.basename(file), [])

    def functionSwitcher(status):
        switcher = {
            'commentedBlock': _getOFDictCommentLineType,
            'comment': None,
            'includeLine': None,
            'empty': None,
            'commentedBlockEnd':  _getOFDictReadLineType,
            'list': _getOFDictValueType,
            'dict': _getOFDictValueType,
            'value': _storeOFDictValue,
            'multiLineUnknown': _getOFDictEntryType,
            'dictName': _newOFDictDict,
            'listName': _newOFDictList,
            'multiLineValue': _appendOFDictEntry,
            'multiLineEntryStart': _storeOFDictMultiLineEntryName,
            'singleLineSingleValuedEntry': _storeOFDictSingleLineSingleValuedEntry
        }
        return switcher.get(status, _getOFDictReadLineType)

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

    #- Convert list of dicts to Pandas dataframe
    for param in params.keys():
        if isinstance(params[param], list):
            if all([isinstance(item, dict) for item in params[param]]):
                df = pd.DataFrame(params[param])
                params[param] = df.set_index(df.columns[0])

    return params

def printInputParams(filepath='inputParameters'):

    params = readInputParameters(filepath)

    print(params)

def cleanDictFile(filepath):
    pass
######################## Private Member Functions ###########################


def _interpretUnitsAndConvert(dct):
    """
    Reads string formatted dimensional values and converts to a float in OpenFOAM standard units


    Parameters
    ----------

    dct: dict
        (Potentially nested) Dictionary of values to be parsed

    Returns
    -------

    convetedDict: dict
        Equivalent dictionary with dimensioned values converted to "float" types

    """
    pass


    try:
        ureg
    except NameError:
        ureg=UnitRegistry()


    convertedDict = {}

    #- Parse nested dictionaries (from https://stackoverflow.com/questions/10756427/loop-through-all-nested-dictionary-values)
    def loopContents(v):
        if any([type(v) is t for t in [dict, list, tuple]]):
            iterateIterable(obj, v, k=None)
        elif type(v) is str:
            #- Process 'str' values
            if len(v.split(" "))>=2:
                vList = v.split(" ")
                try:
                    mag = float(vList)
                except ValueError:
                    pass
                try:
                    unit = " ".join(vList[1:])
                    ureg[unit]
                except UndefinedUnitError:
                    pass
                v = mag*ureg[unit]



    def iterateIterable(obj):
        if type(obj) is dict:
            for k, v in obj.items():
                loopContents(obj, v, k)
        elif type(obj) is list or type(obj) is tuple:
            for v in obj:
                loopContents(obj, v)
        else:
            log.error('Invalid "obj" provided')
            sys.exit()

    loopContents(dct)

    return convertedDict

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
