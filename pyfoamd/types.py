from dataclasses import dataclass, field
import operator
from collections.abc import MutableMapping
# from 

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
    
#@dataclass
class _ofDictFileBase(MutableMapping):
    #store: dict()
    #update: dict(*args, **kwargs)
    value: field(default_factory=list)

    def __getitem__(self, key):
        return self.store[self._keytransform(key)]

    def __setitem__(self, key, value):
        self.store[self._keytransform(key)] = value

    def __delitem__(self, key):
        del self.store[self._keytransform(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def _keytransform(self, key):
        return key

@dataclass
class _ofDictFileDefaultsBase:
    filename: str = None
    location: str = 'system/'
    version: str = '2.0'
    ofClass: str = 'dictionary'
    #entries: field(default_factory=lambda: [])
    
@dataclass
class _ofDictBase(_ofDictFileBase):
    name: str
    value: dict
    
        
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
    name: str
    value: list


@dataclass 
class _ofIntBase(_ofDictFileBase):
    name: str
    value: int
        
    @property
    def valueStr(self):
        return str(self.value)

@dataclass
class _ofFloatBase(_ofIntBase):
    name: str
    value: float
        
@dataclass
class _ofStrBase(_ofIntBase):
    name: str
    value: str

@dataclass
class _ofBoolBase(_ofIntBase):
    name: str
    value: bool
        
@dataclass
class _ofDimensionedScalarBase(_ofFloatBase):
    dimensions: field(default_factory=list)

@dataclass
class _ofVectorBase:
    #name: field(init=False, repr=False)
    value: field(default_factory=list)

        
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
        if ( len(v) != 3 or any(isinstance(i, (int, float)) for i in v)
            is False):
            raise Exception("'ofVector' values must be a numeric list of length 3.")
        self._value = v
@dataclass 
class _ofVectorDefaultsBase:
    pass
    #name: None=None
    
@dataclass
class _ofNamedVectorDefaultsBase(_ofFloatBase):
    pass

@dataclass
class ofDictFile(_ofDictFileDefaultsBase, _ofDictFileBase):
    pass
    
#    self.filename = filename or None
#    self.location = location or 'system/'
#    self.version = version or '2.0'
#    self.ofClass = ofClass or 'dictionary'
#    self.entries = entries or []

    
@dataclass
class ofDict(ofDictFile, _ofDictBase):
    
    def asString(self) -> str:
        if self.name is not None:
            dStr = self.name+"\n{\n"
        else:
            dStr = "{\n"
        for v in self.value:
            if isinstance(v, ofDict):
                dStr2 = v.asString().split("\n")
                for i in range(len(dStr2)):
                    dStr2[i] = TAB_STR+dStr2[i]+"\n"
                    dStr += dStr2[i]
            else:
                dStr += TAB_STR+v.asString()
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
@dataclass
class ofFloat(ofInt, _ofFloatBase):
    pass
        
@dataclass
class ofStr(ofInt, _ofStrBase):
    pass

@dataclass
class ofBool(ofInt, _ofBoolBase):
    def asString(self) -> str:
        boolStr = ['true' if self.value else 'false'][0]
        return printNameStr(self.name)+boolStr+';\n'

    def __str__(self):
        return self.asString().rstrip(';\n')
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
class _ofNamedVectorBase(_ofFloatBase, _ofVectorBase):
    pass
    #value: ofVector

@dataclass
class ofNamedVector( _ofDictFileDefaultsBase, _ofVectorDefaultsBase, _ofNamedVectorBase):
    
    
    def asString(self) -> str:
        print(self.value)
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
