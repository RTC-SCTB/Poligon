from poligon.cells.tower import Tower
import json
import time
import logging

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger('test')
fileHandler = logging.FileHandler("{0}.log".format('example'))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.INFO)

with open("poligon/testconfig.json", "r") as file:
    data = json.load(file)

tower = Tower(host=data["Tower"][0]["ip"], controller=data["Tower"][0]["controller"],
              config=data["Tower"][0]["connection"],
              invfreq=data["Tower"][0]["invfreq"], logger=rootLogger, name="Tower")  # создаем экземпляр башни
tower.start()

while True:
    #print(tower._towerHandle.isRedButtonPress())
    time.sleep(0.1)
