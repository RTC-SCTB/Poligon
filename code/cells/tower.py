import time
from controllers.basecontroller import BaseModbusTcpController
import threading

from controllers.et_7060 import ET_7060

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "FirstRedButton": "DI1",  # первая красная кнопка, при нажании на которую, загорается красный
    "SecondRedButton": "DI3",  # вторая красная кнопка(опциональна)
    "FirstGreenButton": "DI0",  # первая зеленая кнопка, при нажании на которую, загорается зеленый
    "SecondGreenButton": "DI2",  # вторая зеленая кнопка(опциональна)
    "RedLedRelay": "Relay0",  # реле, зажигающее красный цвет
    "GreenLedRelay": "Relay1",  # реле, зажигающее зеленый цвет
    "BlueLedRelay": "Relay2"  # реле, зажигающее голубой цвет
}


class _TowerHandle:
    """ Класс работы с устройствами в башне """

    def __init__(self, controller: BaseModbusTcpController, config):
        self._controller = controller  # контроллер испытания
        self._config = config
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере данного испытания нет устройства " + item)

    def isRedButtonPress(self):
        """ Нажата ли красная кнопка """
        return self._controller.__getattr__(self._config["FirstRedButton"]) or \
               self._controller.__getattr__(self._config["SecondRedButton"])  # считываем значения с DI

    def isGreenButtonPress(self):
        """ Нажата ли зеленая кнопка """
        return self._controller.__getattr__(self._config["FirstGreenButton"]) or \
               self._controller.__getattr__(self._config["SecondGreenButton"])  # считываем значения с DI

    def greenLight(self):
        self._controller.__setattr__(self._config["RedLedRelay"], False)  # выключаем все реле, кроме зеленого
        self._controller.__setattr__(self._config["BlueLedRelay"], False)
        self._controller.__setattr__(self._config["GreenLedRelay"], True)

    def blueLight(self):
        self._controller.__setattr__(self._config["RedLedRelay"], False)  # выключаем все реле, кроме голубого
        self._controller.__setattr__(self._config["BlueLedRelay"], True)
        self._controller.__setattr__(self._config["GreenLedRelay"], False)

    def redLight(self):
        self._controller.__setattr__(self._config["RedLedRelay"], True)  # выключаем все реле, кроме красного
        self._controller.__setattr__(self._config["BlueLedRelay"], False)
        self._controller.__setattr__(self._config["GreenLedRelay"], False)


class Tower(threading.Thread):
    """ Класс автономного испытания - башни """
    def __init__(self, host, config=_baseConfig, invfreq=0.2):
        threading.Thread.__init__(self, daemon=True)
        self._host = host
        self._controller = ET_7060(self._host)  # создаем экземпляр контроллера
        self._towerHandle = _TowerHandle(self._controller, config)  # создаем экземляр handle башни
        self._invfreq = invfreq     # частота обновления испытания
        self._exit = False  # метка выхода из потока

    def _update(self):
        """ метод обновления логики """
        if self._towerHandle.isGreenButtonPress():  # если нажата зеленая кнопка
            self._towerHandle.greenLight()  # зажигаем башню в зеленый
        if self._towerHandle.isRedButtonPress():  # если нажата красная кнопка
            self._towerHandle.redLight()  # зажигаем башню в красный

    def reset(self):
        """ сброс всей логики """
        self._towerHandle.blueLight()  # включаем синий цвет

    def run(self):
        """ тут производится обновление """
        while not self._exit:
            self._update()
            time.sleep(self._invfreq)

    def start(self):
        """ запуск работы испытания """
        self.reset()
        threading.Thread.start(self)

    def exit(self):
        """ функция выхода из потока """
        self._exit = True
        self._controller.close()    # закрываем соединение
