from pyfoamd.functions import cloneCase, listCases

import logging

logger = logging.getLogger('pyfoamd')


def cloneCases(srcPath, destPath, sshSrc=None, sshDest=None):
    """
    Clone all cases found in the srcPath to the destPath.

    Parameters:
    src [str or Path]:  The location of the source case.
    dest [str or Path]:  The destination to copy case files to.
    sshSrc [str]:  If copying from a remote location, the string of login details  
            for the remote host in sh format (e.g. 'marc@my.remote.com')
    sshDest [str]:  If copying to a remote location, the string of login details  
            for the remote host in sh format (e.g. 'marc@my.remote.com')
    """
        
    #- Note the sshSrc option currently isnt working because the src files need to
    # be accessed for more than just the subprocess command 

    # logger.setLevel(logging.DEBUG)

    cases = listCases(srcPath)

    for casePath in cases:
        logger.debug(f"Cloning case directory: {casePath}")

        (destPath / casePath).mkdir(parents=True)

        cloneCase(srcPath / casePath, 
            destPath / casePath,
            sshSrc=sshSrc,
            sshDest=sshDest)