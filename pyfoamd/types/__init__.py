from dataclasses import dataclass, field, make_dataclass
from typing import List
import operator
from collections.abc import MutableMapping
import copy
from pathlib import Path
import warnings
import sys

from inspect import signature #- just for debugging

from ._isOFDict import _isOFDict
#from ._readDictFile import _readDictFile

from rich.console import Console
console = Console()

import logging

log = logging.getLogger('pyfoamd')


OF_BOOL_VALUES = {
    'on': True, 'off': False, 'true': True, 'false': False, 
    'yes': True, 'no':False
    }
TAB_SIZE = 4
OF_HEADER = """/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  7
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/"""
#- Build the string to be used as a tab
TAB_STR = ""
for _ in range(TAB_SIZE): TAB_STR+= " "

def printNameStr(name) -> str:
    if len(name) >= 12:
        return name+"\t"
    else:
        return "{: <12}".format(name)


def _interpretValue(value):
    if isinstance(value, float):
        return ofFloat(value)

TYPE_REGISTRY = []


def _populateRegistry(path):
    reg = []

    return field(default_factory=lambda: copy.copy(reg))


@dataclass
class ofTimeReg:
    pass


# @dataclass(frozen=True)
# class ofFolder:
#     _path: Path
#     #_path: Path = field(init=False)
#
#     def __post_init__(self):
#         #object.__setattr__(self, '_name',
#                            # Path(self._input).name or self.__input)
#         object.__setattr__(self, '_path', Path(self._path))
#         # self._name = Path(self._input).name or self.__input
#         # self._path = Path(self._input) or Path.cwd() / self.__input
#
#
#
#         addDirs = []
#         for obj in self._path.iterdir():
#             if obj.is_dir():
#                 fields = list(self.__dict__.keys())
#                 if any([obj.name == field_ for field_ in fields]):
#                     warnings.warn(f"'{obj.name}' is a reserved attribute.  "
#                                   "Skipping directory: {obj} ")
#                     continue
#                 addDirs.append((obj, ofFolder(obj)))
#
#         self.__class__ = make_dataclass('ofFolder',
#                                         addDirs,
#                                         bases=(ofFolder,), frozen=True)

class FolderParser:  # Class id required because 'default_factory' argument 
                     # 'makeOFFolder' must be zero argument
    def __init__(self, path):
        self.path = path

    def makeOFFolder(self):

        attrList = [('_path', Path, field(default=self.path))]
        for obj in Path(self.path).iterdir():
            #- Prevent invalid ofFolder attribute names:
            name_ = obj.name.replace('.', '_')
            if obj.is_dir():
                if obj.name == '_path':
                    warnings.warn(f"'{obj.name}' is a reserved attribute.  "
                                "Skipping directory: {obj} ")
                    continue
                attrList.append((name_, ofFolder, 
                    field(default_factory=FolderParser(obj).makeOFFolder)))
            # - Check for OpenFOAM dictionary files
            if obj.is_file() and _isOFDict(obj):
                attrList.append( (name_, ofDictFile,
                                #field(default=DictFileParser(obj).readDictFile()) )
                                field(default_factory=
                                    DictFileParser(obj).readDictFile) )
                )

        dc_ = make_dataclass('ofFolder', 
                            attrList, frozen=True)

        log.debug(f"ofFolder dataclass: {dc_}")
        log.debug(f"ofFolder dataclass: {signature(dc_)}")

        return dc_()


# @dataclass
# class ofCase:
#     location: Path = field(default=Path.cwd().parent)
#     name: str = field(default=Path.cwd().name)
#     constant: ofFolder = field(default=ofFolder('constant'))
#     system: ofFolder = field(default=ofFolder('system'))
#     times: ofTimeReg = field(default=ofTimeReg())
#     registry: list = _populateRegistry(location)
#
#     def __post_init__(self):
#         addDirs = []
#         for obj in self.location.iterdir():
#             if (obj.is_dir() and all(obj.name != default for default in
#                                      ['constant', 'system'])):
#                 fields = list(self.__dict__.keys())
#                 if any([obj.name == field_ for field_ in fields]):
#                     warnings.warn(f"'{obj.name}' is a reserved attribute.  "
#                                   "Skipping directory: {obj} ")
#                     continue
#                     addDirs.append((obj, ofFolder()))
#
#         self.__class__ = make_dataclass('ofCase', addDirs, bases=(self,))

def ofCase(path=Path.cwd()):

    if isinstance(path, Path) is False:
        path = Path(path)

    attrList = [
        ('location', Path, field(default=path.parent)),
        ('name', str, field(default=path.name)),
        ('constant', ofFolder, 
            field(default=FolderParser('constant').makeOFFolder())),
        ('system', ofFolder, 
            field(default=FolderParser('system').makeOFFolder())),
        ('times', ofTimeReg,  field(default=ofTimeReg())),
        ('registry', list, field(default=_populateRegistry(path)))
    ]
    for obj in path.iterdir():
        if (obj.is_dir() and all(obj.name != default for default in
                                 ['constant', 'system'])):
            fields = [attr[0] for attr in attrList]
            if any([obj.name == field for field in fields]):
                warnings.warn(f"'{obj.name}' is a reserved attribute.  "
                              "Skipping directory: {obj} ")
                continue
                attrList.append((obj, ofFolder, field(default=ofFolder(obj))))

    return make_dataclass('ofCase', attrList)(
        path.parent, path.name, ofFolder('constant'),
        ofFolder('system'), ofTimeReg(), _populateRegistry(path))


@dataclass
class ofFolder:
    _path: Path

@dataclass
class _ofDictFileBase:
    #store: dict()
    #update: dict(*args, **kwargs)
    #value: dict = field(default_factory=lambda:{})
    pass

    # def __getitem__(self, key):
    #     return self.store[self._keytransform(key)]
    #
    # def __setitem__(self, key, value):
    #     self.store[self._keytransform(key)] = value
    #
    # def __delitem__(self, key):
    #     del self.store[self._keytransform(key)]
    #
    # def __iter__(self):
    #     return iter(self.store)
    #
    # def __len__(self):
    #     return len(self.store)
    #
    # def _keytransform(self, key):
    #     return key



@dataclass
class _ofDictFileDefaultsBase:
    _name: str = None


@dataclass
class _ofDictBase(dict):
    _name: str = None
    # _value: ofIntBase = None #TODO:  Add value that accepts any type
    _nUnnamed: int = field(init=False, default=0)
    # def __init__(self, _name: str = None,
    #              _nUnnamed: int = field(init=False, default=0),
    #              *iterable):
    #     super().__init__(self.iterable)

    def __post_init__(self):
        #- Store '_name' as an attribute rather than a dict key
        self.__dict__['_name'] = self['_name']
        del self['_name']


    # ref: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    def __getattr__(*args):
        val = dict.get(*args)
        return ofDict(val) if type(val) is dict else val
    def __setitem__(self, item, value=None):
        if isinstance(item, _ofIntBase):  # _ofIntBase is base type for all other ofTypes
            if item.name is None:
                self._nUnnamed += 1
                name_ = '_unnamed'+str(self._nUnnamed)
            if '_unnamed' in item.name or item.name == '_name':
                self._userMsg("Found reserved name in dictionary key.", 'WARNING')
            else:
                name_ = item.name
            return dict.__setitem__(name_, item.value)
        else:
            return dict.__setitem__(item, value)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    _update = dict.update

    
    def update(self, iterable):
        if iterable is None:
            return
        if isinstance(iterable, _ofIntBase):
            self._update({iterable.name: iterable.value})
        else:
            self._update(iterable)
        



@dataclass
class _ofListBase(_ofDictFileBase):
    value: list

    @property
    def valueStr(self):
        str_ = '('
        for v in self.value:
            str_+= str(v)+" "
        return str_.rstrip()+')'

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class _ofNamedListBase(_ofListBase):
    name: str = None
    value: List = field(default_factory=lambda:[])


@dataclass
class _ofIntBase(_ofDictFileBase):
    value: int = None
    name: str = None

    @property
    def valueStr(self):
        return str(self.value)

@dataclass
class _ofFloatBase(_ofIntBase):
    name: str = None
    value: float = None

@dataclass
class _ofStrBase(_ofIntBase):
    name: str = None
    value: str = None

@dataclass
class _ofIncludeBase(_ofDictFileBase):
    _name: str="#include"
    value: str = None

@dataclass
class _ofBoolBase(_ofIntBase):
    name: str = None
    value: None
    _valueStr: str = field(init=False)  #User cant pass a value

    def __post_init__(self):
        self._valueStr = self.value
        self.value = OF_BOOL_VALUES[self._valueStr]

@dataclass
class _ofDimensionedScalarBase(_ofFloatBase):
    dimensions: List = field(default_factory=lambda:[])

@dataclass
class _ofVectorBase:
    #name: field(init=False, repr=False)
    value: List = field(default_factory=lambda:[])


    #- Ensure the value is numeric list of length 3
    @property
    def value(self):
        return self._value

    @property
    def valueStr(self):
        return "("+str(self.value[0])+ \
                " "+str(self.value[1])+ \
                " "+str(self.value[2])+")"

    def __str__(self):
        return self.asString().rstrip(';\n')

    @value.setter
    def value(self, v):
        if isinstance(v, list) is False:
            raise TypeError("Value for 'ofVector' must be a list of length 3.  Got '"+str(v)+"'")
        if (len(v) != 3 or any(isinstance(i, (int, float)) for i in v)
                is False):
            raise Exception("'ofVector' values must be a numeric list of length 3.")
        self._value = v


@dataclass
class _ofVectorDefaultsBase:
    pass
    # name: None=None


@dataclass
class _ofNamedVectorDefaultsBase(_ofFloatBase):
    pass


@dataclass
class ofDictFile(dict, _ofDictFileDefaultsBase, _ofDictFileBase):
    # - TODO: Add ability to read in dictionary entries as python variables
    pass



# def ofDictFile(path):
#
#     attrList = [('_path', Path, field(default=path))]
#     valueList = _readOFDictValues(path)
#
#     for obj in valueList:
#         if obj.name == '_path':
#             warnings.warn(f"'{obj.name}' is a reserved attribute.  "
#                           "Skipping entry.")
#             continue
#         attrList.append(tuple(obj.name, type(obj)))
#
#     return make_dataclass('ofDictFile', attrList)


@dataclass
class ofDict(_ofDictBase):

    def asString(self) -> str:
        if self._name:
            dStr = self._name+"\n{\n"
        else:
            dStr = "{\n"
        for k, v in zip(self.keys(), self.values()):
            log.debug(f"dict entry: {k}: {v}")
            try:
                self.__getattribute__(k)
            except AttributeError: # Do not print dictionary attributes
                #- Handle unnamed values in dicts:
                if '_unnamed' in k:
                    k = '' 
                if isinstance(v, ofDict):
                    dStr2 = v.asString().split("\n")
                    for i in range(len(dStr2)):
                        dStr2[i] = TAB_STR+dStr2[i]+"\n"
                        dStr += dStr2[i]
                elif hasattr(v, 'asString') and callable(getattr(v, 'asString')):
                    dStr += printNameStr(TAB_STR+k)+v.asString()
                else:
                    dStr += printNameStr(TAB_STR+k)+str(v)+"\n"
        dStr+= "}\n"
        return dStr

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofInt(ofDictFile, _ofIntBase):
    def asString(self) -> str:
        return printNameStr(self.name)+str(self.value)+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

TYPE_REGISTRY.append(ofInt)

@dataclass
class ofFloat(ofInt, _ofFloatBase):
    pass

TYPE_REGISTRY.append(ofFloat)

@dataclass
class ofStr(ofInt, _ofStrBase):
    pass

TYPE_REGISTRY.append(ofStr)

@dataclass
class ofBool(ofInt, _ofBoolBase):
    def asString(self) -> str:
        return printNameStr(self.name)+self._valueStr+';\n'

    def __str__(self):
        return self.asString().rstrip(';\n')

TYPE_REGISTRY.append(ofBool)

@dataclass
class ofNamedList(ofDictFile, _ofNamedListBase):

    def asString(self) -> str:
        return printNameStr(self.name)+self.valueStr+";\n"
    #def asString(self) -> str:
    #    valueStr = '('
    #    valueStr += str(self.value[0])
    #    for i in range(1,len(self.value)):
    #        valueStr += ' '+str(self.value[i])
    #    valueStr += ')'
    #    return printNameStr(self.name)+valueStr+";\n"

    def __str__(self):
        return self.asString()

TYPE_REGISTRY.append(ofNamedList)

@dataclass
class ofList(ofDictFile, _ofListBase):

    def asString(self) -> str:
        return self.valueStr
    #def asString(self) -> str:
    #    valueStr = '('
    #    valueStr += str(self.value[0])
    #    for i in range(1,len(self.value)):
    #        valueStr += ' '+str(self.value[i])
    #    valueStr += ')'
    #    return printNameStr(self.name)+valueStr+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

TYPE_REGISTRY.append(ofList)

@dataclass
class ofNamedSplitList(ofNamedList, _ofNamedListBase):
    #- Same as ofNamedList except entries are split on multiple lines according the
    #  OpenFoam Programmer's Style Guide

    def asString(self) -> str:
        printStr = self.name+'\n(\n'
        for v in self.value:
            printStr += TAB_STR+str(v)+'\n'
        printStr += ');\n'
        return printStr

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofDimensionedScalar(ofFloat, _ofDimensionedScalarBase):

    #- Ensure dimensions are a list of length 7 per OpenFOAM convention
    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, d):
        if (len(d) != 7 or any(isinstance(i, int) for i in d) is False):
            raise Exception('Dimensions must be a list of 7 integer values, where each entry corresponds to a base unit type: \
    1:  Mass - kilogram (kg) \
    2:  Length - meter (m) \
    3:  Time - second (s) \
    4:  Temperature - Kelvin (K) \
    5:  Quantity - mole (mol) \
    6:  Current - ampere (A) \
    7:  Luminous intensity - candela (cd)')
        self._dimensions = d

    def asString(self) -> str:
        #- format the dimensions list properly
        dimStr = "["
        for i in range(6):
            dimStr+= str(self.dimensions[i])+' '
        dimStr+= str(self.dimensions[6])+']'

        return printNameStr(self.name)+str(dimStr)+" "+str(self.value)+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofVector(_ofDictFileDefaultsBase, _ofVectorDefaultsBase, _ofVectorBase):
    def asString(self) -> str:
        return self.valueStr
#        return "("+str(self.value[0])+ \
#                " "+str(self.value[1])+ \
#                " "+str(self.value[2])+")"

    def __str__(self):
        return self.asString()

@dataclass
class _ofNamedVectorBase(_ofVectorBase):
    name: str = None

@dataclass
class ofNamedVector(_ofDictFileDefaultsBase, _ofVectorDefaultsBase, _ofNamedVectorBase):


    def asString(self) -> str:
        return printNameStr(self.name)+self.valueStr+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class _ofDimensionedVectorBase(_ofDimensionedScalarBase):
    value: ofVector

@dataclass
class ofDimensionedVector(ofDimensionedScalar, _ofDimensionedVectorBase):

    def asString(self) -> str:
        return printNameStr(self.name)+self.value.asString()+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofInclude(ofDictFile, _ofIncludeBase):
    def asString(self) -> str:
        return printNameStr(self._name)+'"'+str(self.value)+'"\n'

    def __str__(self):
        return self.asString().rstrip('\n')

TYPE_REGISTRY.append(ofInclude)

@dataclass
class ofIncludeEtc(ofInclude):
    _name: str = "#includeEtc"

TYPE_REGISTRY.append(ofIncludeEtc)

@dataclass
class ofIncludeFunc(ofInclude):
    _name: str = "#includeFunc"

TYPE_REGISTRY.append(ofIncludeFunc)


class DictFileParser:
    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            self.lines = f.readlines()
        self.status = None
        self.entryList = []
        self.i=0


    def readDictFile(self):

        status = 'start'
        ofType = None
        prevLine = None
        lineStatus = 'read'
        level = 0

        self.i = self._findEndOfHeader()

        attempts = 0
        while True:
            attempts += 1
            log.debug(f"Parsing line {self.i+1} of file {self.filepath}")
            if attempts > 1000:
                log.error("Error reading dictionary file.  Maximum lines exceeded")
                sys.exit()
            if self.i >= len(self.lines):
                break

            value = self._parseLine()

            if value is not None:
                self.entryList.append(value)

            # [status, lineStatus] = _readDictEntry(status, ofType, lines, i)

        return ofDictFile(self.entryList
                        #location=Path(file).parent, 
                        #filename=Path(file).name
                        )

    def _userMsg(self, msg, level = "INFO"):
        """
        Write message to console or stdout for the usre (i.e. without code details)
        
        Parameters:
            msg [str]:  The message to print
            
            level [str]: Either "INFO", "WARNING" or "ERROR".  If "ERROR", scroipt is
            terminated.
        """

        printStyle = {
            "INFO": 'blue',
            "WARNING": "bold orange",
            "ERROR": "bold red"
        }

        console.print(f'\n[{printStyle[level]}]{level}:[/{printStyle[level]}]'
        f' {msg}\n')
        if level == 'ERROR':
            sys.exit()

        # with open(file, 'r') as f:
        #     lines = f.readlines()
        #     for i, line in enumerate(lines):
        #         if line.startswith(('//', '#')):
        #             #- Ignore line comments and includes
        #             continue
        #         if lineStatus == 'endMultiLine':
        #             #- Determine how to interpret the previous line
        #             [status, lineStatus] = _getOFDictMultiLinePreviousType(line)
        #         lineStatus = 'read'
        #         count = 0
        #         while lineStatus != 'end':
        #             if lineStatus == 'endMultiLine':
        #                 prevLine = line
        #                 break
        #             count += 1
        #             if count >= 100: #prevent infinite loop in case of error
        #                 raise Exception("Maximum number of loops reached.")
        #             #func = functionSwitcher(status)
        #             # if func is not None
        #                 #[status, lineStatus] = func(_argSwitcher(func, line, ofType))
        #             [status, lineStatus] = _readDictEntry(
        #                                         status, ofType, lines, i
        #                                     )


    # def readDictFile(self):
    #     """
    #     Reads an OpenFOAM dictionary file and stores values in a python dictionary.
    #     """
    #     #from of.ofTypes import ofDictFile, ofDict, ofNamedList, ofIntValue, ofFloatValue, ofStrValue

    #     #- Function assumes:
    #     #   - All entries start on a new line
    #     #   - Comments on line after C++ code are ignored

    #     #pyOFDict = ofDictFile(os.path.basename(file), [])

    #     if not isOFDict(self.filepath):
    #         raise Exception("File is not a valid OpenFOAM dictionary file:"
    #                         f"\n{self.filepath}")

    #     def functionSwitcher(status):
    #         switcher = {
    #             'commentedBlock': _getOFDictCommentLineType,
    #             'comment': None,
    #             'includeLine': None,
    #             'empty': None,
    #             'commentedBlockEnd':  _parseLine,
    #             'list': _getOFDictValueType,
    #             'dict': _getOFDictValueType,
    #             'value': _storeOFDictValue,
    #             'multiLineUnknown': _getOFDictEntryType,
    #             'dictName': _newOFDictDict,
    #             'listName': _newOFDictList,
    #             'multiLineValue': _appendOFDictEntry,
    #             'multiLineEntryStart': _storeOFDictMultiLineEntryName,
    #             'singleLineSingleValuedEntry': _storeOFDictSingleLineSingleValuedEntry
    #         }
    #         return switcher.get(status, _parseLine)

    #     status = {
    #         'inBlockComment': False,
    #         'inDict': 0,
    #         'inList': 0,
    #         'multiLineEntryStart': False
    #     }

    #     pyDict = {}

    #     # - Parse the file line by line for data
    #     with open(file) as f:
    #         lines = f.readlines()
    #         for line in lines:
    #             line = line.lstrip().rstrip()
    #             if status['inBlockComment']:
    #                 if line.rstrip()[-2:] == '*/':
    #                     status['inBlockComment'] = False
    #                 continue
    #             if status['inList']:
    #                 pass
    #             if status['inDict']:
    #                 pass
    #             if status['multiLineEntryStart']:
    #                 pass
    #             # - Check for block comment
    #             if line[:1] == '/*':
    #                 status['inBlockComment'] = True
    #                 continue
    #             # - Check for line comment
    #             if line[:1] == '//':
    #                 continue
    #             # - Check for include statement
    #             if line.startwith('#includeEtc'):
    #                 pyDict.update

    #             # - Check for single line entry
    #             # - Check for multi-line entry


    # def _readDictEntry(self):

    #     #- Function assumes:
    #     #   - All entries start on a new line
    #     #   - Comments on line after C++ code are ignored

    #     #pyOFDict = ofDictFile(os.path.basename(file), [])

    #     def functionSwitcher(status):
    #         switcher = {
    #             'commentedBlock': _getOFDictCommentLineType,
    #             'comment': None,
    #             'includeLine': _storeInclude,
    #             'empty': None,
    #             'commentedBlockEnd':  _parseLine,
    #             'list': _getOFDictValueType,
    #             'dict': _getOFDictValueType,
    #             'value': _storeOFDictValue,
    #             'multiLineUnknown': _getOFDictValueType,
    #             'startDict': _readDictEntry, # _newOFDictDict,
    #             'startList': _readList, # _newOFDictList,
    #             'multiLineValue': _appendOFDictEntry,
    #             'multiLineEntryStart': _storeOFDictMultiLineEntryName,
    #             'singleLineSingleValuedEntry': _storeOFDictSingleLineSingleValuedEntry
    #         }
    #         return switcher.get(status, _parseLine)

    #     def _argSwitcher(func, line, ofType):
    #         switcher = {
    #             _parseLine: len(line.split(" ")),
    #             _storeOFDictValue: (ofType,
    #                                 line[1:].remove('{()}').split(" ")
    #                             )
    #         }
    #         return switcher.get(func, line.remove['()'])

    #     attempts = 0
    #     while status != 'endDict':
    #         attempts +=1
    #         if attempts > 1000:
    #             log.error("Error reading dictionary file.  Maximum lines exceeded")
    #             sys.exit()

    #         func = functionSwitcher(status)
    #         [status, lineStatus] = func(_argSwitcher(func, lines[i], ofType))

    #         i += 1



    

    def _getLinesList(self, i):
        """
        Parse an OpenFOAM dictionary file to the end of a C++ statement 
        (i.e. to the `statementEnd` value.) .  Assumes there are no `#include` statements in the 
        range of lines.

        Parameters:
            lines [list(str)]:  List of lines of the dictionary file as text
            obtained from the `open()` command.
            i [int]: index of the line currently being parsed

        Returns:
            linesList [list(str)]:  List of individuals entries (space delimited)
            for the current C++ statement.
            i [int]: index of the current line after parsing the statement 

        """
        
        linesList = []
        line = self.lines[self.i]
        # Pass first opening bracket character ('(' or '{')
        if any([line[0] == char for char in ['(', '{']]):
            line = line[1:]
        attempts = 0
        while ';' not in line:
            if attempts > 1000:
                log.error('Maximumum number of attempts')
                sys.exit()
            for item in line.split():
                linesList.append(item)
            self.i+=1
            line = self.lines[self.i]
        #parse last line; remove statement end from list:
        for item in self.lines[self.i][:-1].split():
            linesList.append(item)
        return linesList


    def _getOFDictCommentLineType(self, startsWith):
        switcher = {
            '*/': ['commentedBlockEnd', 'end']
        }
        return [switcher.get(startsWith, 'commentedBlock'), 'end']


    def _getOFDictValueType(self, startsWith):
        switcher = {
            '(': 'list',
            '{': 'dict'
        }
        return [switcher.get(startsWith, 'value'), 'read']


    def _getOFDictMultiLineEntryType(self, line):
        switcher = {
            '(': 'list',
            '{': 'dict',
            'FoamFile': 'fileInfoStart'
        }
        return [switcher.get(line, 'value'), 'read']


    def _ofMultiLineEntryReadNextLine(self, line):
        pass



    def _parseListOrDict(self, name):
        """
        Parse a list or dictionary with name `name`, starting from the opening 
        parenthesis `(` in the case of a list or opening bracket '{' in the case of 
        a dict

        Parameters:
            name [str or None]:  The name of the list or dict;  None if an unnamed 
            value.

            lines [list(str)]:  The dictionary file read in as a list of lines.

            i [int]:  The `lines` index currently being parsed 

        Returns:
            value [ofList or ofDict]:  The value of the list or dict items to 
            be added.  

        """

        #linesList = self._getLinesList(self.lines[self.i])

        name = name.strip()

        line = self.lines[self.i]

        log.debug(f"lines[i]: {line}")

        if line.startswith('('):
            linesList = self._getLinesList[self.lines[self.i]]
            # - Parse the list recursively to capture list of lists
            value = self._parseList(name)
        elif line.startswith('{'):
            #value = { name: None }
            # - Parse the dictionary recursively to capture dict of dicts
            self.i += 1
            log.debug(f"Parsing {name} dictionary.")
            value = ofDict(self._parseDict(name))
        else:
            self._userMsg(f"Invalid syntax on line {self.i+1} of dictionary "
            f"file '{self.filepath}'.", level='ERROR')
            # log.error(f"Invalid syntax on line {self.i+1} of dictionary "
            # f"file '{self.filepath}'.")
            # sys.exit()

        self.i += 1

        return value

    def _parseList(self, name, list_):
        pass

    def _parseDict(self, name):
        """
        Recursive parse a dictionary storing values as ofDict 
        """
        # - Find the end of dictionary        
        i_end = self._findDictOrListEnd('dict')

        log.debug(f"name: {name}")

        dict_ = ofDict(_name=name)

        while self.i < i_end:
            dict_.update(self._parseLine())

        log.debug(f"dict_:\n{dict_}")

        return dict_

    def _findDictOrListEnd(self, type):
        """
        Find the line that terminates the dictionary starting on the currently
        parsed line (i.e. the `self.i'th line)

        Parameters:
            type [str]:  The type of object to parse (either 'dict' or 'list')

        Returns:
            i [int]:  The line on which the current list or dictionary ends.
        """

        searchChar = {
            'dict': ['{', '}'],
            'list': ['(', ')']
        }

        level = 0

        i_ = self.i

        while level >= 0:
            if i_ >= len(self.lines):
                self._userError(f'Invalid syntax in dictionary {dict}. '
                f'Could not locate end of {type}.')
            line = self.lines[i_]
            for char in line:
                if char == searchChar[type][0]:
                    level += 1
                if char == searchChar[type][1]:
                    level -= 1 
            i_+=1

        log.debug(f"Found {type} entry from lines {self.i} to {i_}.")

        return i_
            


    # TODO: Handle case of multiLineEntry with more than 1 word on  first line.
    def _parseLine(self):
        # switcher = {
        #     "parse": ,
        #     : ['multiLineUnknown', 'readMultiLine'],
        #     2: ['singleLineSingleValuedEntry', 'read']
        # }

        lineList = self.lines[self.i].split()

        log.debug(f"lineList: {lineList}")

        try: 
            if len(lineList) == 0:
                # Line is blank
                return None
            elif len(lineList) == 1:
                listOrDictName = self.lines[self.i].lstrip(" ").rstrip(" ")
                if any([listOrDictName is char for char in ['(', '{']]):
                    return self._parseListOrDict(None)
                else:
                    self.i += 1
                    return self._parseListOrDict(listOrDictName)
            elif len(lineList) == 2:
                return self._parseLineLenTwo()
            else:  # Multiple value entry
                return self._parseLineLenGreaterThanTwo()
        except Exception as e:
            raise e
        finally:
            self.i += 1



    def _parseLineLenTwo(self):
        log.debug("Parsing line of length 2.")

        lineList = self.lines[self.i].split()
        
        log.debug(f"lineList: {lineList}")
        
        try:
            if lineList[0].startswith('#include'):
                # Found include statement 
                return self._parseIncludes(lineList[0], lineList[1].rstrip(';'))
            elif lineList[1][-1] == ';':
                # Found single line entry
                return self._parseSingleLineEntry(lineList[0], 
                    lineList[1].rstrip(';'))
            else:
                log.error(f"Cannot handle single line entry '{lineList}'")
        except Exception as e:
            raise e
        finally:
            self.i+=1


    def _parseIncludes(self, key, value):
        """
        Extract value as the appropriate include type
        """

        if key == '#includeEtc':
            return ofIncludeEtc(value)
        elif key == '#includeFunc':
            return ofIncludeFunc(value)
        else:
            return ofInclude(value)


    def _parseSingleLineEntry(self, key, value):
        """
        Extract the value as the approriate ofTypes

        Search order:
            - ofFloat, ofInt, ofBool, ofStr
        """

        log.debug("Parsing a single line entry")

        log.debug(f"key: {key}, value: {value}")

        try:
            v_ = float(value)
            return ofFloat(v_, name=key)
        except ValueError:
            pass
        try:
            v_ = int(value)
            return ofInt(v_, name=key)
        except ValueError:
            pass
        if any([value == b for b in OF_BOOL_VALUES.keys()]):
            return ofBool(name=key, value=value)
        else:
            return ofStr(value, name=key)

    def _parseLineLenGreaterThanTwo(self):

        line = self.lines[self.i]
        entryName = None

        lineList = line.split(" ")

        # - find the entry type
        for i, char in enumerate(line):
            if char == '{' or char == '(':
                entryName = line[:i].lstrip().rstrip()
                valueList = line[i:].split(" ").rstrip(char+';')
                break

        if entryName:
            self._parseListOrDict(entryName)
        else:
            log.error(f"Invalid syntax found on line {self.i} of file "
            f"{self.filepath}")



    # def _storeOFDictValue(line):
    #     pass


    # def _appendOFDictEntry(line):
    #     pass


    # def _storeOFNamedListValue(line):
    #     pass


    # def _getMultiLineType(line):
    #     switcher = {
    #         '{': 'startDict',
    #         '(': 'startList'

    #     }

    #     typeSwitcher = {
    #         '{': ofDict(),
    #         '(': ofNamedList()
    #     }

    #     self.entryList[self.entryList.keys[-1]] = typeSwitcher.get(line)

    #     return [switcher.get(line, 'multiLineValue'), 'read']


    # def _storeOFDictSingleLineSingleValuedEntry(line):
    #     values = line.split(" ")
    #     if len(values) != 2:
    #         raise Exception("Not able to process line format.")
    #     if values[1].isnumeric() is True:
    #         if '.' in values[1]:
    #             pyOFDict.add(ofFloatValue(values[0], values[1]))
    #         else:
    #             pyOFDict.add(ofIntValue(values[0], values[1]))
    #     elif values[1] in OF_BOOL_VALUES:
    #         pyOFDict.add(ofBoolValue(values[0], values[1]))
    #     else:
    #         pyOFDict.add(ofStrValue(values[0], values[1]))

    #     return ['newLine', 'end']

    # def _storeOFDictMultiLineEntryName(line):
    #     _currentEntryKey = line
    #     self.entryList.update({line: None})

    # def _ofDictFindBlockEntryStartStop(file, blockList, searchValues=False):
    #     #TODO:  Account for the case of opening and closing parenthesis or brackets
    #     #  on the same line.
    #     relPath = file
    #     file = os.path.join(os.getcwd(), file)

    #     if os.path.isfile(file) is False:
    #         raise FileNotFoundError(file)

    #     copyfile(file, file+"_old")

    #     start = 0
    #     stop = 0

    #     try:
    #         old = open(file, 'r')
    #         for line in old:
    #             stop+=1
    #         old.seek(0)
    #         lines = old.readlines()

    #         if stop <= 0:
    #             raise Exception('File is empty: '+file)

    #         if blockList is not None:

    #             for block in blockList:
    #                 #- initialize variables to be defined below
    #                 openStr = None
    #                 closeStr = None

    #                 #old.seek(start-1)

    #                 # while 'block' is not the first word in the line:
    #                 while True:
    #                     lineList = lines[start].strip().split(" ")
    #                     if block == lineList[0]:
    #                         break
    #                     start += 1
    #                     if start >= stop:
    #                         log.warning("End of file '"+relPath+"' reached "\
    #                                 "without finding a match for block '"+\
    #                                 str(block)+"'.")
    #                         return None, stop-1
    #                 for i in [0,1]: #search line with block name and next line
    #                     if len(lines[start+i].split(" ")) > 1:
    #                         #- Search for opening and closing of block on the same line
    #                         for openChar, closeChar in zip(['(', '{'],[')', '}']):
    #                             if openChar in lines[start+i]:
    #                                 openStr = openChar
    #                                 closeStr = closeChar
    #                                 start = start+i
    #                                 break
    # #                                if closeStr in lines[start+i]:
    # #                                    print("Warning:  No values found matching block '"+block+"' within "+file)
    #                 #- If block is not opened on same line assume it is opened on next
    #                 #  line:
    #                 if not openStr:
    #                     start+=1
    #                     openStr = lines[start].lstrip()[0]

    #                 if openStr == '(':
    #                     closeStr = ')'
    #                 elif openStr == '{':
    #                     closeStr = '}'
    #                 else:
    #                     raise Exception("Unexpected file format enountered at line "+str(start+1)+" of "+file)
    #                 stop = start

    #                 nOpenStr = 1
    #                 nCloseStr = 0

    #                 while nOpenStr > nCloseStr:
    #                     if stop >= len(lines)-1:
    #                         raise Exception("End of file '"+relPath+"' reached without terminating block.")
    #                     stop+=1
    #                     nOpenStr+= lines[stop].count(openStr)
    #                     nCloseStr+= lines[stop].count(closeStr)
    #             start+=1
    #         else:  #Search top level.  Find end of file
    #             if len(lines) > 0:
    #                 start = len(lines)-1
    #                 stop = len(lines)-1
    #             else:
    #                 start = 0
    #                 stop = 0

    #     except:
    #         copyfile(file+"_old", file)
    #         raise

    #     return start, stop

    def _findEndOfDict(self):
        """
        Returns the line number of an OpenFOAM dictionary corresponding to the
        whitespace after the last entry of the root dictionary.
        """
        #- TODO: Handle the case where a subdict of an existing dictionary is
        #  not found.

        endofDict = None

        lines = self.lines
        nLines = len(lines)
        for i, line in enumerate(reversed(lines)):
            #TODO:  This does not properly handle commented blocks at end of
            #       file.
            if (len(line.strip()) > 0 and
                any([line.lstrip()[:2] == c for c in ['//', '/*']]) is False):
                    endOfDict = nLines - i
                    break
        if endOfDict is None:
            endOfDict = self._findEndOfHeader()

        log.debug('endofDict: '+str(endOfDict))

        return endOfDict

    def _findEndOfHeader(self):
        foamFileFound = False
        with open(self.filepath) as f:
            for i, line in enumerate(f.readlines()):
                if line.strip() == 'FoamFile':
                    foamFileFound = True
                if (foamFileFound and
                    (line[:6] == '*\\----' or
                    line[:6] == '// * *')):
                    return i+1

        log.error('Invalid OpenFOAM file specified: '+str(file))
        sys.exit()
