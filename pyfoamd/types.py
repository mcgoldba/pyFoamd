from dataclasses import dataclass, field, make_dataclass
import operator
from collections.abc import MutableMapping
import copy
from pathlib import Path
import warnings

#from pyfoamd.functions import isOFDictFile, _readDictFile
#from pyfoamd.functions.private.dictUtil import *

from typing import List

OF_BOOL_VALUES = ['on', 'off', 'true', 'false']
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

def ofFolder(path):

    attrList = [('_path', Path, field(default=path))]
    for obj in Path(path).iterdir():
        if obj.is_dir():
            if obj.name == '_path':
                warnings.warn(f"'{obj.name}' is a reserved attribute.  "
                              "Skipping directory: {obj} ")
                continue
            attrList.append((obj.name, ofFolder, field(default=ofFolder(obj))))
        # - Check for OpenFOAM dictionary files
        if obj.is_file() and isOFDictFile(obj):
            attrList.append(obj.name, ofDictFile,
                            field(default=_readDictFile(obj)))

    return make_dataclass('ofFolder', attrList, frozen=True)(path)


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
        ('constant', ofFolder, field(default=ofFolder('constant'))),
        ('system', ofFolder, field(default=ofFolder('system'))),
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


# @dataclass
# class ofFolder:
#     case: Path = field(default=Path.cwd())


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
    name: str = None
    path: str = 'system/'
    version: str = '2.0'
    ofClass: str = 'dictionary'
    #entries: field(default_factory=lambda: [])

@dataclass
class _ofDictBase(dict):
    # ref: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    def __getattr__(*args):
        val = dict.get(*args)
        return ofDict(val) if type(val) is dict else val
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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
    name: str = None
    value: int = None

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
    value: bool = None

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
        dStr = "{\n"
        for k, v in zip(self.keys(), self.values()):
            if isinstance(v, ofDict):
                dStr2 = v.asString().split("\n")
                for i in range(len(dStr2)):
                    dStr2[i] = TAB_STR+dStr2[i]+"\n"
                    dStr += dStr2[i]
            else:
                dStr += printNameStr(TAB_STR+k)+v.asString()
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
        boolStr = ['true' if self.value else 'false'][0]
        return printNameStr(self.name)+boolStr+';\n'

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
