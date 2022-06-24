import subprocess
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import logging
import pyfoamd.types as pt
from pyfoamd.functions.getProbe import getProbe
logger = logging.getLogger("pf")

plt.style.use('ggplot')

# def monitor(time=None, supplement=None, workingDir=os.getcwd()):

#     commands = ['pfmonitor']
#     if time:
#         commands.append('-t')
#         commands.append(str(time))
#     if supplement:
#         commands.append('-s')
#         for s in supplement:
#             commands.append(str(s))

#     log.debug("commands: "+str(commands))
#     try:
#         subprocess.run(commands, cwd=workingDir)
#     except KeyboardInterrupt:
#         sys.exit(0)
#     # subprocess.call(commands, cwd=workingDir)

def monitor(values=['U', 'p'], time='latestTime', supplement=None, 
    workingDir=Path.cwd(), title=None):

    if title is None:
        title = Path(workingDir).name

    pauseTime = 3

    def updatePlot(x, y, plotData, identifier='', pauseTime=0.2,
    ylabel = None, title=None,legendName = None):
        if not plotData: # i.e. if plotData == []:
            print(f"Initializing plot for {ylabel}")
            plt.ion()
            fig = plt.figure(figsize=(6,3))
            ax = fig.add_subplot(1, 1, 1)
            plotData,  = ax.plot(x, y, label=legendName)
            plt.ylabel(ylabel)
            plt.xlabel("Time")
            plt.title(title)
            plt.legend()
            # plt.show()
        
        plotData.set_data(x, y)
        plt.xlim(np.min(x), np.max(x))

        logging.getLogger('pf').setLevel(logging.DEBUG)

        logger.debug(f"ylim: {plotData.axes.get_ylim()}")

        if ( all([np.isfinite(v) for 
            v in plotData.axes.get_ylim()])
        and (np.min(y) <= plotData.axes.get_ylim()[0]
        or np.max(y) >= plotData.axes.get_ylim()[1])):
            y[y > 1e8] = 0 # replace very large values
            y[y < -1e8] = 0 # replace very large negative values             
            ystd = np.std(y)
            logger.debug(f"y: {y}")
            logger.debug(f"ystd: {ystd}")
            plt.ylim([0.9*np.min(y), 1.1*np.max(y)])

        # plt.pause(pause_time)

        return plotData

    plotDataGroups = [[[] for probe in value] for value in values]

    probes = [getProbe(value, time, workingDir) for value in values]

    while True:
        for plotDataGroup, probe in zip(plotDataGroups, probes):
            for plotData in plotDataGroup:
                logger.debug(f"parsing probe:\n {probe.dataPath}")
                logger.debug(f"plotData: {plotData}")
                logger.debug(f"probe.data :\n {probe.data}")
                data = probe.data.to_numpy()
                x = data[:,0]
                for ((y , name), loc) in zip(zip(data[:,1:].T, 
                probe.data.columns), probe.locations):
                    logger.debug(f"x: {x}")
                    logger.debug(f"y: {y}")
                    logger.debug(f"location: {loc}")
                    legendName = f"{name}: {loc}"
                    plotData = updatePlot(x, y, plotData, ylabel=probe.field,
                    legendName= legendName)

        plt.pause(pauseTime)