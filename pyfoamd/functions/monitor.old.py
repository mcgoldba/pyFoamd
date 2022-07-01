import subprocess
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import logging
import re
from pyfoamd import userMsg
import pyfoamd.types as pt
from pyfoamd.functions.getProbe import getProbe
from pyfoamd.functions.getMonitor import getMonitor

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
    workingDir=Path.cwd(), title=None, filters=None):

    # logging.getLogger('pf').setLevel(logging.DEBUG)

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
            plt.show()

        logger.debug(f"x: {x}")        
        logger.debug(f"y: {y}")

        plotData.set_data(x, y)
        plt.xlim(np.min(x), np.max(x))

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

    monitors = []
    
    for value in values:
        try:
            monitor = getMonitor(name=value, startTime=time, 
                        workingDir=workingDir)
        except FileNotFoundError:
            monitor = getProbe(value, time, workingDir)
        monitors.append(monitor)


    if filters is not None:
        # Determine which columns to plot of each ofMonitor / ofProbe
        filteredColumnIdx = []
        if len(filters) > len(monitors):
            userMsg("Found more arguments for `filters` than `values`.  "
            "Ignoring extra `filters` arguments.")
            filters = filters[:len(monitors)]
        elif len(filters) < len(monitors):
            #- pad `filters` with extra `None`s
            filters = (filters + len(monitors) * [None])[:len(monitors)] 

        
        for i, filter in enumerate(filters):
            if filter is not None:
                filteredColumnIdx.append([i for i, item in 
                enumerate(monitors[i].data.columns) if re.search(filter, item)])
    else:
        for monitor in monitors:
            filteredColumnIdx.append(range(1, len(monitor.data.columns)))

    while True:
        plots = [None for _ in monitors]
        for p, (plotDataGroup, probe) in enumerate(
            zip(plotDataGroups, monitors)):
            for plotData in plotDataGroup:
                logger.debug(f"parsing probe:\n {probe.dataPath}")
                logger.debug(f"plotData: {plotData}")
                logger.debug(f"probe.data :\n {probe.data}")
                data = probe.data.to_numpy()
                x = probe.data.index.to_numpy()
                try:
                    x = [int(v) for v in x]
                except:
                    x = [float(v) for v in x]

                for i, (y , name) in enumerate(zip(data.T[filteredColumnIdx], 
                probe.data.columns)):
                    if filter is not None and re.search(filter, name):
                        y = np.array([float(v) for v in y])
                        if isinstance(monitor, pt.ofProbe):
                            legendName = f"{name}: {probe.locations[i]}"
                            ylabel = probe.field
                        else:
                            legendName = name
                            ylabel = 'Value'
                        plots[p] = updatePlot(x, y, plots[p], 
                        ylabel=ylabel,
                        legendName=legendName)

        plt.pause(pauseTime)