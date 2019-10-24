from cells.tower import Tower
import json
import time

with open("config.json", "r") as file:
    data = json.load(file)

tower = Tower(host=data["Tower"]["ip"],
              config=data["Tower"]["connection"],
              invfreq=data["Tower"]["invfreq"])  # создаем экземпляр башни
tower.start()

while True:
    print(tower._towerHandle.isRedButtonPress())
    time.sleep(0.1)
