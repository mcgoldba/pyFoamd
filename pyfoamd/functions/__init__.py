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

import pint
from pint import UnitRegistry
import json
import pandas as pd
# from functools import reduce
# import operator
# from collections.abc import Mapping

from .private.readDict import readDict
from .private.dictUtil import _appendBlockEntryWithBlockName, _replaceStringEntry,\
_replaceSingleLineEntry, _findBlockEntryStartStop, _findEndOfDict,\
_appendBlockEntryWithLineNum, _readDictFile, _ofDictFindBlockEntryStartStop,\
_findEndOfHeader
from .private._interpretUnitsAndConvert import _interpretUnitsAndConvert
from .private._unitDecoder import _unitDecoder
from .appendEntry import appendEntry
from .getLatestTime import getLatestTime
from .replaceEntry import replaceEntry
from .removeEntry import removeEntry
from .removeBlockEntries import removeBlockEntries
from .readDictFile import readDictFile
from .readInputs import readInputs
from .printInputs import printInputs
from .cleanDictFile import cleanDictFile
from .isDecomposed import isDecomposed
from .isReconstructed import isReconstructed
from .isMeshed import isMeshed
from .cleanDictFile import cleanDictFile
from .readDictFile import readDictFile


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


############################ Member Functions ###############################

######################## Private Member Functions ###########################
