import pyfoamd.functions as pf
import warnings
import IPython
from IPython.terminal.prompts import Prompts, Token
from code import InteractiveConsole
import atexit
import os
import argparse
from configparser import ConfigParser
from pyfoamd import userMsg
from pathlib import Path
from traitlets.config import Config # for IPython config
# import config
import sys

import logging
logger = logging.getLogger('pf')

class PyFoamdConsole(InteractiveConsole):
    def __init__(*args, **kwargs):
        InteractiveConsole.__init__(*args, **kwargs)

class CommandLine:
    def __init__ (self, addArgs, configFilepath):
        self.configFilepath = configFilepath
        self.config = ConfigParser()
        self.config.read(configFilepath)
        self.prog = 'pf'
        self.addArgs = addArgs

    def init(self):
        """
        Read an OpenFOAM case and store as a Python dictionary.
        """
        self.prog+= ' init'

        parser = argparse.ArgumentParser(prog=self.prog)

        parser.add_argument('-path',type=str, nargs='?',
                            help='The path of the OpenFOAM case to parse.')

        args = parser.parse_args(self.addArgs)
        
        if args.path is None:
            case = pf.init()
        else:
            case = pf.init(path=args.path)

        logger.debug(f"case: {case}")

        #- store the case data as json file:
        if case is not None:
            case.save()

    def edit(self):
        """
        Edit the case contents with an interactive (IPython) console.

        Console automatic imports:
            `import pyfoamd.functions as pf`
            `import pyfoamd.types as pt`
            `case = pf.load()`

        """

        #TODO:  Is this method loading a case multiple times?

        self.prog+= ' edit'

        parser = argparse.ArgumentParser(prog=self.prog)

        parser.add_argument('-ipython',type=bool, nargs=1, default=True,
                            help='If `True`, starts an IPython console instead \
                                of a Python console.')


        args = parser.parse_args(self.addArgs)

        # import pyfoamd.functions as pf
        # import pyfoamd.types as pt
        # try:
        #     case = pf.load()
        # except FileNotFoundError:
        #     userMsg("No cached case data found.  Run 'pf init'"\
        #     " before 'pf edit'.", "WARNING")
        #     case = None

        case = pf.load()

        #TODO:  Automatically save case before exiting or maybe automatically
        #          save case everytime the ofCase is modified?
        if args.ipython:

            c = Config()
            c.TerminalInteractiveShell.confirm_exit = False
            c.TerminalIPythonApp.display_banner = False
            c.InteractiveShellApp.exec_files = [
                str(Path(__file__).parent /  '_iPython_env.py')
            ]

            # IPython.embed(header="", config=c, prompt=PyFoamdPrompt)
            IPython.start_ipython(argv=[], config=c)

            logger.debug(f"case: {case}")
            # if case is not None:
            #     # pf.writeParams(case, '_case.json')
            #     # pf.writeCase(case)
            #     case.save()
        else:  # Use a customized version of the standard Python console
            
            def atExitCommands():
                try:
                    print("Saving case to PyFoamd cache (i.e. as a JSON object)")
                    print(locals())
                    locals()['case'].save()
                finally:
                    sys.exit()
            
            # atexit.register(atExitCommands)

            exit = atExitCommands

            #exit = atExitCommands



            # namespace = {'case':case}
            console = PyFoamdConsole(locals=dict(globals(), **locals()))
            console.interact()

            atexit.unregister(atExitCommands)


    def setConfig(self):
        """
        Set details of the PyFoamd configuration, specified in 'config.ini'
        """
        self.prog+= ' setConfig'

        parser = argparse.ArgumentParser(prog=self.prog)

        parser.add_argument('key',type=str, nargs=1,
                            help='The configuration variable to be set.')
    
        parser.add_argument('value', nargs=1,
                        help='The value to which the variable is to be set.')

        args = parser.parse_args(self.addArgs)

        if 'user' in self.config.keys():
            self.config['user'].update({args.key[0]: args.value[0]})
        else:
            self.config['user'] = {args.key[0]: args.value[0]}

        with open(self.configFilepath, 'w') as configFile:
            self.config.write(configFile)

        userMsg(f"Setting '{args.key[0]}' config option" 
            f" to '{args.value[0]}'.", "INFO")
    
    def write(self):
        """
        Save the case, and overwrite the existing OpenFOAM dictionary case with 
        values in the `ofCase`.  Saves existing case structure in cache for 
        backup.
        """
        case = pf.load()

        case.write()

