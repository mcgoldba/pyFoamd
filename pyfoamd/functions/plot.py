import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import re
import numpy as np

import logging
logger = logging.getLogger('pf')

def plot(relDataFile, xIndex=0, filter=None, workingDir=Path.cwd()):

    logging.getLogger('pf').setLevel(logging.DEBUG)

    dataFile = Path(workingDir) / relDataFile

    with open(dataFile) as f:
        line = f.readline()
        while line.strip().startswith('#'):
            prevline=line
            line=f.readline()

    header = prevline.lstrip('#').split()
    logger.debug(f"header: {header}")
    df = pd.read_csv(dataFile, comment='#', index_col=xIndex, sep='\t')
    logger.debug(f"columns: {df.columns}")
    df.columns = header[1:]

    xData = df.index.values

    data = df.values
    names = header
    del names[xIndex]

    if filter is not None:
        filteredNames = []
        filteredData = []
        for data_, name in zip(data.T, names):
            data_ = [v if isinstance(v, (float, int)) else 0 for v in data_]
            if re.search(name, filter):
               filteredNames.append(name)
               filteredData.append(data_)
        data = filteredData
        names = filteredNames

    for lineData, name in zip(data, names):
        logger.debug(lineData)
        plt.plot(xData, lineData, label = name)
    
    plt.xlabel(header[xIndex])
    plt.ylabel('Value')
    plt.title(Path(dataFile).name)

    plt.show()