from poligon.controllers.basecontroller import BaseModbusTcpController
from poligon.cells.basecell import BaseCell

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
    configList = ("FirstRedButton", "SecondRedButton", # конфигурационный список всех значений, которые нужно установить
                  "FirstGreenButton", "SecondGreenButton",
                  "RedLedRelay", "GreenLedRelay", "BlueLedRelay")

    def __init__(self, controller: BaseModbusTcpController, config):
        self._controller = controller  # контроллер испытания
        self._config = config

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


class Tower(BaseCell):
    """ Класс автономного испытания - башни """
    def __init__(self, host, controler, config=_baseConfig, invfreq=0.2, *args, **kwargs):
        err = [attr for attr in _TowerHandle.configList if attr not in config]  # проверка конфигурации(первая)
        if len(err) != 0:
            raise AttributeError("В конфигурации не были указаны следующие параметры: {err}".format(err=err))

        BaseCell.__init__(self, host, controler, config, invfreq, *args, **kwargs)
        self._towerHandle = _TowerHandle(self._controller, self._config)  # создаем экземляр handle башни

    def _update(self):
        """ метод обновления логики """
        if self._towerHandle.isGreenButtonPress():  # если нажата зеленая кнопка
            self._towerHandle.greenLight()  # зажигаем башню в зеленый
        if self._towerHandle.isRedButtonPress():  # если нажата красная кнопка
            self._towerHandle.redLight()  # зажигаем башню в красный

    def reset(self):
        """ сброс всей логики """
        self._towerHandle.blueLight()  # включаем синий цвет


if __name__ == "__main__":
    import time

    # 1 тест
    """
    # обычный пуск
    tower = Tower(host="192.168.255.1", controler="et_7060", invfreq=0.1, unit=1)
    tower.start()

    while True:
        print(tower._towerHandle.isRedButtonPress())
        time.sleep(0.5)
    """

    # 2 тест
    """
    # уже созданный контроллер
    from poligon.controllers.et_7060 import ET_7060
    controller = ET_7060("192.168.255.1")
    tower = Tower(host="192.168.255.1", controler=controller, invfreq=0.1, unit=1)
    tower.start()

    while True:
        print(tower._towerHandle.isRedButtonPress())
        time.sleep(0.5)
    """

    # 3 тест
    """
    # несуществующий контроллер
    tower = Tower(host="192.168.255.1", controler="et_70", invfreq=0.1, unit=1)
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
    tower = Tower(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1)
    """

    # 5 test
    """
    # ошибка конфигурации, несуществующие выходы контроллера
    conf = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
        "FirstRedButton": "DI7",  # первая красная кнопка, при нажании на которую, загорается красный
        "SecondRedButton": "DI8",  # вторая красная кнопка(опциональна)
        "FirstGreenButton": "DI9",  # первая зеленая кнопка, при нажании на которую, загорается зеленый
        "SecondGreenButton": "DI6",  # вторая зеленая кнопка(опциональна)
        "RedLedRelay": "Relay0",  # реле, зажигающее красный цвет
        "GreenLedRelay": "Relay1",  # реле, зажигающее зеленый цвет
        "BlueLedRelay": "Relay2"  # реле, зажигающее голубой цвет
    }
    tower = Tower(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1) 
    """

