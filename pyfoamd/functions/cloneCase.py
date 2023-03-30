from pyfoamd.functions import isCase
from pyfoamd import userMsg, getPyFoamdConfig
from pathlib import Path
import shutil
from distutils.dir_util import copy_tree
import logging
import tempfile
import subprocess

logger = logging.getLogger('pyfoamd')


def cloneCase(srcPath, destPath, sshSrc=None, sshDest=None):
    """
    Clone the setup files of an OpenFOAM case to a new directory.

    The cloned case excludes any files and directories that include large
    amounts of data.

    The excluded directories are:
        - time directories other than '0/'
        - processor directories
        - 'constant/polyMesh'
        - 'constant/extendedFeatureEdgeMesh'
    In addition, any file with size greater than the pyfoamd file size limit is 
    ommitted.

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

    if not isCase(srcPath):
        userMsg("Specified src is not a valid OpenFOAM case", 'ERROR')
    
    #-Copy all cloned files to temporary directory to allow for a single call to 
    # 'subprocess'


    srcPath = Path(srcPath)

    tmpPath = Path(tempfile.mkdtemp())
    # tmpPath = srcPath.parent / (srcPath.name+"_tmp")

    logger.debug(f"temp directory: {tmpPath}")

    # tmpPath.mkdir()

    tabStr = ""

    def _copyObj(src, dest, top=False, tabStr=""):
        tabStr += "    "
        for obj in src.iterdir():
            logger.debug(f"{tabStr}Parsing {obj}")
            if obj.is_dir():
                if top and obj.name.startswith('processor'):
                    continue
                if top: # ignore time directories
                    try:
                        float(obj.name)
                        if obj.name != "0":
                            continue
                    except ValueError:
                        pass
                if top and obj.name == 'constant': #handle constant dir seperately
                    logger.debug(f"{tabStr}Making directory: {(dest / 'constant')}")
                    (dest / 'constant').mkdir()
                    for obj_ in obj.iterdir(): #iterate items in 'constant' dir
                        if obj_.is_dir():
                            logger.debug(f"{tabStr}Parsing object name {obj_.name}")
                            if (obj_.name == 'polyMesh' or
                            obj_.name == 'extendedFeatureEdgeMesh'
                            ):
                                continue
                            logger.debug(f"{tabStr}Making directory: {(dest / 'constant' / obj_.name)}")
                            (dest / 'constant' / obj_.name).mkdir()
                            _copyObj(obj_, (dest / 'constant' /obj_.name), tabStr=tabStr)
                        else:
                            logger.debug(f"{tabStr}Copying {obj_} to {(dest / 'constant')}")
                            shutil.copy(obj_, (dest / 'constant'))
                if not (dest / obj.name).is_dir():
                    logger.debug(f"{tabStr}Making directory: {(dest / obj.name)}")
                    (dest / obj.name).mkdir()
                    _copyObj(obj, (dest / obj.name), tabStr=tabStr)
            else:
                if obj.stat().st_size > int(getPyFoamdConfig('dict_filesize_limit')):
                    continue
                logger.debug(f"{tabStr}Copying {obj} to {dest}")
                shutil.copy(obj, dest)
    
    _copyObj(srcPath, tmpPath, top=True)

    cmd = 'cp'

    if sshSrc:
        fromStr = f'{sshSrc}:{str(tmpPath)}/*'
        cmd = 'ssh'
    else:
        fromStr = str(tmpPath)+'/*'
        
    if sshDest:
        toStr = f'{sshDest}:{str(destPath)}'
        cmd = 'ssh'
    else:
        toStr = str(destPath)

    cmdStr = f'{cmd} -r {fromStr} {toStr}'
    
    logger.info(f"Copy case from {srcPath} to {toStr}")

    subprocess.check_call(cmdStr, shell=True)
    
    shutil.rmtree(tmpPath)