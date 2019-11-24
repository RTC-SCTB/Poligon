import time

from poligon.controllers.basecontroller import BaseModbusTcpController
from poligon.cells.basecell import BaseCell

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "FirstMine": "DI0",  # первая мина
    "SecondMine": "DI1",  # вторая мина
    "ThirdMine": "DI2",  # третья мина
    "SirenRelay": "Relay1"  # реле, включающее серену
}

_blinkTime = 0.9  # время, на сколько зажигается сирена, если нажата мина


class _MineHandle:
    """ Класс работы с устройствами в минах """
    configList = ("FirstMine", "SecondMine", "ThirdMine", "SirenRelay")

    def __init__(self, controller: BaseModbusTcpController, config):
        self._controller = controller  # контроллер испытания
        self._config = config

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


class Mine(BaseCell):
    """ Класс автономного испытания - мины """
    def __init__(self, host, controller, config=_baseConfig, invfreq=0.2, *args, **kwargs):
        BaseCell.__init__(self, host, controller, config, invfreq, *args, **kwargs)

        if self._logger is not None:
            self._logger.info("[{n}]: Проверка ключей-параметров испытания, указанных в конфигурации".format(n=self.name))
        err = [attr for attr in _MineHandle.configList if attr not in config]  # проверка конфигурации(первая)
        if len(err) != 0:
            if self._logger is not None:
                self._logger.error("[{n}]: В конфигурации не были указаны следующие параметры: {err}".format(n=self.name,
                                                                                                             err=err))
            raise AttributeError("В конфигурации не были указаны следующие параметры: {err}".format(err=err))
        if self._logger is not None:
            self._logger.info("[{n}]: Проверка прошла успешно, все ключи указаны".format(n=self.name))

        self._mineHandle = _MineHandle(self._controller, config)  # создаем экземляр handle
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

        if self._mineHandle.isSecondMineActive() and self._secondMineActiveFlag:  # если нажата мина и она была активна
            self._mineHandle.sirenState = True
            self._secondMineActiveFlag = False
            self._time = time.time()

        if self._mineHandle.isThirdMineActive() and self._thirdMineActiveFlag:  # если нажата мина и она была активна
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


if __name__ == "__main__":
    import time

    # 1 тест

    # обычный пуск
    mine = Mine(host="192.168.255.1", controler="et_7060", invfreq=0.1, unit=1)
    mine.start()

    while True:
        time.sleep(0.5)


    # 2 тест
    """
    # уже созданный контроллер
    from poligon.controllers.et_7060 import ET_7060
    controller = ET_7060("192.168.255.1")
    mine = Mine(host="192.168.255.1", controler=controller, invfreq=0.1, unit=1)
    mine.start()

    while True:
        time.sleep(0.5)
    """

    # 3 тест
    """
    # несуществующий контроллер
    mine = Mine(host="192.168.255.1", controler="et_70", invfreq=0.1, unit=1)
    """

    # 4 тест
    """
    # ошибка конфигурации, часть словаря
    conf = {
        "FirstRedButton": "DI1",  # первая красная кнопка, при нажании на которую, загорается красный
        "SecondRedButton": "DI3",  # вторая красная кнопка(опциональна)
        "FirstGreenButton": "DI0",  # первая зеленая кнопка, при нажании на которую, загорается зеленый
        "SecondGreenButton": "DI2",  # вторая зеленая кнопка(опциональна)
    }
    mine = Mine(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1)
    """

    # 5 test

    # ошибка конфигурации, несуществующие выходы контроллера
    conf = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
        "FirstMine": "DI10",  # первая мина
        "SecondMine": "DI1",  # вторая мина
        "ThirdMine": "DI2",  # третья мина
        "SirenRelay": "Relay1"  # реле, включающее серену
    }
    mine = Mine(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1) 

