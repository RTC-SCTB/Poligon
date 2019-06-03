from controllers.basecontroller import BaseModbusTcpController

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "FirstRedButton": "DI1",  # первая красная кнопка, при нажании на которую, загорается красный
    "SecondRedButton": "DI3",  # вторая красная кнопка(опциональна)
    "FirstGreenButton": "DI0",  # первая зеленая кнопка, при нажании на которую, загорается зеленый
    "SecondGreenButton": "DI2",  # вторая зеленая кнопка(опциональна)
    "RedLedRelay": "Relay0",  # реле, зажигающее красный цвет
    "GreenLedRelay": "Relay1",  # реле, зажигающее зеленый цвет
    "BlueLedRelay": "Relay2"  # реле, зажигающее голубой цвет
}


class Tower:
    """ Класс работы с устройствами в башне """

    def __init__(self, controller: BaseModbusTcpController, config=_baseConfig):
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
        self._controller.__setattr__(self._config["RedLedRelay"], False)   # выключаем все реле, кроме зеленого
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

