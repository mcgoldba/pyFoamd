from dataclasses import dataclass, field, make_dataclass
from signal import valid_signals
from typing import List, Dict
import operator
from collections.abc import MutableMapping
import copy
from pathlib import Path
import warnings
import sys
import string #- to check for whitespace
import re
import pandas as pd

from inspect import signature #- just for debugging

from ._isOFDict import _isOFDict
#from ._readDictFile import _readDictFile

from rich.console import Console
console = Console()

import logging

# log = logging.getLogger('pyfoamd')

#from pyfoamd.richLogger import logger
logger = logging.getLogger('pf')

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

BRACKET_CHARS = {
    'dict': ['{', '}'],
    'list': ['(', ')']
}

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
                attrList.append((name_, _ofFolderBase, 
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

        logger.debug(f"ofFolder dataclass: {dc_}")
        logger.debug(f"ofFolder dataclass: {signature(dc_)}")

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
        ('constant', _ofFolderBase, 
            field(default=FolderParser('constant').makeOFFolder())),
        ('system', _ofFolderBase, 
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
        path.parent, path.name, FolderParser('constant').makeOFFolder(),
        FolderParser('system').makeOFFolder(), 
        ofTimeReg(), _populateRegistry(path))


@dataclass
class _ofFolderBase:
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


#TODO: Common functionality for all ofTypes (e.g. print str as OpenFOAM entry)
@dataclass
class _ofTypeBase:
    """Common derived class to group all ofTypes"""
    pass

@dataclass 
class _ofUnnamedTypeBase(_ofTypeBase):
    """
    Base class for unnamed values.  'value' should be stored as a Python type.
    For derived classes where the conversion from python type back to the ofType
    is not intuitive, a secondary '_value' attribute should be defined that
    stores the appropriate string repesentation of the OpenFOAM value.
    
    Iterable derived types (e.g. ofList) should store ofTypes as values.

    """
    value : str = None

@dataclass 
class _ofNamedTypeBase(_ofUnnamedTypeBase):
    """
    Base class for named values.  'value' should be stored as a Python type.
    For derived classes where the conversion from python type back to the ofType
    is not intuitive, a secondary '_value' attribute should be defined that
    stores the appropriate string repesentation of the OpenFOAM value.

    Iterable derived types (e.g. ofDict) should store ofTypes as values.

    call signatures:
        with single argument:   _ofNamedTypeBase(value)
        with two arguments:     _ofNamedTypeBase(name, value)

    """
    name: str = None
    # value : str = None

    def __post_init__(self, *args, **kwargs):
        if len(args) == 1:
            self.value = args[0]
            self.name = None
        elif len(args) == 2:
            self.name = args[0]
            self.name = args[1]


#TODO: Eliminate this class
@dataclass
class _ofDictFileDefaultsBase:
    _name: str = None


# @dataclass
# class _ofDictBase(dict):
#     #_name: str = None
#     # _value: ofIntBase = None #TODO:  Add value that accepts any type
#     # _nUnnamed: int = field(init=False, default=0)
#     # _entryTypes: Dict = field(init=False, default_factory=lambda:{})

#     # def __post_init__(self, *args, **kwargs):
#     #     #- Store '_name' as an attribute rather than a dict key
#     #     logger.debug(f"_name: {self['_name']}")
#     #     self.__dict__['_name'] = self['_name']
#     #     del self['_name']

#     #- ref: https://stackoverflow.com/a/27472354/10592330
#     def __init__(self, *args, **kwargs):
#         self._name = kwargs.pop('_name', None)
#         self._entryTypes = {}
#         self._nUnnamed = 0

#         super().__init__(*args, **kwargs)


#     # ref: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
#     def __getattr__(*args):
#         val = dict.get(*args)
#         return ofDict(val) if type(val) is dict else val
#     def __setitem__(self, item, value=None):
#         nameTag = None
#         logger.debug(f'__setitem__.item: {item}')
#         if isinstance(item, _ofIntBase):  # _ofIntBase is base type for all other ofTypes
#             nameTag = 'name'
#         elif isinstance(item, _ofDictBase):
#             nameTag = '_name'

#         logger.debug(f"nameTag: {nameTag}")
        
#         if nameTag is not None:
#             itemName = item.__getattr__[nameTag]
#             if itemName is None:
#                 self._nUnnamed += 1
#                 name_ = '_unnamed'+str(self._nUnnamed)
#             if '_unnamed' in itemName or itemName == '_name':
#                 self._userMsg("Found reserved name in dictionary key.", 'WARNING')
#             else:
#                 name_ = item.name
#             return dict.__setitem__(name_, item.value)
#         else:
#             return dict.__setitem__(item, value)

#     __setattr__ = dict.__setitem__
#     __delattr__ = dict.__delitem__

#     _update = dict.update

    
#     def update(self, iterable):
#         if iterable is None:
#             return
#         if isinstance(iterable, _ofIntBase):
#             self._update({iterable.name: iterable.value})
#             # self._entryTypes[iterable.name] = type(iterable)
#         elif isinstance(iterable, _ofDictBase):
#             logger.debug(f"ofDict._name: {iterable._name}")
#             self._update({iterable._name: iterable.__dict__})
#             # self._entryTypes[iterable.name] = type(iterable)
#         else:
#             self._update(iterable)
        

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

    def __list__(self):
        _list = []
        return [v.value if isinstance(v, _ofIntBase) else v for v in self.value]

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
class ofWord(_ofUnnamedTypeBase):
    """
    An OpenFOAM word is a specialization of a string with no whitespace,
    quotes, slashes, semicolons, or brace brackets
    """
    value : str

    def __post_init__(self):
        FORBIDDEN_VALUES = ['"', "'", '\\', '/', ";", '{', '}']
        if (any([fv in self.value for fv in FORBIDDEN_VALUES])
            or any([c in self.value for c in string.whitespace])):
            raise ValueError("String cannot be converted to a word.")

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
class ofDict(dict, _ofTypeBase):

   #- ref: https://stackoverflow.com/a/27472354/10592330
    def __init__(self, *args, **kwargs):
        self._name = kwargs.pop('_name', None)
        self._entryTypes = {}
        self._nUnnamed = 0
        #- Keep a list of class variables to filter printed dict items:
        self.CLASS_VARS = ['CLASS_VARS', '_name', 
                            '_entryTypes', '_nUnnamed']

        if (len(args) == 1 and isinstance(args[0], list)
            and  all([isinstance(v, _ofTypeBase) for v in args[0]])):
            #- Parse list of ofTypes with ofDict().update function
            super().__init__(**kwargs)
            self.update(args[0])
        else:
            super().__init__(*args, **kwargs)


    # ref: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    def __getattr__(*args):
        val = dict.get(*args)
        return ofDict(val) if type(val) is dict else val
    def __setitem__(self, item, value=None):
        nameTag = None
        if isinstance(item, _ofIntBase):  # _ofIntBase is base type for all other ofTypes
            nameTag = 'name'
        elif isinstance(item, ofDict):
            nameTag = '_name'
        
        if nameTag is not None:
            itemName = item.__getattr__[nameTag]
            if itemName is None:
                self._nUnnamed += 1
                name_ = '_unnamed'+str(self._nUnnamed)
            if '_unnamed' in itemName or itemName == '_name':
                self._userMsg("Found reserved name in dictionary key.", 'WARNING')
            else:
                name_ = item.name
            return dict.__setitem__(name_, item.value)
        else:
            return dict.__setitem__(item, value)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    _update = dict.update

    def _NoneKey(self):
        self._nUnnamed += 1
        return '_unnamed'+str(self._nUnnamed)
    
    def update(self, iterable):
        # logger.debug(f"ofDict initalizer iterable type: {type(iterable)}")
        if iterable is None:
            return
        if (isinstance(iterable, _ofIntBase) 
            or isinstance(iterable, _ofNamedTypeBase)):
            self._update({iterable.name: iterable.value})
        elif isinstance(iterable, _ofUnnamedTypeBase):
            self._update({self._NoneKey(): iterable.value})
        elif isinstance(iterable, list):
            listTypes = set([type(item) for item in iterable])
            if all([isinstance(v, _ofTypeBase) for v in iterable]):
                # dict_ = {item.name: item for item in iterable}
                for item in iterable:
                    self.update(item)
        elif isinstance(iterable, ofDict):
            self._update({iterable._name: iterable.__dict__})
            # self._entryTypes[iterable.name] = type(iterable)
        else:
            self._update(iterable)

    def asString(self) -> str:
        if self._name:
            dStr = self._name+"\n{\n"
        else:
            dStr = "{\n"
        for k, v in zip(self.keys(), self.values()):
            logger.debug(f"dict entry: {k}: {v}")
            if k is None:
                k=''
            try:
                self.__getattribute__(k)
            except AttributeError: # Do not print dictionary attributes
                if any([k == v for v in self.CLASS_VARS]):
                    continue # do not print class varibales
                #- Handle unnamed values in dicts:
                # if '_unnamed' in k:
                #     k = '' 
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
class ofDictFile(ofDict):
    # - TODO: Add ability to read in dictionary entries as python variables

    def __init__(self, *args, **kwargs):
        self._location = Path(kwargs.pop('_location', Path.cwd()))

        super().__init__(*args, **kwargs)
        self.CLASS_VARS.append('_location')

@dataclass
# class ofInt(_ofDictFileBase, _ofIntBase):
class ofInt(_ofNamedTypeBase):
    def asString(self) -> str:
        return printNameStr(self.name)+str(self.value)+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

TYPE_REGISTRY.append(ofInt)

@dataclass
class ofFloat(_ofNamedTypeBase):
    value: float

TYPE_REGISTRY.append(ofFloat)

@dataclass
class ofStr(_ofNamedTypeBase):
    pass

TYPE_REGISTRY.append(ofStr)

@dataclass
class ofBool(ofInt, _ofBoolBase):
    def asString(self) -> str:
        return printNameStr(self.name)+self._valueStr+';\n'

    def __str__(self):
        return self.asString().rstrip(';\n')

TYPE_REGISTRY.append(ofBool)

#TODO:  Add abilty to get value based on variable name
@dataclass
class ofVar(_ofNamedTypeBase):
    
    def asString(self) -> str:
        return f"${self.value};\n"


    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofNamedList(ofDictFile, _ofNamedListBase):

    def asString(self) -> str:
        return printNameStr(self.name)+self.valueStr+";\n"
    
    def asString(self) -> str:
        if self.name:
            dStr = self.name+"( "
        else:
            dStr = "( "
        for v in self.value:
            if isinstance(v, ofDict):
                dStr2 = v.asString().split(" ")
                for i in range(len(dStr2)):
                    dStr2[i] = TAB_STR+dStr2[i]+" "
                    dStr += dStr2[i]
            elif hasattr(v, 'asString') and callable(getattr(v, 'asString')):
                dStr += v.asString()
            else:
                dStr += str(v)+" "
        dStr+= ")\n"
        return dStr


    def __str__(self):
        return self.asString()

TYPE_REGISTRY.append(ofNamedList)

@dataclass
class ofList(ofDictFile, _ofListBase):

    def asString(self) -> str:
        dStr = "( "
        for v in self.value:
            if isinstance(v, ofDict):
                dStr2 = v.asString().split(" ")
                for i in range(len(dStr2)):
                    dStr2[i] = TAB_STR+dStr2[i]+" "
                    dStr += dStr2[i]
            elif hasattr(v, 'asString') and callable(getattr(v, 'asString')):
                dStr += v.asString()
            else:
                dStr += str(v)+" "
        dStr+= ") "
        return dStr
    # def asString(self) -> str:
    #     return self.valueStr
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
class ofTable(ofNamedList):

    _value = None

    @property
    def value(self):
        return self.value

    @value.setter
    def value(self, val):
        """Convert varoius input types to pd.Dataframe"""

        if isinstance(val, str):
            logger.debug("Found string input.")
            list_ = DictFileParser()._parseListValues(v)
        elif isinstance(val, _ofListBase):
            logger.debug("Found ofList input.")
            list_ = list(val)
        elif isinstance(val, list):
            logger.debug("Found list input.")
            list_ = [v.value if isinstance(v, _ofIntBase) else v \
                for v in val]
        else:
            logger.error("Unhandled type provided for 'value'.")
            
        logger.debug(f"list_: {list_}.")
        #- check that value is a list of lists of equal length
        if (len(list_) == 1 and isinstance(list_[0], list) 
            and all([isinstance(l, list) for l in list_[0]])
            and all([len(list_[0][0]) == len(l) for l in list_[0][1:]])):
            
            table_ = pd.DataFrame()

            if len(list_[0]) > 1:
                if isinstance(list_[0][1], list): # if '(0.0 (1 2 3))' format
                    for item in list_:
                        df_ = pd.DataFrame(item[1], index=[item[0]])
                        pd.concat([table_, df_])
                else:  # '(0.0 1 2 3)' format
                    for item in list_:
                        df_ = pd.DataFrame(item[1:], index=[item[0]])
                        pd.concat([table_, df_])

            else:
                raise Exception("Invalid list formatting for table.")                
        else:
            raise Exception("Invalid list formatting for table.")



    def asString(self) -> str:
        dStr = "( "
        for v in self.value:
            if isinstance(v, ofDict):
                dStr2 = v.asString().split(" ")
                for i in range(len(dStr2)):
                    dStr2[i] = TAB_STR+dStr2[i]+" "
                    dStr += dStr2[i]
            elif hasattr(v, 'asString') and callable(getattr(v, 'asString')):
                dStr += v.asString()
            else:
                dStr += str(v)+" "
        dStr+= ") "
        return dStr
    # def asString(self) -> str:
    #     return self.valueStr
    #def asString(self) -> str:
    #    valueStr = '('
    #    valueStr += str(self.value[0])
    #    for i in range(1,len(self.value)):
    #        valueStr += ' '+str(self.value[i])
    #    valueStr += ')'
    #    return printNameStr(self.name)+valueStr+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

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
class ofDimension():
    
    dimensions: List = field(default_factory=lambda:[])

    #- Ensure dimensions are a list of length 7 per OpenFOAM convention
    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, d):
        if not isinstance(d, list):
            d = [0, 0, 0, 0, 0, 0, 0]
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

        return str(dimStr)

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofDimensionedScalar(ofFloat, ofDimension):

    #- Ensure dimensions are a list of length 7 per OpenFOAM convention
    # @property
    # def dimensions(self):
    #     return self._dimensions

    # @dimensions.setter
    # def dimensions(self, d):
    #     if (len(d) != 7 or any(isinstance(i, int) for i in d) is False):
    #         raise Exception('Dimensions must be a list of 7 integer values, where each entry corresponds to a base unit type: \
    # 1:  Mass - kilogram (kg) \
    # 2:  Length - meter (m) \
    # 3:  Time - second (s) \
    # 4:  Temperature - Kelvin (K) \
    # 5:  Quantity - mole (mol) \
    # 6:  Current - ampere (A) \
    # 7:  Luminous intensity - candela (cd)')
    #     self._dimensions = d

    def asString(self) -> str:
        # #- format the dimensions list properly
        # dimStr = "["
        # for i in range(6):
        #     dimStr+= str(self.dimensions[i])+' '
        # dimStr+= str(self.dimensions[6])+']'

        return printNameStr(self.name)+str(self.dimensions)+" "+str(self.value)+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofSphericalTensor(_ofVectorBase):
    
    #- Ensure the value is numeric list of length 3
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if isinstance(v, list) is False:
            raise TypeError("Value for 'ofVector' must be a list of length 3.  Got '"+str(v)+"'")
        if (len(v) != 1 or any(isinstance(i, (int, float)) for i in v)
                is False):
            raise Exception("'ofSphericalTensor' values must be a numeric list of length 1.")
        self._value = v

@dataclass
class ofSymmTensor(_ofVectorBase):
    """
    A symmetric tensor, defined by components '(xx xy xz yy yz zz)'
    """
    
    #- Ensure the value is numeric list of length 3
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if isinstance(v, list) is False:
            raise TypeError("Value for 'ofVector' must be a list of length 3.  Got '"+str(v)+"'")
        if (len(v) != 6 or any(isinstance(i, (int, float)) for i in v)
                is False):
            raise Exception("'ofSymmTensor' values must be a numeric list of length 6.")
        self._value = v

@dataclass
class ofTensor(_ofVectorBase):
    """
    A symmetric tensor, defined by components '(xx xy xz yy yz zz)'
    """
    
    #- Ensure the value is numeric list of length 3
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if isinstance(v, list) is False:
            raise TypeError("Value for 'ofVector' must be a list of length 3.  Got '"+str(v)+"'")
        if (len(v) != 9 or any(isinstance(i, (int, float)) for i in v)
                is False):
            raise Exception("'ofTensor' values must be a numeric list of length 9.")
        self._value = v

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
class ofDimensionedSphericalTensor(ofSphericalTensor, ofDimension):
    name : str = None

    def asString(self) -> str:
        return printNameStr(self.name)+self.dimensions+\
            self.value.asString()+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofDimensionedSymmTensor(ofSymmTensor, ofDimension):
    name : str = None

    def asString(self) -> str:
        return printNameStr(self.name)+self.dimensions+\
            self.value.asString()+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

@dataclass
class ofDimensionedTensor(ofTensor, ofDimension):
    name : str = None

    def asString(self) -> str:
        return printNameStr(self.name)+self.dimensions+\
            self.value.asString()+";\n"

    def __str__(self):
        return self.asString().rstrip(';\n')

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
        self.extraLine = None


    def _addExtraLine(self, line):
        if self.extraLine is not None:
            logger.error("Unhandled sequence.  Found multiple extra lines")
            raise Exception
        else:
            self.extraLine = line
    

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
                logger.error('Maximumum number of attempts')
                sys.exit()
            for item in line.split():
                linesList.append(item)
            self.i+=1
            line = self.lines[self.i]
        #parse last line; remove statement end from list:
        for item in self.lines[self.i][:-1].split():
            linesList.append(item)
        return linesList

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
            logger.debug(f"Parsing line {self.i+1} of file {self.filepath}")
            if attempts > 1000:
                logger.error("Error reading dictionary file.  Maximum lines exceeded")
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

    # TODO: Handle case of multiLineEntry with more than 1 word on  first line.
    def _parseLine(self):
        # switcher = {
        #     "parse": ,
        #     : ['multiLineUnknown', 'readMultiLine'],
        #     2: ['singleLineSingleValuedEntry', 'read']
        # }

        logger.debug("Parsing new line.")
        logger.debug(f"\tself.extraLine: {self.extraLine}")

        logger.debug(f"\tline[{self.i+1}]: {self.lines[self.i].rstrip()}")

        parsingExtraLine = False

        if self.extraLine is None:
            #- Ignore comments and split line into list
            lineList = self.lines[self.i].strip().split('//')[0].split()
        else:
            lineList = self.extraLine.strip().split('//')[0].split()
            parsingExtraLine = True

        logger.debug(f"\tlineList: {lineList}")

        try: 
            if len(lineList) == 0 or self._parseComments():
                # Line is blank or comment
                return None
            elif len(lineList) == 1:
                if lineList[0].strip() == '};' or lineList[0] == ');':
                    #- ending list or dict
                    return None
                match = re.match('\$(.*);', lineList[0].strip())
                if match is not None:
                    # Found variable reference
                    name_ = match.group(1)
                    logger.debug(f"Found variable: {name_}.")
                    return ofVar(name_)
                if lineList[0].strip()[-1] == ';':
                    #- found non-keyword value
                    return ofWord(lineList[0].strip().rstrip(';'))
                if lineList[0] == '}':
                    return None # Found beggining or end of dictionary
                listOrDictName = self.lines[self.i].lstrip().rstrip()
                logger.debug(f"listOrDictName: {listOrDictName}")                
                if any([listOrDictName is char for char in ['(', '{']]):
                    logger.debug("Parsing unnamed list or dictionary.")
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
            if parsingExtraLine:
                self.extraLine = None #- reset the extra line to parse 
                                      #  next line in file.
            else:
                self.i += 1

    def _parseLineLenTwo(self):
        logger.debug("Parsing line of length 2.")

        lineList = self.lines[self.i].strip().split()
        
        #logger.debug(f"lineList: {lineList}")
        
        if lineList[0].startswith('#include'):
            # Found include statement 
            return self._parseIncludes(lineList[0], lineList[1].rstrip(';'))
        elif lineList[1][-1] == ';':
            # Found single line entry
            return self._parseSingleLineEntry(lineList[0], 
                lineList[1].rstrip(';'))
        elif lineList[1] == 'table':
            # Found a table entry
            return self._parseTable(lineList[0])
        else:
            logger.error(f"Cannot handle single line entry '{lineList}' on line "\
                f"{self.i+1} of {self.filepath}.")


    def _parseSingleLineEntry(self, key, value):
        """
        Extract the value as the approriate ofTypes

        Search order:
            - ofFloat, ofInt, ofBool, ofStr
        """

        logger.debug("Parsing a single line entry")

        logger.debug(f"key: {key}, value: {value}")

        type_, value_ = self._parseValue(value)

        if hasattr(type_, 'name'):
            return type_(name=key, value=value_)
        elif hasattr(type_, '_name'):
            return type_(_name=key, value=value_)
        else:
            self._userMsg(f"Could not set name for type {type_}.  Returning "\
                "value only!", "WARNING")
            return type_(value=value_)

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

        if name is not None:
            name = name.strip()

        lineList = self.lines[self.i].strip().split()

        logger.debug(f"parseListOrDict name: {name}")

        logger.debug(f"lines[{self.i+1}]: {self.lines[self.i].split()}")

        openingChar = None
        if any([lineList[0].startswith(c) for c in ['(', '{']]):
            openingChar = lineList[0][0]
        elif (lineList[0] == name and
            any([lineList[1].startswith(c) for c in ['(', '{']])):
            openingChar = lineList[1][0]
        
        logger.debug(f'openingChar: {openingChar}')

        if openingChar is None:
            self._userMsg(f"Invalid syntax on line {self.i+1} of dictionary "
            f"file '{self.filepath}'.", level='ERROR')
                 
        logger.debug(f"Opening char: {openingChar}")

        if openingChar == '(':
            if len(lineList) > 1:
                #list in one a single line
                if lineList[-1][-1] != ';':
                    return self._parseList(name)
                    #lineList = self._getLinesList(self.i)
                logger.debug(f"lineList: {lineList}")
                #TODO: Handle lists of lists on a single line
                list_ = ofNamedList(name=name)
                for v in lineList[1:]:
                    if v != "":
                        list_.value.append(v)
                return list_
            else:
                # - Parse the list recursively to capture list of lists
                return self._parseList(name)
        elif openingChar == '{':
            #value = { name: None }
            # - Parse the dictionary recursively to capture dict of dicts
            self.i += 1
            logger.debug(f"Parsing {name} dictionary.")
            return ofDict(self._parseDict(name))
        # else:
        #     self._userMsg(f"Invalid syntax on line {self.i+1} of dictionary "
        #     f"file '{self.filepath}'.", level='ERROR')
        #     # logger.error(f"Invalid syntax on line {self.i+1} of dictionary "
        #     # f"file '{self.filepath}'.")
        #     # sys.exit()

        #self.i += 1

    def _parseList(self, name):
        """
        Parse a list storing values as ofList.  
        
        Only parse recursively if dictionaries are found within list, otherwise
        keywords are not included
        """
        
        i_start = self.i
        # - Find the end of dictionary        
        i_end = self._findDictOrListEndLine('list')

        logger.debug(f"i_end: {i_end}")

        logger.debug(f"name: {name}")



        list_ = ofNamedList(name=name)

        #- check to see if list contains dictionaries:
        contentStr = ' '.join(self.lines[self.i:i_end+1])
        logger.debug(f"content string:\n{contentStr}")

        if '{' in contentStr and '}' in contentStr:
            #- found dictionary, parse recursively
            logger.debug("Found dictionaries within list, parsing recursively...")
            
            #- Skip current line (with '('), and store any additional text as 
            #  extra line.
            extraLine = ''.join(self.lines[self.i].strip().split('(')[1:])
            if extraLine != '':
                logger.debug(f"extraLine: {extraLine}")
                self._addExtraLine(extraLine)

            self.i+=1

            while self.i < i_end:
                list_.value.append(self._parseLine())

            logger.debug(f"list_:\n{list_}")

            return list_

        logger.debug("Parsing list without dictionary values...")

        entryList = []

        while self.i <= i_end:
            line = self.lines[self.i]
            if self.i == i_start:
                #- ignore first (
                if line.strip() != "" and line.strip()[0] != '(':
                    self._userMsg("Inavlid syntax.  List value does not "\
                        "begin with '('.", 'ERROR')
                line=line.strip()[1:]
            if ';' in line:
                if self.i != i_end:
                    logger.error("Unhandled pattern found!")
                    sys.exit()
                #- store extra characters as a new line to be parsed later
                self._addExtraLine(''.join(line.split(';')[1:]))
                #- ignore last );
                line = line.split(';')[0].rsplit(')')[0] 
                
            logger.debug(f"line[{self.i+1}]: {line}")

            for entry in line.strip().split():
                entryList.append(entry)
            strValue = " ".join(entryList)
            if strValue.strip() != "":
                list_.value.append(self._parseListValues(strValue))
            # for entry in entryList:
            #     if entry != "":
            #         list_.value = self._parseListValues(" ".join(entry))
            self.i+=1
            logger.debug(f"self.i: {self.i}")
            
        

        return list_

    def _parseListValues(self, values : str):
        """
        convert a string value from file into the appropriate of type.
        """

        logger.debug(f"list values: {values}")
        logger.debug(f"len list values: {len(values)}")

        #- Get expressions between parenthesis as list:
        #valuesList = [p.split(')')[0] for p in values.split('(') if ')' in p]

        #logger.debug(f"valuesList: {valuesList}")

        # #- remove any leading or trailing parentheses if they cover whole line
        # if values[0] == '(' and values[-1] == ')':
        #     if len(values) > 2
        #     nopen = 0
        #     nclosed = 0
        #     for char in values[1:-1]:
        #         if char = '('
        #     else:
        #         return None

        listValues = []

        #- Divide value string into entities with list of lists if parentheses
        i=0
        delimiters = BRACKET_CHARS['list']
        delimiters.append(" ")

        while i < len(values):
            if values[i] == '(':
                #- add value as list
                #- find end of list:
                logger.debug(f"line list searchStr: {values[i:]}")
                j=self._findDictOrListEndIndex(values[i:])
                subStr = values[i+1:i+j]
                logger.debug(f"subStr: {subStr}")
                # if j != len(values)-1:
                #     #- Add extra text to self.extraLine
                #     self.extraLine.append(values[j:])
                if not any([char in subStr for char in BRACKET_CHARS['list']]):
                    #if not list of lists, append values
                    for value in subStr.split():
                        listValues.append(value)
                else:
                    #TODO: Store as ofList or list
                    # listValues.append(ofList(value=self._parseListValues(subStr)))
                    listValues.append(self._parseListValues(subStr))
                i=j+i
                logger.debug(f"i: {i}")
                logger.debug(f"j: {j}")
            else:
                value_ = ''
                while not any([values[i] == char for char in delimiters]):
                    value_+=values[i]
                    if i == len(values)-1:
                        break
                    logger.debug(f"value_: {value_}")
                    i+=1
                if value_ != '':
                    type_, v = self._parseValue(value_)
                    #listValues.append(type_(value=v)) # TODO: save as ofType?
                    listValues.append(v)
            logger.debug("list values during parsing: "\
                f"{listValues}")
            i+=1
            logger.debug(f"i: {i}")
                    
        return listValues


    def _findDictOrListEndIndex(self, string, type='list'):
        """
        Find the index that terminates the list or dictionary that begins at the
        start of string.  Any text before the first opening bracket is ignored.

        Parameters:
            string [str]:  The string to be parsed.
            type [str]:  The type of object to parse (either 'dict' or 'list')

        Returns:
            i [int]:  The index on of the string where the highet level list
                        or dictionary ends.
        """

        openingChar = BRACKET_CHARS[type][0]
        closingChar = BRACKET_CHARS[type][1]

        logger.debug(f"Search for close str: {string}")

        #- Check that the appropraite BRACKET_CHAR is actually in string
        if openingChar not in string:
            logger.error(f"String does not contain {type} opening char "\
                f"'{openingChar}.")
            sys.exit()

        # #- Remove first opening char and any preceding text
        # string = openingChar.join(string.split(openingChar)[1:])

        i = 0
        #-Increment to the first opening char:
        while string[i] != openingChar:
            i+=1
        i+=1

        logger.debug(f"Search for close str: {string[i:]}")

        level = 1
        while True: # Find matching parenthesis
            if i >= len(string):
                self._userMsg("Unhandled expression.  Could not find "\
                    f"end of list on line {self.i+1} of {self.filepath}.",
                    'ERROR')
            if string[i] == openingChar:
                level+=1
            if string[i] == closingChar:
                level-=1
            if level == 0:
                break 
            i+=1

        logger.debug(f"list ended at index {i} at char '{string[i]}'.")

        return i
            
    def _parseDict(self, name):
        """
        Recursively parse a dictionary storing values as ofDict 
        """
        # - Find the end of dictionary        
        i_end = self._findDictOrListEndLine('dict')

        logger.debug(f"Parsing dictionary '{name}'.")
        logger.debug(f"line[{self.i+1}] '{self.lines[self.i].strip()}'.")

        dict_ = ofDict(_name=name)

        # self.i -= 1 #- reset index because will increment automatically in
                    #  _parseLine

        while self.i <= i_end:
            dict_.update(self._parseLine())

        logger.debug(f"dict_:\n{dict_}")

        self.i-=1 # Reset line index since it will increment in _parseLine

        logger.debug(f"Finished parsing dict {name} on line {self.i+1}")

        return dict_

    def _findDictOrListEndLine(self, type, string=None):
        """
        Find the line that terminates the dictionary starting on the currently
        parsed line (i.e. the `self.i'th line)

        Parameters:
            type [str]:  The type of object to parse (either 'dict' or 'list')

        Returns:
            i [int]:  The line on which the current list or dictionary ends.
        """

        def searchLine(level, i):
            line = self.lines[i]
            for char in line:
                if char == BRACKET_CHARS[type][0]:
                    level += 1
                    logger.debug(f'found char: {BRACKET_CHARS[type][0]}')
                    logger.debug(f"level: {level}")
                    logger.debug(f"line: {i}")
                if char == BRACKET_CHARS[type][1]:
                    level -= 1 
                    logger.debug(f'found char: {BRACKET_CHARS[type][1]}')
                    logger.debug(f"level: {level}")
                    logger.debug(f"line: {i}")
            return level


        level = 0

        i_ = self.i

        #- Parse to the first opening bracket to initialize second while loop
        while level == 0:
            if i_ >= len(self.lines):
                self._userMsg(f'Invalid syntax.  Could not locate start of '\
                    f'{type} from line {self.i+1}.', 'ERROR')

            level = searchLine(level, i_)
            i_+=1

        logger.debug("End of initialization loop.")

        while level > 0:
            if i_ >= len(self.lines):
                self._userMsg(f'Invalid syntax.  Could not locate end of '\
                    f'{type} starting on line {self.i+1}.', 'ERROR')
            line = self.lines[i_]
            logger.debug(f"i: {i_}")
            logger.debug(f"line: {line}")
            for char in line:
                if char == BRACKET_CHARS[type][0]:
                    level += 1
                    logger.debug(f'found char: {BRACKET_CHARS[type][0]}')
                    logger.debug(f"level: {level}")
                    logger.debug(f"line: {i_}")
                if char == BRACKET_CHARS[type][1]:
                    level -= 1 
                    logger.debug(f'found char: {BRACKET_CHARS[type][1]}')
                    logger.debug(f"level: {level}")
                    logger.debug(f"line: {i_}")
            i_+=1

        logger.debug(f"Found {type} entry from lines {self.i+1} to {i_}.")

        return i_-1
            

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

    def _parseTable(self, name, string = None):
        """
        Parse a table entry specified as 

        <name>   table
        (
            (0.0 (1 2 3))
            (1.0 (4 5 6))
        );

        If string is 'None', parses lines starting with '('.  else parses a 
        string starting at '('

        """

        if string is not None: # parse string 
            line = string
            logger.debug(f"parseTable string: {string}")
            if line.split()[1] == 'table': # whole line is passed as input
                lineList = line.split()[2:] # Remove the 'table' designation
            elif line.strip().startswith('(('):  # only list value is passed as input
                lineList = line.split()
            else:
                self._userMsg(f"Unhandled syntax for table found on line "\
                    f"{self.i+1} of {self.filepath}.", "ERROR")
            list_ = self._parseListValues(" ".join(lineList))
            return ofTable(name=name, value = list_) 
        else: # parse lines
            line = self.lines[self.i]
            list_ = self._parseList(name)
            return ofTable(name=name, value = list_.value)


    def _parseValue(self, value):
        """
        Parse a single value to get the appropraite ofType.
        """
        # TODO: Should I assume list values of certain length are tensors?
        # TODO:  Add ofScalar?
        
        # check for a spherical tensor, (e,g, '(0)')
        if value[0] == '(' and value[-1] == ')':
            #- Value is a list
            try:
                value_ = float(value.strip('()'))
                return ofSphericalTensor, value_
            except:
                pass

            #- Check if the str value can be conveted into a list
            list_ = value.strip('()').split()
            # if len(list_) > 1:
            #     value_ = []
            #     valid = True
            #     for v in list_:
            #         # TODO:  Need to return non-numeric values too
            #         try:
            #             v_ = float(value.strip('()'))
            #             value_.append(v_)
            #         except:
            #             valid = False
            #     if valid:
            #         return ofList, value_                

            return ofNamedList, list_

        try:
            value_ = float(value)
            if '.' in value:
                return ofFloat, value_
            else:
                return ofInt, int(value_)
        except ValueError:
            pass
        # try:
        #     value_ = int(value)
        #     return ofInt, value_
        # except ValueError:
        #     pass
        if any([value == b for b in OF_BOOL_VALUES.keys()]):
            return ofBool, value
        
        return ofStr, value

    def _parseLineLenGreaterThanTwo(self):
        """
        Parse a line that has more than two words.  Assumes that the line
        defines either a dict or list since list entries appearing on a single
        line are handled within the '_parseList' method, and should not be
        encountered here.
        """

        logger.debug("Parsing line of length greater than two...")

        line = self.lines[self.i]
        entryName = None

        #- Check if commented line
        comment = self._parseComments()
        if comment:
            return None

        #- Check if the line contains a dimensioned type
        dimType = self._parseDimensionedType()
        logger.debug(f"dimType: {dimType}")
        if dimType is not None:
            return dimType
        

        #- check if the line terminates in an open list or dict
        nl = 0
        nd = 0

        while True:
            for char in line:
                if char == '(':
                    nl+=1
                if char == ')':
                    nl-=1
                if char == '{':
                    nd+=1
                if char == '}':
                    nd-=1
            
            if nl == 0 and nd == 0:
                break

            if nl > 0:
                logger.debug("Found open list..")
            if nd > 0:
                logger.debug("Found open dictionary...")

            # self.i+=1
            line+=self.lines[self.i]

        if ';' in line:
            #- add extra text after ';' as a new line to be parsed later
            #- Remove ';',) and extra closing ')' or '}' (maybe).  Assuming within list 
            # or dict.  Other possibilities (e.g dimensioned types) should be
            # handled prior to this point in the method.
            extraText = ''.join(line.split(';')[1:]).replace('\n', '') 
            self._addExtraLine(extraText)
            #line = line.split(';')[0][:-1] 
            line = line.split(';')[0] # do not remove last ')' or '}' 

        if ' (' in line or ' {' in line:
            #- Found list or dict
            # - find the entry type
            for i, char in enumerate(line):
                if char == '{' or char == '(':
                    entryName = line[:i].lstrip().rstrip()
                    logger.debug(entryName)
                    # valueList = line[i:].split(" ").rstrip(char+';')
                    break

            logger.debug(f"entryName: {entryName}")

            if entryName:
                entryNameList = entryName.split()
                if len(entryNameList) == 2 and entryNameList[1] == 'table':
                    list_ = line.strip()[len(entryName):]
                    self._parseTable(entryNameList[0], list_)
                else:
                    self._parseListOrDict(entryName)
            else:
                self._userMsg(f"Invalid syntax found on line {self.i+1} of file "
                f"{self.filepath}", 'ERROR')
                sys.exit()
        else:
            #- Assume entry is a key value pair with a muliple word value.
            #      (e.g. 'default       Gauss linear')
            lineList = line.split()
            self._parseSingleLineEntry(key=lineList[0], 
                                       value=' '.join(lineList[1:]))


    def _parseComments(self):
        """
        Returns 'True' if the current line is a C++ comment type.  If block 
        comment, self.i is incremented to end of comment block.
        """
        #TODO: Doesnt handle comments in middle of line (Maybe this should be 
        # handled elsewhere)

        line = self.lines[self.i]

        # logger.debug("Checking for comment.")
        # logger.debug(f"line: {line}")

        if line.strip().startswith('//'):
            return True

        if line.strip().startswith('/*'):
            while not self.lines[self.i].strip().endswith('*/'):
                self.i+=1
                if self.i >= len(self.lines):
                    self._userMsg("Could not find end of commented block in"\
                        f" file {self.filepath}.", 'ERROR')
            return True

        return False

    def _parseDimensionedType(self):
        """ 
        Check to see if the line contained a entry for a dimensioned type.  If 
        so, return the ofType, else return None

        dimensioned types have the syntax: 

        nu      [0 2 -1 0 0 0 0] 1.138e-06;

        """

        i_ = self.i
        line = self.lines[i_]
        #- Parse the file to the end of the statement (maybe not at end of line)
        while ';' not in line:
            if i_ >= len(self.lines)-1:
                return None # No staement found, cant be dimensioned type
            i_+=1
            line += self.lines[i_]
        
        lineList = line.split()

        if not len(lineList) >= 9:
            return None # Need at least nine entries to define a dimensioned type 

        try: 
            ofWord(lineList[0])
        except ValueError:
            return None  # First item is not a ofWord, and can't be a keyword
        
        if '[' not in lineList[1]:
            return None # Second item does not start a dimension specification
        
        if not any([']' in val for val in lineList[7:10]]): # handle 
            return None                                     # [0 1 2 0 0 0 0]
                                                            # [ 0 1 2 0 0 0 0]
                                                            # [0 1 2 0 0 0 0 ]
                                                            # [ 0 1 2 0 0 0 0 ]

        #- Get the dimension string
        dims = []
        try:
            d_ = int(lineList[1].strip('['))
            dims.append(d_)
        except ValueError:
            return None #- Dimensioned quantity is not an int

        for i, d in enumerate(lineList[2:10]):
            logger.debug(f"i: {i}")
            try:
                d_ = int(d.strip(']'))
                dims.append(d_)
            except ValueError:
                return None
            if ']' in d:
                break
        
        #- parse the value
        strValue = " ".join(lineList[i+3:]).strip(';')
        type_ , value = self._parseValue(strValue)

        logger.debug(f'type_: {type_}')
        logger.debug(f'value: {value}')

        returnType = None
        if type_ is ofInt or type_ is ofFloat:
            returnType = ofDimensionedScalar
        elif type_ is ofSphericalTensor:
            returnType = ofDimensionedSphericalTensor
        if type_ == ofList:
            try:
                [float(v) for v in value]
            except ValueError:
                return None # not all values in list are numeric
            if len(value) == 3:
                returnType = ofDimensionedVector
            elif len(value) == 5:
                returnType = ofDimensionedSymmTensor
            elif len(value) == 9:
                returnType = ofDimensionedTensor

        if returnType:
            self.i = i_ 
            return returnType(value=value, name=lineList[0],
                              dimensions=dims)

        return None #- Could not find a suitable dimensioned type based on
                    # length of list 


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
    #                         logger.warning("End of file '"+relPath+"' reached "\
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

        logger.debug('endofDict: '+str(endOfDict))

        return endOfDict

    def _findEndOfHeader(self):
        foamFileFound = False
        foamFileStart = False

        with open(self.filepath) as f:
            for i, line in enumerate(f.readlines()):
                if line.strip() == 'FoamFile':
                    foamFileFound = True
                if (foamFileFound and line.startswith('{')):
                    foamFileStart = True
                if (foamFileFound and foamFileStart and '}' in line):
                    return i+1

        logger.error('Invalid OpenFOAM file specified: '+str(self.filepath))
        sys.exit()
