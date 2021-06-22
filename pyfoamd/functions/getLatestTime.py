import os

def getLatestTime(directory=os.getcwd()):

    #- Get the latest time directory
    directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    latestTime = '0'
    for directory in directories:
        name = directory.replace('/', '')
        if name.isdigit() is True:
            if int(name) > int(latestTime):
                latestTime = name

    return latestTime
