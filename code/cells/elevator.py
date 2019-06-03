from controllers.basecontroller import BaseModbusTcpController

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "UpSwitch": "DI1",  # верхний кончевик, при нажатии на который лифт останавливается
    "DownSwitch": "DI0",  # нижний концевик, при нажатии на который лифт останавливается
    "UpButton": "DI2",  # кнопка, при нажании на которую лифт едет вверх
    "DownButton": "DI3",  # кнопка, при нажании на которую лифт едет вниз
    "SirenRelay": "Relay0",  # реле, включающее серену
    "MotorStartStopRelay": "Relay1",  # реле, включающее/выключающее драйвер мотора
    "MotorDirRelay": "Relay2"  # реле, переключающее направление вращение мотора на драйвере
}


class Elevator:
    """ Класс испытания подъемника """

    def __init__(self, controller: BaseModbusTcpController, config=_baseConfig):
        self._controller = controller  # контроллер испытания
        self._config = config
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере данного испытания нет устройства " + item)

    def isUpSwitchPress(self):
        return self._controller.__getattr__(self._config["UpSwitch"])

    def isDownSwitchPress(self):
        return self._controller.__getattr__(self._config["DownSwitch"])

    def isUpButtonPress(self):
        return self._controller.__getattr__(self._config["UpButton"])

    def isDownButtonPress(self):
        return self._controller.__getattr__(self._config["DownButton"])

    def changeSirenState(self, state):
        self._controller.__setattr__(self._config["SirenRelay"], state)  # меняем состояние сирены

    def changeMotorDirection(self, direction):
        """ меняем направление вращения мотора """
        pass    # TODO: доделать

    def changeMotorState(self, state):
        """ меняем состояние мотора остановить или запустить """
        pass     # TODO: доделать
