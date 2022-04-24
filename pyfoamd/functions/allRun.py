import subprocess
import sys
from pathlib import Path
import os
from pyfoamd.functions import isCase
from pyfoamd import userMsg

def allRun(runDir=Path.cwd()):
    script_ = str(Path(runDir) / 'Allrun')
    userMsg(f"Running Allrun script from {runDir}.")
    subprocess.check_call('./'+script_, stdout=sys.stdout, stderr=subprocess.STDOUT)
