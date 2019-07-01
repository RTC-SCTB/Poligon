import time
from controllers.basecontroller import BaseModbusTcpController
import threading

from controllers.et_7060 import ET_7060

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "FirstMine": "DI0",  # первая мина
    "SecondMine": "DI1",  # вторая мина
    "ThirdMine": "DI2",  # третья мина
    "SirenRelay": "Relay1"  # реле, включающее серену
}

_blinkTime = 1.0  # время, на сколько зажигается сирена, если нажата мина


class _MineHandle:
    """ Класс работы с устройствами в минах """

    def __init__(self, controller: BaseModbusTcpController, config):
        self._controller = controller  # контроллер испытания
        self._config = config
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере данного испытания нет устройства " + item)

    def isFirstMineActive(self):  # активирована ли первая мина
        return self._controller.__getattr__(self._config["FirstMine"])

    def isSecondMineActive(self):  # активирована ли вторая мина
        return self._controller.__getattr__(self._config["SecondMine"])

    def isThirdMineActive(self):  # активирована ли третья мина
        return self._controller.__getattr__(self._config["ThirdMine"])

    @property
    def sirenState(self):
        """ свойство - возращающее состояние сирены - активна или нет """
        return self._controller.__getattr__(self._config["SirenRelay"])

    @sirenState.setter
    def sirenState(self, state):
        self._controller.__setattr__(self._config["SirenRelay"], state)  # меняем состояние сирены


class Mine(threading.Thread):
    """ Класс автономного испытания - мины """

    def __init__(self, host, config=_baseConfig, invfreq=0.2):
        threading.Thread.__init__(self, daemon=True)
        self._host = host
        self._controller = ET_7060(self._host)  # создаем экземпляр контроллера
        self._mineHandle = _MineHandle(self._controller, config)  # создаем экземляр handle
        self._invfreq = invfreq  # частота обновления испытания
        self._exit = False  # метка выхода из потока

        self._time = time.time()  # таймер
        self._firstMineActiveFlag = True  # флаг - показывающий активна ли первая мина
        self._secondMineActiveFlag = True  # флаг - показывающий активна ли  вторая мина
        self._thirdMineActiveFlag = True  # флаг - показывающий активна ли третья мина

    def _update(self):
        """ метод обновления логики """
        if self._mineHandle.isFirstMineActive() and self._firstMineActiveFlag:  # если нажата мина и она была активна
            self._mineHandle.sirenState = True
            self._firstMineActiveFlag = False
            self._time = time.time()

        if self._mineHandle.isSecondMineActive() and self._firstMineActiveFlag:  # если нажата мина и она была активна
            self._mineHandle.sirenState = True
            self._secondMineActiveFlag = False
            self._time = time.time()

        if self._mineHandle.isThirdMineActive() and self._firstMineActiveFlag:  # если нажата мина и она была активна
            self._mineHandle.sirenState = True
            self._thirdMineActiveFlag = False
            self._time = time.time()

        if self._mineHandle.sirenState and ((time.time() - self._time) > _blinkTime):
            self._mineHandle.sirenState = False

    def reset(self):
        """ сброс всей логики """
        self._firstMineActiveFlag = True
        self._secondMineActiveFlag = True
        self._thirdMineActiveFlag = True
        self._mineHandle.sirenState = False  # выключаем сирену

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
