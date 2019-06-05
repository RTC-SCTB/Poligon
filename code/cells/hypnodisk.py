import threading
import time
from controllers.basecontroller import BaseModbusTcpController
from controllers.et_7060 import ET_7060

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "StopButton": "DI0",  # кнопка, при нажании на которую гипнодиск перестает вращаться
    "MotorStateRelay": "Relay0",  # реле, включающее/выключающее драйвер мотора
}


class _HypnodiskHandle:
    """ Класс работы с устройствами в гипнодиске """

    def __init__(self, controller: BaseModbusTcpController, config=_baseConfig):
        self._controller = controller  # контроллер испытания
        self._config = config
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере данного испытания нет устройства " + item)

    def isStopButtonPress(self):
        return self._controller.__getattr__(self._config["StopButton"])

    @property
    def motorState(self):
        """ свойство - возращающее состояние мотора - включен он или выключен """
        return self._controller.__getattr__(self._config["MotorStateRelay"])

    @motorState.setter
    def motorState(self, state):
        self._controller.__setattr__(self._config["MotorStateRelay"], state)  # меняем состояние мотора


class Hypnodisk(threading.Thread):
    """ Класс автономного испытания - гипнодиск """

    def __init__(self, host, config=_baseConfig, invfreq=1.0):
        threading.Thread.__init__(self, daemon=True)
        self._host = host
        self._controller = ET_7060(self._host)  # создаем экземпляр контроллера
        self._hypnoHandle = _HypnodiskHandle(self._controller, config)  # создаем экземляр handle подъемника
        self._invfreq = invfreq  # частота обновления испытания
        self._exit = False  # метка выхода из потока

    def _update(self):
        """ метод обновления логики """
        if self._hypnoHandle.isStopButtonPress():
            self._hypnoHandle.motorState = False
        else:
            self._hypnoHandle.motorState = True

    def reset(self):
        """ сброс всей логики """
        pass

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
        self._controller.close()  # закрываем соединение
