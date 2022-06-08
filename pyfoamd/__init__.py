import os
from configparser import ConfigParser
from pathlib import Path
import sys

import logging
# logger = logging.getLogger('pf')

from rich import print

from rich.traceback import install
install()

from .richLogger import logger

try:
    FOAM_VERSION = os.environ['WM_PROJECT_VERSION']
except:
    FOAM_VERSION = ""
    print("OpenFOAM not found!")

def getPyFoamdConfig(param):
    parser = ConfigParser()
    parser.read(Path(__file__).parent / 'config.ini')

    if parser.has_section('user'): 
        param_ = parser.get('user', param.lower(), fallback=None)
        if param_ is None:
            param_ = parser.get('default', param.lower(), fallback=None)
    else:
        param_ = parser.get('default', param.lower(), fallback=None)
    
    if param_ is not None:
        return param_ 
    else:
        raise Exception(
            f"Could not find parameter {param} in 'config.ini'.")

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

    # levels = {
    #     "CRITICAL": logging.CRITICAL,
    #     "ERROR": logging.ERROR,
    #     "WARNING": logging.WARNING,
    #     "INFO": logging.INFO,
    #     "DEBUG": logging.DEBUG,
    #     "NOTSET": logging.NOTSET
    # }

    logging.getLogger('pf').setLevel(level)
