from controllers.basecontroller import BaseModbusTcpController

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "StopButton": "DI0",  # кнопка, при нажании на которую гипнодиск перестает вращаться
    "MotorStartStopRelay": "Relay0",  # реле, включающее/выключающее драйвер мотора
}


class HypnoDisk:
    """ Класс испытания гипнодиска """

    def __init__(self, controller: BaseModbusTcpController, config=_baseConfig):
        self._controller = controller  # контроллер испытания
        self._config = config
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере данного испытания нет устройства " + item)

    def isStopButtonPress(self):
        return self._controller.__getattr__(self._config["StopButton"])

    def changeMotorState(self, state):
        """ меняем состояние мотора остановить или запустить """
        pass     # TODO: доделать