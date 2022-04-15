import subprocess
from pathlib import Path
import os

def allRun(caseDir=Path.cwd()):
    os.chdir(caseDir)
    subprocess.call('Allrun')
    os.chdir(Path.cwd())
