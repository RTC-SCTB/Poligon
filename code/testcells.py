from cells.tower import Tower
from controllers.et_7060 import ET_7060
import time

et_7060 = ET_7060("192.168.255.1")  # создаем экземпляр контроллера

optionalConfig = {
    "FirstRedButton": "DI1",  # первая красная кнопка, при нажании на которую, загорается красный
    "SecondRedButton": "DI3",  # вторая красная кнопка(опциональна)
    "FirstGreenButton": "DI0",  # первая зеленая кнопка, при нажании на которую, загорается зеленый
    "SecondGreenButton": "DI2",  # вторая зеленая кнопка(опциональна)
    "RedLedRelay": "Relay1",  # реле, зажигающее красный цвет
    "GreenLedRelay": "Relay2",  # реле, зажигающее зеленый цвет
    "BlueLedRelay": "Relay0"  # реле, зажигающее голубой цвет
}

tower = Tower(et_7060, config=optionalConfig)  # создаем экземпляр башни
tower.blueLight()   # зажигаем ее в голубой цвет

while True:
    if tower.isGreenButtonPress():  # если нажата зеленая кнопка
        tower.greenLight()  # зажигаем башню в зеленый
    if tower.isRedButtonPress():    # если нажата красная кнопка
        tower.redLight()    # зажигаем башню в красный
    time.sleep(0.3)
