import sys

print(sys.version)

#- Check the python version:
if sys.version_info < (3,7):
    sys.exit('Sorry, Python < 3.7 is not supported.')

from pyfoamd.types import ofDictFile, ofDict, ofList, ofInt, ofFloat, \
    ofStr, ofBool, ofDimensionedScalar, ofVector, ofNamedVector, \
        ofDimensionedVector, TAB_STR

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
from .readInputs import readInputs
from .writeParams import writeParams
from .printInputs import printInputs
from .cleanDictFile import cleanDictFile
from .isDecomposed import isDecomposed
from .isReconstructed import isReconstructed
from .isMeshed import isMeshed
from .cleanDictFile import cleanDictFile
from .isCase import isCase
from .listCases import listCases
from .monitor import monitor
from .writeConfig import writeConfig
from .readConfig import readConfig
from .extractLogData import extractLogData
from .isOFDict import isOFDict
from .init import init
from .readCaseFromCache import readCaseFromCache
from .writeCase import writeCase
from .load import load
from .restore import restore
from .allRun import allRun

#import logging

#Define padding for blockMeshDict
PAD = 1 / 12 / 3.281 # 1 inch


############################ Member Functions ###############################

######################## Private Member Functions ###########################
