import sys
import argparse, textwrap
from argparse import RawTextHelpFormatter
import pkg_resources  # part of setuptools
import os
import pyfoamd.functions as pf

from .commandline import CommandLine

from rich import print
import logging
from rich.logging import RichHandler

DEBUG = True

FORMAT = "%(message)s"
logging.basicConfig(
       level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger= logging.getLogger("pf")

if DEBUG:
   from rich.traceback import install
   install()


#- main() function
def main():
    """
    PyFoamd:  Pythonic manipulation of OpenFOAM dictionaries.
    """

    version = pkg_resources.require("pyfoamd")[0].version

    intro = main.__doc__+"version "+version + \
            " on Python "+str(sys.version_info.major)+"."+\
                    str(sys.version_info.minor)+"."+\
                    str(sys.version_info.micro)+'\n'

    print("[bold grey35]"+intro)

    # #- Manually capture the "help" arguments and process last
    # help = None
    # args = sys.argv
    # for i in range(len(sys.argv)):
    #     if any([sys.argv[i] == h for h in ['-h', '--help']]) is True:
    #         help = i
    #         args = sys.argv[:i]
    #         break

    #- Argument parser
    parser = argparse.ArgumentParser(
        prog = 'pf',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    #subparsers = parser.add_subparsers()

    commands = {
        'init': pf.init,
    }

    # commandsStr = ''
    # i=0
    # while i<len(commands.keys()):
    #     commandsStr += list(commands.keys())[i]+', '
    #     if len(commandsStr.split('\n')[-1]) > 70:
    #         commandsStr+= '\n'
    #     i+=1
    #
    # commandsStr = commandsStr.rstrip(', ')

    commandsStr = ''

    for command in commands.keys():
        commandsStr+= '{0:<30}'.format(command+":")
        if commands[command].__doc__:
            commandsStr+= commands[command].__doc__+'\n\n'
        else:
            commandsStr+= '\n\n'


    parser.add_argument(
        'command',
        metavar='command',
        help=textwrap.dedent("The command to be executed.  Valid commands are:\n\n"+commandsStr),
        choices=commands
    )

    #- Global [<options>] arguments

    parser.add_argument('--debug',
                        help="Print out additional debug information",
                        action='store_true'
                       )

    #- parse args manually to find command args
    args=sys.argv
    i = 0
    while any([c == args[i] for c in commands]) is False:
        i += 1
        if i >=len(args):
            parser.print_help()
            sys.exit()

    opt_args = args[1:i]
    addArgs = args[i:]

    #- Manually parse the optional arguments
    debug = False
    for i in range(len(opt_args)):
        if opt_args[i] == '--debug':
            debug = True
            i+=1

        elif any([opt_args[i] == command for command in commands.keys()]):
            break


    args = parser.parse_args(opt_args+[addArgs[0]])

    logger.setLevel("DEBUG" if debug else "INFO")

    logger.debug('main args:'+str(opt_args+[addArgs[0]]))
    logger.debug('main addArgs:'+str(addArgs))

    commandList = list(commands.keys())


    cl = CommandLine(addArgs[1:])

    CL_FUNCTION_MAP = {
        commandList[0]: cl.init,
    }

    cl_func = CL_FUNCTION_MAP[addArgs[0]]
    cl_func()

    print("")

if __name__ == '__main__':
    main()