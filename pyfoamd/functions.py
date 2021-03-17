import sys

#- Check the python version:
if  sys.version_info < (3,7):
    sys.exit('Sorry, Python < 3.7 is not supported.')


from pyfoamd.types import ofDictFile, ofDict, ofNamedList, ofNamedSplitList, ofIntValue, ofFloatValue, ofStrValue, ofBoolValue, ofDimensionedScalar, ofVector, ofNamedVector, ofDimensionedVector, TAB_STR


import os
from shutil import copyfile
import re
import math
#import numpy as np
import subprocess
import tempfile

from rich import print
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
        level="NOTSET",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

from rich.traceback import install
install()

#Define padding for blockMeshDict
PAD = 1 / 12 / 3.281 # 1 inch

#class PyFoamd:

#    def __init__(self, modifying_per, add_args):
#        self.add_args = add_args  #additional, unprocessed arguments
#        self.modifying_per = modifying_per
#        #self.n_ops = n_ops
#        #self.wd = PROJECTS_DIR+str(op_args.number)+r'/2-work/2-mesAndSim/of/'
#        self.wd = None
#        self.ui = None
#        self.of_case_dir = None
#        self.active_sim = None
#        self.op_scn = None
#        self.per_metadata_file = None
#          #self.arg_start = None

#def initialize(self):
#
#    #- '<command>' argument
#    CFD_FUNCTION_MAP = {'init': self.init,
#                        'activate': self.activate,
#                        'make': self.makeCase,
#                        'view': self.view,
#                        'vis': self.vis,
#                        'monitor': Processing(self.modifying_per, self.add_args[1:]).monitor,
#                        'clone':  self.clone,
#                        'getResults': self.copyResultsFromServer,
#                        'geom': self.geom,
#                        'scp': self.scp,
#                        'open': self.open
#                       }
#
#    parser = argparse.ArgumentParser(
#        prog='per cfd',
#        usage='''per cfd [<options>] <command> [<args>]
#d command options:
#"    "+str([c for c in CFD_FUNCTION_MAP.keys()]),
#        description='A set of commands for working with CFD projects.'
#    )
#
#    #- Global cfd [<options>] arguments
#    #parser.add_argument('-d', '--directory',
#    #                    help="OpenFOAM case directory name used to set the active directory. The default value is 'of'.",
#    #                    type=str,
#    #                    const='sim01',
#    #                    default='sim01',
#    #                    action='store',
#    #                    nargs='?'
#    #                   )
#
#     #- Manually count the number of optional arguments (which start with an '-')
#     n_ops_cfd = 0
#     while (sys.argv[1+self.n_ops+n_ops_cfd].startswith('--') is True or
#            sys.argv[1+self.n_ops+n_ops_cfd].startswith('-') is True):
#         n_ops_cfd += 1
#         #- break the search if the default help arguments are given
#         if (sys.argv[n_ops_cfd] == '--help' or
#             sys.argv[n_ops_cfd] == '-h'):
#             parser.print_help()
#             break
#
#     #- Parse the optional arguments first
#     op_args_cfd = None
#     if n_ops_cfd > 0:
#         op_args_cfd = parser.parse_args(sys.argv[2+self.n_ops:self.n_ops+n_ops_cfd+3])
#     else:
#         #parse only the optional arguments with default values
#         op_args_cfd = parser.parse_args(['--number'])
#
#    [args_cfd, self.add_args] = parser.parse_known_args(self.add_args)
#
#    h = Handler(self.modifying_per, [])
#
#    self.wd = os.path.join(
#        PROJECTS_DIR,
#        str(self.modifying_per),
#        '2-work',
#        '2-meshAndSim'
#    )
#
#    self.per_metadata_file = os.path.join(
#            PROJECTS_DIR,
#            str(self.modifying_per),
#            ".per",
#            str(self.modifying_per)+".per"
#    )
#
#    try:
#        self.active_sim = h.lookupValue(
#            self.per_metadata_file,
#            'cfd_active_sim'
#        )
#        self.of_case_dir = os.path.join(self.wd, self.active_sim)
#    except ValueError:
#        self.of_case_dir = os.path.join(self.wd, 'sim01') #Set as default sim name
#
#    #- Populate the operating scenario based on the sim name:
#    self.op_scn = int(self.active_sim[-2:]) #Assumes 2 digits for opScn
#
#
#
#    #- '<command>' argument
#    #CFD_FUNCTION_MAP = {'init': self.init,
#    #                    'activate':  self.activate,
#    #                    'make': self.makeCase,
#    #                    'view': self.view,
#    #                    'vis': self.vis,
#    #                    'monitor': Processing(self.modifying_per, self.add_args[1:]).monitor,
#    #                    'clone':  self.clone,
#    #                    'getResults': self.copyResultsFromServer,
#    #                    'geom': self.geom
#    #                   }
#
#    parser.add_argument('command',
#                        choices=CFD_FUNCTION_MAP.keys(),
#                        help="The cfd operation to perform.  Valid options are"+str(CFD_FUNCTION_MAP.keys())
#                        )
#
#    [args, self.add_args] = parser.parse_known_args(self.add_args)
#
#    #self.arg_start = self.n_ops+n_ops_cfd+4
#
#    cfd_func = CFD_FUNCTION_MAP[args.command]
#    cfd_func()

######################## Public Member Functions ############################


#def cloneSim():
#
#    import shutil
#    import re
#
#    #- Parse 'clone sim' specific arguments
#
#    parser = argparse.ArgumentParser(
#        description= 'Clone an existing simulation into a new OpenFOAM case directory.'
#    )
#
#    if (len(self.add_args) not in (0,1,2)):
#        log.error("Wrong number of arguments provided.\nThe proper syntax is:\n\t 'per cfd clone sim <src> <destination>")
#    elif (len(self.add_args) == 2):
#        if((os.path.isdir(os.path.join(self.wd, self.add_args[0]))) is False):
#            log.error("Specified source directory does not exist:\n\t"+os.path.join(self.wd, self.add_args[0]))
#            sys.exit()
#
#    rootDir = self.wd
#    srcDir = ''
#    destDir = ''
#    if (len(self.add_args) == 1):
#        srcDir = os.getwd()
#        destDir = os.path.join(rootDir, self.add_args[0])
#    elif (len(self.add_args) == 0):
#        srcDir = os.getwd()
#        n = re.findall('[0-9]+', os.path.split(os.getwd())[-1])[-1]
#        m = int(n)+1
#        destDir = os.path.join(self.wd, 'sim'+str(m).zfill(2))
#    else:
#        srcDir = os.path.join(rootDir, self.add_args[0])
#        destDir = os.path.join(rootDir, self.add_args[1])
#    n = 1
#    newDir = destDir
#    while (os.path.isdir(newDir)):
#        if n > 99:
#            log.error("Could find a suitable simulation name.")
#            raise
#        n+=1
#        newDir = os.path.join(rootDir, 'sim{:02d}'.format(n))
#
#    if (newDir != destDir):
#        log.warning("Specified destination directory "+destDir+" already exists. Cloning into next available directory: "+newDir)
#
#    print("Cloning case files from "+pcolor(os.path.split(srcDir)[-1],1)+' to '+pcolor(os.path.split(newDir)[-1],1))
#
#    #destDir = os.path.join(destDir, newDir)
#
#    excludeDirs = [['constant', 'polyMesh'],['constant', 'triSurface']]
#
#    #- Exclude all processor and reconstructed time directories (other than
#    #  '0')
#    excludeRe = [
#        r'processor.*',
#        r'0*([1-9]\d+|[2-9])'
#        r'postProcessing',
#        r'viz_scenes',
#        r'VTK',
#    ]
#
#    copyDirs = ['0', 'system']
#
#    #Update the current case directory
#    os.getwd() = destDir
#
#
#    #Copy the template to the destination directory
#    self.init()
#
#    #if not os.path.exists(newDir):
#    #    os.mkdir(newDir)
#
#    #- Copy specific files from the srcDir
#    for file in os.listdir(srcDir):
#        #for regex in excludeRe:
#        #    if re.search(file, regex):
#        #        copy=False
#        if os.path.isfile(file):
#            shutil.copy2(file, destDir)
#            continue
#        if any([copyDir == file for copyDir in copyDirs]):
#            shutil.copytree(
#                os.path.join(srcDir, file),
#                os.path.join(destDir, file),
#                dirs_exist_ok=True
#            )
#            continue
#        if file == 'constant':  #Special copy for files only
#            for f in os.listdir(os.path.join(srcDir, file)):
#                if os.path.isdir(os.path.join(srcDir,file,f)):
#                    break
#                shutil.copy2(
#                    os.path.join(srcDir,file,f),
#                    os.path.join(destDir, "constant")
#                )
#         if copy is True:
#             print(file)
#             for i in range(len(excludeList)):
#                 excludePath = ''
#                 for directory in excludeList:
#                     if excludeList == file:
#                         copy=False
#
#        #if copy and os.path.isfile(file):
#            #shutil.copy(
#            #    os.path.join(srcDir, file),
#            #    os.path.join(destDir, file)
#            #)
#            #shutil.copytree
#
#def cloneStudy():
#    self.__notImplemented


def getLatestTime(directory):

    #- Get the latest time directory
    directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    latestTime = '0'
    for directory in directories:
        name = directory.replace('/', '')
        if name.isdigit() is True:
            if int(name) > int(latestTime):
                latestTime = name

    return directory

def appendBlockEntry(value, blockList=None, lineNum=None, searchValues=False):
    if blockList != None:
        __appendBlockEntryWithBlockName(value, blockList, searchValues=searchValues)
    elif lineNum != None:
        __appendBlockEntryWithLineNum(value, lineNum, searchValues=searchValues)
    else:
        log.error("One of 'blockList' or 'lineNum' must be specified to indicate the location to insert the dictionary entry.")

def replaceEntry(ofValue, rType='singleLine', silent=False):
    #- Base function for ofDict replacements
    #- rType = Replacement type.  One of:  ['string', 'singleLine']

    file = os.path.join(
            os.getcwd(),
            ofValue.location,
            ofValue.filename
    )

    #- Check if the file exists
    open(file)

    copyfile(file, file+"_old")

    if rType == 'string':
        found = __replaceStringEntry(
            ofValue.name,
            ofValue.value,
            file,
            silent=silent
        )
    elif rType == 'singleLine':
        #found = __replaceSingleLineEntry(
        #    ofValue.name,
        #    ofValue.value,
        #    ofValue.asString(),
        #    file,
        #    silent=silent
        #)
        found = __replaceSingleLineEntry(
            ofValue,
            file,
            silent=silent
        )
    else:
        raise ValueError("Unrecognized replace type: "+str(rType))

    if found == False:
        copyfile(file+"_old", file)
        raise ValueError("Key "+ str(ofValue.name)+ \
                     " not found in file:  "+ \
                     os.path.join(ofValue.location,ofValue.filename)+'\n')

def removeEntry(file, blockList, searchValues=False):
    #- Removes lists or dicts in an OpenFOAM dictionary that are split between
    #   many lines.
    #- blockList = list heiarchy to be searched
    #-   e.g.  ['geometry', 'wetwell'] removes everything within:
    #-      geometry{ wetwell{*delete_everything_here}}
    #- searchValues = switch to search within a line for block start / stop
    #-  (not yet implemented)

    entryName = blockList[len(blockList)-1]

    print("Deleting entry '"+entryName+"' in file: "+file)

    try:
        start, stop = __ofDictFindBlockEntryStartStop(
            file,
            blockList,
            searchValues=searchValues
        )
    except:
        print("\tBlock entry '"+entryName+"' not found.  Nothing to delete.")
        return None

    #- Correct start and stop locations to delete entry including names and
    #   brackets or parenthesis
    start -= 2
    stop+=1

    file = os.path.join(os.getwd(), file)

    if start>= stop:
        print("\tNo lines to delete.")
    else:
        print("\tDeleting values for block '"+entryName+"', between lines "+str(start+1)+" and "+str(stop)+".")
        #- delete lines in file
        with open(file, 'r+') as new:
            lines = new.readlines()
            del lines[start:stop]
            new.seek(0)
            new.truncate()
            new.writelines(lines)



    return start # return the line where the block ends, so values can be
                 # written here with __ofDictAppendBlockEntryWithLineNum

def removeBlockEntries(file, blockList, searchValues=False):
    #TODO:  Merge this method with __ofDictRemoveBlockEntry() (only 2 lines are
    #  different)
    #- Removes entries in an OpenFOAM dictionary block
    #- blockList = list heiarchy to be searched
    #-   e.g.  ['geometry', 'wetwell'] removes everything within:
    #-      geometry{ wetwell{*delete_everything_here}}
    #- searchValues = switch to search within a line for block start / stop
    #-  (not yet implemented)

    print("Deleting block '"+blockList[len(blockList)-1]+"' in file: "+file)

    start, stop = __ofDictFindBlockEntryStartStop(
        file,
        blockList,
        searchValues=searchValues
    )

    file = os.path.join(os.getwd(), file)


    if start>= stop:
        print("\tNo lines to delete.")
    else:
        print("\tDeleting values for block '"+blockList[len(blockList)-1]+"', between lines "+str(start+1)+" and "+str(stop)+".")
        #- delete lines in file
        with open(file, 'r+') as new:
            lines = new.readlines()
            del lines[start:stop]
            new.seek(0)
            new.truncate()
            new.writelines(lines)



    return start # return the line where the block ends, so values can be
                 # written here with __ofDictAppendBlockEntryWithLineNum




def readOFDictFile(file):

    from of.ofTypes import ofDictFile, ofDict, ofNamedList, ofIntValue, ofFloatValue, ofStrValue

    #- Function assumes:
    #   - All entries start on a new line
    #   - Comments on line after C++ code are ignored

    pyOFDict = ofDictFile(os.path.basename(file), [])

    def functionSwitcher(status):
        switcher = {
            'commentedBlock': __getOFDictCommentLineType,
            'comment': None,
            'includeLine': None,
            'empty': None,
            'commentedBlockEnd':  __getOFDictReadLineType,
            'list': __getOFDictValueType,
            'dict': __getOFDictValueType,
            'value': __storeOFDictValue,
            'multiLineUnknown': __getOFDictEntryType,
            'dictName': __newOFDictDict,
            'listName': __newOFDictList,
            'multiLineValue': __appendOFDictEntry,
            'multiLineEntryStart': __storeOFDictMultiLineEntryName,
            'singleLineSingleValuedEntry': __storeOFDictSingleLineSingleValuedEntry
        }
        return switcher.get(status, __getOFDictReadLineType)
def __appendBlockEntryWithBlockName(
    ofValue,
    blockList,
    searchValues=False
):

    if ofValue.location is None or ofValue.filename is None:
        raise ValueError("The 'location' and 'filename' of the OpenFOAM type must be specified to update the dictionary file.")

    file = os.path.join(
            os.getcwd(),
            ofValue.location,
            ofValue.filename
    )

    #- Check if the file exists
    open(file)

    copyfile(file, file+"_old")

    _, stop = __ofDictFindBlockEntryStartStop(
        ofValue.location + ofValue.filename,
        blockList,
        searchValues=searchValues
    )

    if hasattr(ofValue, 'name') is True and ofValue.name is not None:
        print("Appending entry '"+ofValue.name+"' into block "+blockList[len(blockList)-1]+" at line "+str(stop)+" of file: "+ofValue.location + ofValue.filename)
    else:
        print("Appending unnamed entry into block "+blockList[len(blockList)-1]+" at line "+str(stop)+" of file: "+ofValue.location + ofValue.filename)

    try:
        with open(file+"_old") as old, open(file, "w") as new:
            for i, line in enumerate(old):
                if i == stop:
                    #- build insert string with indents
                    insertStr = ofValue.asString().split('\n')
                    for i in range(len(blockList)):
                        for j in range(len(insertStr)):
                            insertStr[j] = TAB_STR + insertStr[j]
                    #- Write lines
                    for l in insertStr:
                        new.write(l+'\n')
                    new.write(line)
                else:
                    new.write(line)
    except:
        copyfile(file+"_old", file)
        raise

######################## Private Member Functions ###########################

def __replaceStringEntry(key, val, file, silent=False):
    #- Use "__ofDictReplaceEntry(...,rType='string')" instead
    found = False

    with open(file+"_old", 'r') as old, open(file, 'w') as new:
        for line in old:
            #if key in line:
            if key in line:
                found = True
            new.write(line.replace(key, str(val)))


    return found

def __replaceSingleLineEntry(ofValue, file, silent=False):
    #- Use "__ofDictReplaceEntry(...,rType='singleLine')" instead
    #- Replaces a single line based on OpenFOAM variable name
    #- WARNING: Does NOT search for variables of same name defined within
    #  different blocks.  A new nethod will need to be created if this search
    #  is needed.
    found = False

    key = ofValue.name
    string = ofValue.asString()
    logStr = ofValue.valueStr

    with open(file+"_old", 'r') as old, open(file, 'w') as new:

        for line in old:
            #if key in line:
            #if line.strip().startswith(key) is True:
            if (len(line.split()) > 0 and
                line.split()[0] == key):
                #- Ensure that the found key is a single lined value
                if line.split('//')[0].rstrip()[-1] != ';':
                    new.write(line)
                    continue
                #- Save any line comments:
                comment = ""
                if '//' in line:
                    commentList = line.split('//')[1:]
                    for c in commentList:
                        comment+='//'+c
                #- Count the number of leading spaces
                nSpaces = len(line) - len(line.lstrip(" "))
                pre = ''
                for _ in range(nSpaces):
                    pre += ' '
                new.write(pre+string+comment)
                found=True
                if not silent:
                    relPath = file[len(os.getcwd()):]
                    print("'"+str(key)+"' changed to '"+logStr+"' in file:  "+relPath)
                #print('in "if": '+str(key)+', '+str(val))
            else:
                new.write(line)
                #print('in "else": '+str(key)+', '+str(val))

    return found

def __findBlockEntryStartStop(file, blockList, searchValues=False):
    #TODO:  Account for the case of opening anf closing parenthesis or barackets
    #  on the same line.
    relPath = file
    file = os.path.join(os.getcwd(), file)

    if os.path.isfile(file) is False:
        raise FileNotFoundError(file)


    copyfile(file, file+"_old")

    start = 0
    stop = 0

    try:
        old = open(file, 'r')
        for line in old:
            stop+=1
        old.seek(0)
        lines = old.readlines()

        if stop <= 0:
            raise Exception('File is empty: '+file)

        for block in blockList:
            #- initialize variables to be defined below
            openStr = None
            closeStr = None

            #old.seek(start-1)

            # while 'block' is not the first word in the line:
            while True:
                lineList = lines[start].strip().split(" ")
                if block == lineList[0]:
                    break
                start += 1
                if start >= stop:
                    raise Exception("End of file '"+relPath+"' reached without finding a match for block '"+str(block)+"'.")
            for i in [0,1]: #search line with block name and next line
                if len(lines[start+i].split(" ")) > 1:
                    #- Search for opening and closing of block on the same line
                    for openChar, closeChar in zip(['(', '{'],[')', '}']):
                        if openChar in lines[start+i]:
                            openStr = openChar
                            closeStr = closeChar
                            start = start+i
                            break
                            if closeStr in lines[start+i]:
                                 print("Warning:  No values found matching block '"+block+"' within "+file)
            #- If block is not opened on same line assume it is opened on next
            #  line:
            if not openStr:
                start+=1
                openStr = lines[start].lstrip()[0]

            if openStr == '(':
                closeStr = ')'
            elif openStr == '{':
                closeStr = '}'
            else:
                raise Exception("Unexpected file format enountered at line "+str(start+1)+" of "+file)
            stop = start

            nOpenStr = 1
            nCloseStr = 0

            while nOpenStr > nCloseStr:
                if stop >= len(lines)-1:
                    raise Exception("End of file '"+relPath+"' reached without terminating block.")
                stop+=1
                nOpenStr+= lines[stop].count(openStr)
                nCloseStr+= lines[stop].count(closeStr)

        start+=1
    except:
        copyfile(file+"_old", file)
        raise

    return start, stop


def __appendBlockEntryWithLineNum(
    ofValue,
    lineNum,
    searchValues=False
):
    #- Not complete, use __ofDictAppendBlockEntryWithBlockName() instead

    file = os.path.join(
            os.getcwd(),
            ofValue.location,
            ofValue.filename
    )

    #- Check if the file exists
    open(file)

    copyfile(file, file+"_old")
    printName = ofValue.name or ""
    print("Appending block '"+str(printName)+"' at line number "+str(lineNum)+" of file: "+os.path.join(ofValue.location, ofValue.filename))

    try:
        with open(file+"_old") as old, open(file, "w") as new:
            for i, line in enumerate(old):
                if i == lineNum:
                    new.write(ofValue.asString())
                    new.write(line)
                else:
                    new.write(line)
    except:
        copyfile(file+"_old", file)
        raise




    def __argSwitcher(func, line, ofType):
        switcher = {
            __getOFDictReadLineType: len(line.split(" ")),
            __storeOFDictValue: (ofType,
                                      line[1:].remove('{()}').split(" ")
                                     )
        }
        return switcher.get(func, line.remove['()'], )

    status = 'start'
    ofType = None
    prevLine = None
    lineStatus = 'read'
    level = 0
    with open(file, 'r') as f:
        for line in f:
            if line.startswith(('//', '#')):
                #- Ignore line comments and includes
                continue
            if lineStatus == 'endMultiLine':
                #- Determine how to interpret the previous line
                [status, lineStatus] = __getOFDictMultiLinePreviousType(line)
            lineStatus = 'read'
            count = 0
            while lineStatus != 'end':
                if lineStatus == 'endMultiLine':
                    prevLine = line
                    break
                count += 1
                if count >= 100: #prevent infinite loop in case of error
                    raise Exception("Maximum number of loops reached.")
                func = functionSwitcher(status)
                if func is not None:
                    [status, lineStatus] = func(__argSwitcher(func, line, ofType))



def __getOFDictCommentLineType(startsWith):
    switcher = {
        '*/': ['commentedBlockEnd', 'end']
    }
    return [switcher.get(startsWith, 'commentedBlock'), 'end']

def __getOFDictValueType(startsWith):
    switcher = {
        '(': 'list',
        '{': 'dict'
    }
    return [switcher.get(startsWith, 'value'), 'read']

def __getOFDictMultiLineEntryType(line):
    switcher = {
        '(': 'list',
        '{': 'dict',
        'FoamFile': 'fileInfoStart'
    }
    return [switcher.get(line, 'value'), 'read']

def __ofMultiLineEntryReadNextLine(line):
    pass

def __getOFDictReadLineType(length):
    switcher = {
        0: ['empty', 'end'],
        1: ['multiLineUnknown', 'readMultiLine'],
        2: ['singleLineSingleValuedEntry', 'read']
    }
    return switcher.get(length, ['singleLineMultiValuedEntry', 'read'])

def __storeOFDictValue(line):
    pass

def __appendOFDictValue(line):
    pass

def __storeOFNamedListValue(line):
    pass

def __getOFDictMultiLinePreviousType(line):
    switcher = {
        '{': 'dictName',
        '(': 'listName'
    }
    return [switcher.get(line, 'multiLineValue'), 'read']

def __storeOFDictSingleLineSingleValuedEntry(line):
    values = line.split(" ")
    if len(values) != 2:
        raise Exception("Not able to process line format.")
    if values[1].isnumeric() is True:
        if '.' in values[1]:
            pyOFDict.add(ofFloatValue(values[0], values[1]))
        else:
            pyOFDict.add(ofIntValue(values[0], values[1]))
    elif values[1] in OF_BOOL_VALUES:
        pyOFDict.add(ofBoolValue(values[0], values[1]))
    else:
        pyOFDict.add(ofStrValue(values[0], values[1]))

    return ['newLine', 'end']
