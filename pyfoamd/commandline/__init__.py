import pyfoamd.functions as pf
import warnings
import IPython
import argparse
from configparser import ConfigParser
from pyfoamd import userMsg

# import config

import logging
logger = logging.getLogger('pf')

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
        case = pf.init()

        logger.debug(f"case: {case}")

        #- store the case data as json file:
        #TODO:  This doesn't work
        
        pf.writeParams(case, '_case.json')

    def edit(self):
        """
        Edit the case contents with an interactive (IPython) console.

        Console automatic imports:
            `import pyfoamd.functions as pf`
            `case = pf.readCaseFromCache()`

        """
        import pyfoamd.functions as pf
        try:
            case = pf.readCaseFromCache()
        except FileNotFoundError:
            warnings.warn("No cached case data found.  Run 'pf init'"\
            " before 'pf edit'.")
            case = None

        IPython.embed()
        if case is not None:
            pf.writeParams(case, '_case.json')

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


