import subprocess
import sys
import os

from pyfoamd.richinclude import *

log.setLevel(logging.DEBUG)

def monitor(time=None, supplement=None, workingDir=os.getcwd()):

    commands = ['pfmonitor']
    if time: commands.append(['-t', str(time)])
    if supplement:
        commands.append('-s')
        for s in supplement:
            commands.append(str(s))

    log.debug("commands: "+str(commands))
    try:
        subprocess.run(commands, cwd=workingDir)
    except KeyboardInterrupt:
        sys.exit(0)