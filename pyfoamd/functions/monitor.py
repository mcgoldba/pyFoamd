import subprocess
import sys

from richinclude import *

log.setLevel(logging.DEBUG)

def monitor(time=None, supplement=None):
    
    commands = ['pfmonitor']
    if time: commands.append(['-t', str(time)])
    if supplement:
        commands.append('-s')
        for s in supplement:
            commands.append(str(s))

    log.debug("commands: "+str(commands))
    try:
        subprocess.run(commands)
    except KeyboardInterrupt:
        sys.exit(0)

