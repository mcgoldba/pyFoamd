from types import NoneType
from pyfoamd import getPyFoamdConfig, setLoggerLevel, userMsg
from pyfoamd.types import CaseParser, FolderParser, _ofCaseBase
from pathlib import Path
import json
from pydoc import locate #ref: https://stackoverflow.com/a/29831586/10592330
import sys

import logging

logger = logging.getLogger('pf')

# from pyfoamd.config import DEBUG

def load(path=Path.cwd() / '.pyfoamd' / '_case.json', _backup=False):
    """
    Read in an OpenFOAM case saved as a JSON object
    """

    if not isinstance(path, Path):
        path = Path(path)

    if not _backup:
        if str(path)[-5:] != '.json':
            path = Path(str(path)+'.json')
    # else:
    #     if str(path)[-5:] == '.json':
    #         path = Path(str(path)[:-5])


    # def toOfType(dict_):
    #     if '_type' in dict_:
    #         logger.debug(f"_type: {dict_['_type']}")
    #         if dict_['_type'] == 'ofFolder':
    #             #TODO:  THis reads folder from existingpath rathr than copying
    #             # obj = FolderParser(path=dict_['_path']).makeOFFolder()
    #             obj = FolderParser(path=dict_['_path']).initOFFolder()
    #         elif dict_['_type'] =='ofCase':
    #             obj = CaseParser().initOFCase()
    #         else:
    #             type_ = locate('pyfoamd.types.'+dict_['_type'])
    #             try:
    #                 obj = type_()
    #             except TypeError:
    #                 logger.error(f"Could not find suitable type: {dict_['_type']}.")
    #                 raise Exception
    #             for key, value in dict_.items():
    #                 if key != '_type': # type property is set automatically
    #                     logger.debug(f"Setting attribute {key}")
    #                     obj.__setattr__(key, value)
    #             return obj
    #     else:
    #         return dict_)

    setLoggerLevel("DEBUG" if getPyFoamdConfig('debug').lower() == 'true'
                    else "INFO")

    if not path.is_file():
        userMsg("No cached case data found.  Run 'pf init'"\
            " before 'pf edit'.", "WARNING")
        return None

    with open(path, 'r') as fp:
        # caseDict = json.load(fp, object_hook=toOfType)
        caseDict = json.load(fp)

    logger.debug(f"caseDict: {caseDict}")



    def parseCaseDict(obj, tabStr=None):
        """
        Recursrively parse a JSON dictionary representation of an ofCase

        Parameters:
            obj [any] : The current object being parsed.  Initial object should 
                be the caseDict.

            obj_ is the ofCase representation of the caseDict.

            tabStr is for debugging purposes only.
        """
        if tabStr is None:
            tabStr = ''
        else:
            tabStr += '    '
        logger.debug(f"{tabStr}Starting 'parseCaseDict' iteration")
        logger.debug(f"{tabStr}obj: {obj}")
        logger.debug(f"{tabStr}Parsing type {type(obj)}.")
        if isinstance(obj, dict):
            if '_type' in obj.keys():
                logger.debug(f"{tabStr}Parsing {obj['_type']}.")
                if obj['_type'] == 'ofFolder':
                    #TODO:  This reads folder from existing path rather than 
                    # copying 
                    # obj = FolderParser(path=dict_['_path']).makeOFFolder()
                    obj_ = FolderParser(path=obj['_path']).initOFFolder()
                    logger.debug(f"{tabStr}Defined obj_: {obj_}")
                elif obj['_type'] =='ofCase':
                    obj_ = CaseParser().initOFCase()
                    logger.debug(f"{tabStr}Defined obj_: {obj_}")
                else:
                    type_ = locate('pyfoamd.types.'+obj['_type'])
                    try:
                        obj_ = type_()
                        logger.debug(f"{tabStr}Defined obj_: {obj_}")
                    except TypeError as e:
                        logger.error(f"Could not find suitable type: {obj['_type']}.")
                        raise e
                for key, value in obj.items():
                    logger.debug(f"{tabStr}Parsing key {key}.")
                    if key != '_type' and key :
                        logger.debug(f"{tabStr}Setting key {key}.")
                        value_ = parseCaseDict(value, tabStr)
                        logger.debug(f"{tabStr}value_: {value_}")
                        logger.debug(f"{tabStr}obj_: {obj_}")
                        setattr(obj_, key, value_)
                logger.debug(f"{tabStr}Returning {obj_}.")
                return obj_
            else:
                return obj
        else:
            logger.debug(f"{tabStr}Returning {obj}.")
            return obj
            
    case_ = parseCaseDict(caseDict, )


    if isinstance(case_, _ofCaseBase):
        return case_
