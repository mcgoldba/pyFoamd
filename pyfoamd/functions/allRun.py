import subprocess
from pathlib import Path
import os
from pyfoamd.functions import isCase
from pyfoamd import userMsg

def allRun(caseDir=Path.cwd()):
    if not isCase(caseDir):
        userMsg(f"Invalid case directory specified:\n {caseDir}", "ERROR")
    script_ = str(Path(caseDir) / 'Allrun')
    userMsg(f"Running case {caseDir}")
    subprocess.call('./'+script_)
