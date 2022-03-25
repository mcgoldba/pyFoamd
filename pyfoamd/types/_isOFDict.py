import os
import logging
from pyfoamd import getPyFoamdConfig

#from pyfoamd.richLogger import logger
logger = logging.getLogger('pf')

def _isOFDict(file):
    """
    Checks if the argument file is an OpenFOAM dictionary file.  It is assumed
    that all OpenFOAM dictionary files start with a block comment header of the 
    form:

/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  6
     \\/     M anipulation  |
-------------------------------------------------------------------------------
Description
    {Description of file contents}...

\*---------------------------------------------------------------------------*/
    
    Previous impementation:

    It is assumed that all OpenFOAM dictionary files start with the first 
    uncommented line as 'FoamFile\n'

    Parameters:
        file (str or Path):  The path of the file to test.
    """


    # - Convert to string in case of Path object
    file = str(file)

    logger.debug(f"Checking file: {file}")

    isOFDict = False


    filesizeLimit = int(getPyFoamdConfig('dict_filesize_limit'))

    #- Skip large files
    if os.path.getsize(file) > filesizeLimit:
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

        #- Find start of first commented block
        for i, line in enumerate(lines):
            if line.startswith('/*'):
                break

        if i+7 < len(lines):
            commentedBlock = lines[i:i+7]

            if (commentedBlock[0].startswith(
'/*--------------------------------*- C++ -*----------------------------------')
            and commentedBlock[1].startswith(
                '  =========                 |')
            and commentedBlock[2].startswith(
                '  \\\\      /  F ield         |')
            and commentedBlock[3].startswith(
                '   \\\\    /   O peration     |')
            and commentedBlock[4].startswith(
                '    \\\\  /    A nd           |')
            and commentedBlock[5].startswith(
                '     \\\\/     M anipulation  |')
            ):
                isOFDict = True


        #- Previous implementation

        # blockComment = False
        # # -Check for line or block comments
        # for line in lines:
        #     if blockComment:
        #         if line.rstrip()[-2:] == '*/':
        #             blockComment = False
        #         continue

        #     testStr = line.lstrip()[:2]
        #     if testStr == '//':
        #         continue
        #     elif testStr == '/*':
        #         blockComment = True
        #         continue
        #     else:
        #         if line.startswith('FoamFile'):
        #             isOFDict = True
        #         break

    return isOFDict
