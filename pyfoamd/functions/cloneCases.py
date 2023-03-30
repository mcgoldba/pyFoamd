from pyfoamd.functions import cloneCase, listCases

def cloneCase(srcPath, destPath, sshSrc=None, sshDest=None):
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

    cases = listCases(srcPath)

    for casePath in cases:
        cloneCase(casePath, 
            destPath / casePath.relative_to(srcPath),
            sshSrc=sshSrc,
            sshDest=sshDest)