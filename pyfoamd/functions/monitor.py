import subprocess
import sys
import os

import logging

log = logging.getLogger("pf")

def monitor(time=None, supplement=None, workingDir=os.getcwd()):

    commands = ['pfmonitor']
    if time:
        commands.append('-t')
        commands.append(str(time))
    if supplement:
        commands.append('-s')
        for s in supplement:
            commands.append(str(s))

    log.debug("commands: "+str(commands))
    try:
        subprocess.run(commands, cwd=workingDir)
    except KeyboardInterrupt:
        sys.exit(0)
    # subprocess.call(commands, cwd=workingDir)
