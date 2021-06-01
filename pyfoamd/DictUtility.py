import os
from shutil import copyfile

def __ofDictFindBlockEntryStartStop(file, blockList, searchValues=False):
    #TODO:  Account for the case of opening anf closing parenthesis or brackets
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

        if blockList is not None:

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
#                                if closeStr in lines[start+i]:
#                                    print("Warning:  No values found matching block '"+block+"' within "+file)
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
        else:  #Search top level.  Find end of file
            if len(lines) > 0:
                start = len(lines)-1
                stop = len(lines)-1
            else:
                start = 0
                stop = 0

    except:
        copyfile(file+"_old", file)
        raise

    return start, stop
