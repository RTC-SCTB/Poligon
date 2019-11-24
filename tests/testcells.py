import time
from poligon.util import checkConfig, findAvaibleCells, parseConfig
import logging.config
import datetime

PATH = "config.json"

logging.config.fileConfig('logging.conf')
rootLogger = logging.getLogger('poligonLogger')

rootLogger.info("Starting session on: ")
rootLogger.info(str(datetime.datetime.now()))

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
