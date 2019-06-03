from controllers.basecontroller import BaseModbusTcpController

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "Bank": "DI0",  # индикатор маяка-банки
    "HatchRelay": "Relay0",  # реле, открывающее/закрывающее створки люка
    "SirenRelay": "Relay1",  # реле, включающее серену
}


class Hatch:
    """ Класс испытания - люк """

    def __init__(self, controller: BaseModbusTcpController, config=_baseConfig):
        self._controller = controller  # контроллер испытания
        self._config = config
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере данного испытания нет устройства " + item)

    def isBankInPlace(self):    # на месте ли банка
        return self._controller.__getattr__(self._config["Bank"])

    def changeSirenState(self, state):
        self._controller.__setattr__(self._config["SirenRelay"], state)  # меняем состояние сирены

    def changeHatchState(self, state):
        """ меняем состояние люка """
        self._controller.__setattr__(self._config["HatchRelay"], state)  # меняем состояние люка
