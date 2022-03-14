import os
import logging

from pyfoamd.config import DICT_FILESIZE_LIMIT

logger = logging.getLogger('pyfoamd')

def _isOFDict(file):
    """
    Checks if the argument file is an OpenFOAM dictionary file.  It is assumed
    that all OpenFOAM dictionary files start with the first uncommented line as
    'FoamFile\n'

    Parameters:
        file (str or Path):  The path of the file to test.
    """

    # - Convert to string in case of Path object
    file = str(file)

    logger.debug(f"Checking file: {file}")

    isOFDict = False

    #- Skip large files
    if os.path.getsize(file) > DICT_FILESIZE_LIMIT:
        return isOFDict


    #- check for binary
    #  ref: https://stackoverflow.com/a/7392391
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    if is_binary_string(open(file, 'rb').read(1024)):
        return isOFDict    

    with open(file, encoding='utf8') as f:
        try:
            lines = f.readlines()
        except UnicodeDecodeError:
            return isOFDict



        blockComment = False
        # -Check for line or block comments
        for line in lines:
            if blockComment:
                if line.rstrip()[-2:] == '*/':
                    blockComment = False
                continue

            testStr = line.lstrip()[:2]
            if testStr == '//':
                continue
            elif testStr == '/*':
                blockComment = True
                continue
            else:
                if line.startswith('FoamFile'):
                    isOFDict = True
                break

    return isOFDict
