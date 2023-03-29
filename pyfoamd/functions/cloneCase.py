from pyfoamd.functions import isCase
from pyfoamd import userMsg, getPyFoamdConfig
from pathlib import Path
import shutil
from distutils.dir_util import copy_tree


def cloneCase(src, dest, ssh=None):
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
        ssh [str]:  If copying to a remote location, the string of login details  
                for the remote host in sh format (e.g. 'marc@my.remote.com')

    """

    if not isCase(src):
        userMsg("Specified src is not a vlaid OpenFOAM case", 'ERROR')
    
    #-Copy all cloned files to temporary directory to allow for a single call to 
    # 'subprocess'

    srcPath = Path(src)

    tmpPath = srcPath.parent / srcPath.name+'_tmp'

    tmpPath.mkdir()
    def _copyObj(src, dest):
        for obj in src.iter_dir():
            if obj.is_dir():
                if obj.name.startswith('processor'):
                    continue
                if obj.name == 'constant': #handle constant dir seperately
                    (tmpPath / 'constant').mkdir()
                    for obj_ in obj.iter_dir: #iterate items in 'constant' dir
                        if obj_.is_dir():
                            if (obj_.name == 'polyMesh' or
                            obj_.name == 'extendedFeatureEdgeMesh'
                            ):
                                continue
                            (dest / 'constant' / obj.relative_to(src)).mkdir()
                            _copyObj(obj_, dest / 'constant')
                        shutil.copy(obj_, tmpPath / 'constant')
                (dest / obj.relative_to(src)).mkdir
                _copyObj(obj_, dest / (dest / obj.relative_to(src)))
            else:
                if obj.stat().st_size > int(getPyFoamdConfig('dict_filesize_limit')):
                    continue
                shutil.copy(obj, dest)
    
    _copyObj(srcPath, tmpPath)


