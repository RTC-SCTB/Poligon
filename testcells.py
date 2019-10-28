from poligon.cells.tower import Tower
import time
import logging
from poligon.util import checkConfig, findAvaibleCells, parseConfig

PATH = "poligon/testconfig.json"

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger('test')
fileHandler = logging.FileHandler("{0}.log".format('example'))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.INFO)

cells = None


def realize():
    global cells
    if cells is not None:
        raise BrokenPipeError("Объекты испытаний cells уже созданы")
    global rootLogger

    checkConfig(PATH, withCreate=True, logger=rootLogger)
    data = findAvaibleCells(PATH, logger=rootLogger)
    cells = parseConfig(data, logger=rootLogger)
    for cell in cells:
        cell.start()


def unrealize():
    global cells
    if cells is None:
        return

    for cell in cells:
        cell.exit()
        time.sleep(0.5)
        del cell
    del cells
    cells = None


def reset():
    unrealize()
    realize()


while True:
    reset()
    time.sleep(10)
    print("test reset")
