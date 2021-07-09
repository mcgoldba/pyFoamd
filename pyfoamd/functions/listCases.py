import os
import sys
import re

from .isCase import isCase

from pyfoamd.config import DEBUG
DEBUG=False

from pyfoamd.richinclude import *

def listCases(path=os.getcwd(), absolutePath=False):
    if isCase(path): #is the root directory an OpenFOAM case?
        if absolutePath:
            return [path]
        else:
            return ['.']

    cases = []

    for root, subFolders, _ in os.walk(path):
        for subFolder in subFolders:
            if isCase(os.path.join(root, subFolder)):
                log.debug(str(subFolder)+" is an OpenFOAM case.")
                log.debug("root: "+str(root))
                log.debug("subFolder: "+str(subFolder))
                if absolutePath:
                    cases.append(os.path.join(root, subFolder))
                else:
                    relPath = root.replace(path, "")
                    cases.append(os.path.join(relPath, subFolder))
    return cases
