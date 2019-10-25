from poligon.cells.tower import Tower
import time
import logging
from poligon.util import checkConfig, findAvaibleCells
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

checkConfig(PATH, withCreate=True, logger=rootLogger)
data = findAvaibleCells(PATH, logger=rootLogger)

tower = Tower(host=data["Tower"][0]["ip"], controller=data["Tower"][0]["controller"],
              config=data["Tower"][0]["connection"],
              invfreq=data["Tower"][0]["invfreq"], logger=rootLogger, name="Tower")  # создаем экземпляр башни
tower.start()

while True:
    time.sleep(0.1)
