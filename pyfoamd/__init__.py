import os
from configparser import ConfigParser
from pathlib import Path
import sys

import logging


from rich import print

from rich.traceback import install
install()

logger = logging.getLogger('pf')

try:
    FOAM_VERSION = os.environ['WM_PROJECT_VERSION']
except:
    FOAM_VERSION = ""
    print("OpenFOAM not found!")

def getPyFoamdConfig(param):
    def getParam(param, configPath):
        parser = ConfigParser()
        parser.read(configPath)

        if parser.has_section('user'): 
            param_ = parser.get('user', param.lower(), fallback=None)
            if param_ is None:
                param_ = parser.get('default', param.lower(), fallback=None)
        else:
            param_ = parser.get('default', param.lower(), fallback=None)
        return param_       

    param_ = None
    if (Path('.params') / 'config.ini').is_file():
        # print(f"Pyfoamd config file: {Path('.params') / 'config.ini'}")
        param_ = getParam(param, Path('.params') / 'config.ini')
    if param_ is None and (Path.home() / '.pyfoamd' / 'config.ini').is_file():
        # print(f"Pyfoamd config file: {Path.home() / '.pyfoamd' / 'config.ini'}")
        param_ = getParam(param, Path.home() / '.pyfoamd' / 'config.ini')
    # print(f"Looking for Pyfoamd config file: {Path(__file__) / 'config.ini'}...")
    if os.name == 'nt':
        if param_ is None and (Path(__file__) / 'config.ini').is_file():
            # print(f"Pyfoamd config file: {Path(__file__) / 'config.ini'}")
            param_ = getParam(param, Path(__file__) / 'config.ini')
    else:
        if param_ is None and (Path(__file__).parent / 'config.ini').is_file():
            # print(f"Pyfoamd config file: {Path(__file__).parent / 'config.ini'}")
            param_ = getParam(param, Path(__file__).parent / 'config.ini')
    if param_ is None:
        # print(f"Warning: Using system default for Pyfoamd config.  Could not find config file")
        if param.lower() == 'debug':
            param_ = False
        if param.lower() == 'dict_filesize_limit':
            param_ = 10000000

    if param_ is None:
        Exception(f"Could not locate parameter '{param}' in config.ini and no default is provided.")

    # print(f"PyFoam config: {param} = {param_}")

    return param_

def userMsg(msg, level = "INFO"):
    """
    Write message to console or stdout for the user (i.e. without code details)
    
    Parameters:
        msg [str]:  The message to print
        
        level [str]: Either "INFO", "WARNING" or "ERROR".  If "ERROR", script is
        terminated.
    """

    printStyle = {
        "INFO": 'blue',
        "WARNING": "bold orange",
        "ERROR": "bold red"
    }

    if logger.level == logging.DEBUG:
        logger.debug(f'User Msg:{level}: {msg}')
        #raise Exception
    else:
        print(f'[{printStyle[level]}]{level}:[/{printStyle[level]}]'\
            f' {msg}')
    
    if level == 'ERROR':
        sys.exit()

def setLoggerLevel(level):
    """Set the message level of the Python logger."""

    levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET
    }

    logging.getLogger('pf').setLevel(levels[level])
