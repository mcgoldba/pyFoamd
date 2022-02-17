def isOFDict(file):
    """
    Checks if the argument file is an OpenFOAM dictionary file.  It is assumed
    that all OpenFOAM dictionary files start with the first uncommented line as
    'FoamFile\n'

    Parameters:
        file (str or Path):  The path of the file to test.
    """

    # -Convert to string in case of Path object
    file = str(file)

    isOFDict = False

    with open(file) as f:
        lines = f.readlines

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
