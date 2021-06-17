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

from ..DictUtility import __ofDictFindBlockEntryStartStop

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

def appendEntry(value, blockList=None, lineNum=16, searchValues=False):
    if blockList is not None:
        __appendBlockEntryWithBlockName(value, blockList, searchValues=searchValues)
    elif lineNum is not None:
        __appendBlockEntryWithLineNum(value, lineNum, searchValues=searchValues)
    else:
        log.error("One of 'blockList' or 'lineNum' must be specified to indicate the location to insert the dictionary entry.")

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
        found = __replaceStringEntry(
            ofValue.name,
            ofValue.value,
            file,
            silent=silent
        )
    elif rType == 'singleLine':
        #found = __replaceSingleLineEntry(
        #    ofValue.name,
        #    ofValue.value,
        #    ofValue.asString(),
        #    file,
        #    silent=silent
        #)
        found = __replaceSingleLineEntry(
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

    start, stop = __ofDictFindBlockEntryStartStop(
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
                 # written here with __ofDictAppendBlockEntryWithLineNum

def removeBlockEntries(file, blockList, searchValues=False):
    #TODO:  Merge this method with __ofDictRemoveBlockEntry() (only 2 lines are
    #  different)
    #- Removes entries in an OpenFOAM dictionary block
    #- blockList = list heiarchy to be searched
    #-   e.g.  ['geometry', 'wetwell'] removes everything within:
    #-      geometry{ wetwell{*delete_everything_here}}
    #- searchValues = switch to search within a line for block start / stop
    #-  (not yet implemented)

    print("Deleting block '"+blockList[len(blockList)-1]+"' in file: "+file)

    start, stop = __ofDictFindBlockEntryStartStop(
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
                 # written here with __ofDictAppendBlockEntryWithLineNum

def readOFDictFile(file):

    #from of.ofTypes import ofDictFile, ofDict, ofNamedList, ofIntValue, ofFloatValue, ofStrValue

    #- Function assumes:
    #   - All entries start on a new line
    #   - Comments on line after C++ code are ignored

    pyOFDict = ofDictFile(os.path.basename(file), [])

    def functionSwitcher(status):
        switcher = {
            'commentedBlock': __getOFDictCommentLineType,
            'comment': None,
            'includeLine': None,
            'empty': None,
            'commentedBlockEnd':  __getOFDictReadLineType,
            'list': __getOFDictValueType,
            'dict': __getOFDictValueType,
            'value': __storeOFDictValue,
            'multiLineUnknown': __getOFDictEntryType,
            'dictName': __newOFDictDict,
            'listName': __newOFDictList,
            'multiLineValue': __appendOFDictEntry,
            'multiLineEntryStart': __storeOFDictMultiLineEntryName,
            'singleLineSingleValuedEntry': __storeOFDictSingleLineSingleValuedEntry
        }
        return switcher.get(status, __getOFDictReadLineType)

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

######################## Private Member Functions ###########################

def __appendBlockEntryWithBlockName(
    ofValue,
    blockList,
    searchValues=False
):

    if ofValue.location is None or ofValue.filename is None:
        raise ValueError("The 'location' and 'filename' of the OpenFOAM type must be specified to update the dictionary file.")

    file = os.path.join(
            os.getcwd(),
            ofValue.location,
            ofValue.filename
    )

    #- Check if the file exists
    open(file)

    copyfile(file, file+"_old")

    start, stop = __ofDictFindBlockEntryStartStop(
        os.path.join(ofValue.location, ofValue.filename),
        blockList,
        searchValues=searchValues
    )

    if start is None: # if the block wasnt found:
        __appendBlockEntryWithLineNum(
            ofDict(name=blockList[-1], value=[], location=ofValue.location,
                   filename=ofValue.filename),
            stop)
        stop+=1

    if hasattr(ofValue, 'name') is True and ofValue.name is not None:
        print("Appending entry '"+ofValue.name+"' into block "
              +blockList[len(blockList)-1]+" at line "+str(stop)+
              " of file: "+str(os.path.join(ofValue.location, ofValue.filename)))
    else:
        print("Appending unnamed entry into block "+blockList[len(blockList)-1]+
              " at line "+str(stop)+" of file: "+
              str(os.path.join(ofValue.location, ofValue.filename)))

    try:
        with open(file+"_old") as old, open(file, "w") as new:
            for i, line in enumerate(old):
                if i == stop:
                    #- build insert string with indents
                    insertStr = ofValue.asString().split('\n')
                    for i in range(len(blockList)):
                        for j in range(len(insertStr)):
                            insertStr[j] = TAB_STR + insertStr[j]
                    #- Write lines
                    for l in insertStr:
                        new.write(l+'\n')
                    new.write(line)
                else:
                    new.write(line)
    except:
        copyfile(file+"_old", file)
        raise

def __replaceStringEntry(key, val, file, silent=False):
    #- Use "__ofDictReplaceEntry(...,rType='string')" instead
    found = False

    with open(file+"_old", 'r') as old, open(file, 'w') as new:
        for line in old:
            #if key in line:
            if key in line:
                found = True
            new.write(line.replace(key, str(val)))


    return found

def __replaceSingleLineEntry(ofValue, file, silent=False):
    #- Use "__ofDictReplaceEntry(...,rType='singleLine')" instead
    #- Replaces a single line based on OpenFOAM variable name
    #- WARNING: Does NOT search for variables of same name defined within
    #  different blocks.  A new nethod will need to be created if this search
    #  is needed.
    found = False

    key = ofValue.name
    string = ofValue.asString()
    logStr = ofValue.valueStr

    with open(file+"_old", 'r') as old, open(file, 'w') as new:

        for line in old:
            #if key in line:
            #if line.strip().startswith(key) is True:
            if (len(line.split()) > 0 and
                line.split()[0] == key):
                #- Ensure that the found key is a single lined value
                if line.split('//')[0].rstrip()[-1] != ';':
                    new.write(line)
                    continue
                #- Save any line comments:
                comment = ""
                if '//' in line:
                    commentList = line.split('//')[1:]
                    for c in commentList:
                        comment+='//'+c
                #- Count the number of leading spaces
                nSpaces = len(line) - len(line.lstrip(" "))
                pre = ''
                for _ in range(nSpaces):
                    pre += ' '
                new.write(pre+string+comment)
                found=True
                if not silent:
                    relPath = file[len(os.getcwd()):]
                    print("'"+str(key)+"' changed to '"+logStr+"' in file:  "+relPath)
                #print('in "if": '+str(key)+', '+str(val))
            else:
                new.write(line)
                #print('in "else": '+str(key)+', '+str(val))

    return found

def __findBlockEntryStartStop(file, blockList, searchValues=False):
    #TODO:  Account for the case of opening anf closing parenthesis or barackets
    #  on the same line.
    relPath = file
    file = os.path.join(os.getcwd(), file)

    if os.path.isfile(file) is False:
        raise FileNotFoundError(file)


    copyfile(file, file+"_old")

    start = 0
    stop = 0

    try:
        old = open(file, 'r')
        for line in old:
            stop+=1
        old.seek(0)
        lines = old.readlines()

        if stop <= 0:
            raise Exception('File is empty: '+file)

        for block in blockList:
            #- initialize variables to be defined below
            openStr = None
            closeStr = None

            #old.seek(start-1)

            # while 'block' is not the first word in the line:
            while True:
                lineList = lines[start].strip().split(" ")
                if block == lineList[0]:
                    break
                start += 1
                if start >= stop:
                    raise Exception("End of file '"+relPath+"' reached without finding a match for block '"+str(block)+"'.")
            for i in [0,1]: #search line with block name and next line
                if len(lines[start+i].split(" ")) > 1:
                    #- Search for opening and closing of block on the same line
                    for openChar, closeChar in zip(['(', '{'],[')', '}']):
                        if openChar in lines[start+i]:
                            openStr = openChar
                            closeStr = closeChar
                            start = start+i
                            break
                            if closeStr in lines[start+i]:
                                 print("Warning:  No values found matching block '"+block+"' within "+file)
            #- If block is not opened on same line assume it is opened on next
            #  line:
            if not openStr:
                start+=1
                openStr = lines[start].lstrip()[0]

            if openStr == '(':
                closeStr = ')'
            elif openStr == '{':
                closeStr = '}'
            else:
                raise Exception("Unexpected file format enountered at line "+str(start+1)+" of "+file)
            stop = start

            nOpenStr = 1
            nCloseStr = 0

            while nOpenStr > nCloseStr:
                if stop >= len(lines)-1:
                    raise Exception("End of file '"+relPath+"' reached without terminating block.")
                stop+=1
                nOpenStr+= lines[stop].count(openStr)
                nCloseStr+= lines[stop].count(closeStr)

        start+=1
    except:
        copyfile(file+"_old", file)
        raise

    return start, stop


def __appendBlockEntryWithLineNum(
    ofValue,
    lineNum,
    searchValues=False
):
    #- Not complete, use __ofDictAppendBlockEntryWithBlockName() instead

    file = os.path.join(
            os.getcwd(),
            ofValue.location,
            ofValue.filename
    )

    #- Check if the file exists
    open(file)

    copyfile(file, file+"_old")
    printName = ofValue.name or ""
    print("Appending block '"+str(printName)+"' at line number "+str(lineNum)+
          " of file: "+os.path.join(ofValue.location, ofValue.filename))

    try:
        with open(file+"_old") as old, open(file, "w") as new:
            for i, line in enumerate(old):
                if i == lineNum:
                    new.write(ofValue.asString())
                    new.write(line)
                else:
                    new.write(line)
    except:
        copyfile(file+"_old", file)
        raise

def __readOFDictFile(self, file):

    from of.ofTypes import ofDictFile, ofDict, ofNamedList, ofIntValue, ofFloatValue, ofStrValue

    #- Function assumes:
    #   - All entries start on a new line
    #   - Comments on line after C++ code are ignored

    pyOFDict = ofDictFile(os.path.basename(file), [])

    def functionSwitcher(self, status):
        switcher = {
            'commentedBlock': self.__getOFDictCommentLineType,
            'comment': None,
            'includeLine': None,
            'empty': None,
            'commentedBlockEnd':  self.__getOFDictReadLineType,
            'list': self.__getOFDictValueType,
            'dict': self.__getOFDictValueType,
            'value': self.__storeOFDictValue,
            'multiLineUnknown': self.__getOFDictEntryType,
            'dictName': self.__newOFDictDict,
            'listName': self.__newOFDictList,
            'multiLineValue': self.__appendOFDictEntry,
            'multiLineEntryStart': self.__storeOFDictMultiLineEntryName,
            'singleLineSingleValuedEntry': self.__storeOFDictSingleLineSingleValuedEntry
        }
        return switcher.get(status, self.__getOFDictReadLineType)


    def __argSwitcher(func, line, ofType):
        switcher = {
            __getOFDictReadLineType: len(line.split(" ")),
            __storeOFDictValue: (ofType,
                                      line[1:].remove('{()}').split(" ")
                                     )
        }
        return switcher.get(func, line.remove['()'], )

    status = 'start'
    ofType = None
    prevLine = None
    lineStatus = 'read'
    level = 0
    with open(file, 'r') as f:
        for line in f:
            if line.startswith(('//', '#')):
                #- Ignore line comments and includes
                continue
            if lineStatus == 'endMultiLine':
                #- Determine how to interpret the previous line
                [status, lineStatus] = __getOFDictMultiLinePreviousType(line)
            lineStatus = 'read'
            count = 0
            while lineStatus != 'end':
                if lineStatus == 'endMultiLine':
                    prevLine = line
                    break
                count += 1
                if count >= 100: #prevent infinite loop in case of error
                    raise Exception("Maximum number of loops reached.")
                func = functionSwitcher(status)
                if func is not None:
                    [status, lineStatus] = func(__argSwitcher(func, line, ofType))



def __getOFDictCommentLineType(startsWith):
    switcher = {
        '*/': ['commentedBlockEnd', 'end']
    }
    return [switcher.get(startsWith, 'commentedBlock'), 'end']

def __getOFDictValueType(startsWith):
    switcher = {
        '(': 'list',
        '{': 'dict'
    }
    return [switcher.get(startsWith, 'value'), 'read']

def __getOFDictMultiLineEntryType(line):
    switcher = {
        '(': 'list',
        '{': 'dict',
        'FoamFile': 'fileInfoStart'
    }
    return [switcher.get(line, 'value'), 'read']

def __ofMultiLineEntryReadNextLine(line):
    pass

def __getOFDictReadLineType(length):
    switcher = {
        0: ['empty', 'end'],
        1: ['multiLineUnknown', 'readMultiLine'],
        2: ['singleLineSingleValuedEntry', 'read']
    }
    return switcher.get(length, ['singleLineMultiValuedEntry', 'read'])

def __storeOFDictValue(line):
    pass

def __appendOFDictValue(line):
    pass

def __storeOFNamedListValue(line):
    pass

def __getOFDictMultiLinePreviousType(line):
    switcher = {
        '{': 'dictName',
        '(': 'listName'
    }
    return [switcher.get(line, 'multiLineValue'), 'read']

def __storeOFDictSingleLineSingleValuedEntry(line):
    values = line.split(" ")
    if len(values) != 2:
        raise Exception("Not able to process line format.")
    if values[1].isnumeric() is True:
        if '.' in values[1]:
            pyOFDict.add(ofFloatValue(values[0], values[1]))
        else:
            pyOFDict.add(ofIntValue(values[0], values[1]))
    elif values[1] in OF_BOOL_VALUES:
        pyOFDict.add(ofBoolValue(values[0], values[1]))
    else:
        pyOFDict.add(ofStrValue(values[0], values[1]))

    return ['newLine', 'end']

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
