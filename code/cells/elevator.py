import threading
import time
from controllers.basecontroller import BaseModbusTcpController
from controllers.et_7060 import ET_7060

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "UpSwitch": "DI1",  # верхний кончевик, при нажатии на который лифт останавливается
    "DownSwitch": "DI0",  # нижний концевик, при нажатии на который лифт останавливается
    "UpButton": "DI2",  # кнопка, при нажании на которую лифт едет вверх
    "DownButton": "DI3",  # кнопка, при нажании на которую лифт едет вниз
    "StopButton": "DI4",    # кнопка экстренной остановки лифта
    "SirenRelay": "Relay0",  # реле, включающее серену
    "MotorStateRelay": "Relay1",  # реле, включающее/выключающее драйвер мотора
    "MotorDirRelay": "Relay2"  # реле, переключающее направление вращение мотора на драйвере
}


class _ElevatorHandle:
    """ Класс работы с устройствами в подъемнике """

    def __init__(self, controller: BaseModbusTcpController, config):
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

    def isStopButtonPress(self):
        return self._controller.__getattr__(self._config["StopButton"])

    @property
    def sirenState(self):
        """ свойство - возращающее состояние сирены - активна или нет """
        return self._controller.__getattr__(self._config["SirenRelay"])

    @sirenState.setter
    def sirenState(self, state):
        self._controller.__setattr__(self._config["SirenRelay"], state)  # меняем состояние сирены

    @property
    def motorState(self):
        """ свойство - возращающее состояние мотора - включен он или выключен """
        return self._controller.__getattr__(self._config["MotorStateRelay"])

    @motorState.setter
    def motorState(self, state):
        self._controller.__setattr__(self._config["MotorStateRelay"], state)  # меняем состояние мотора

    @property
    def motorDirection(self):
        """ свойство - возращающее направление вращения мотора """
        return self._controller.__getattr__(self._config["MotorDirRelay"])

    @motorDirection.setter
    def motorDirection(self, direction):
        self._controller.__setattr__(self._config["MotorDirRelay"], direction)  # меняем состояние сирены


class _ElevatorStates:
    """ Класс возможных состояний лифта """
    STOP = 0  # лифт остановлен (экстренно)
    UP = 1  # лифт находится наврерху
    DOWN = 2  # лифт находится внизу
    MIDDLE = 3  # лифт едет где-то посередине


class Elevator(threading.Thread):
    """ Класс автономного испытания - подъемник """

    def __init__(self, host, config=_baseConfig, invfreq=0.2):
        threading.Thread.__init__(self, daemon=True)
        self._host = host
        self._controller = ET_7060(self._host)  # создаем экземпляр контроллера
        self._elevatorHandle = _ElevatorHandle(self._controller, config)  # создаем экземляр handle подъемника
        self._invfreq = invfreq  # частота обновления испытания
        self._exit = False  # метка выхода из потока

        self._elevatorState = _ElevatorStates.STOP  # начальное состояние лифта

    def _update(self):
        """ метод обновления логики """
        upButState = self._elevatorHandle.isUpButtonPress()  # разово получаем все данные, чтоб лишний раз канал связи не засорять
        downButState = self._elevatorHandle.isDownButtonPress()
        upSwitchState = self._elevatorHandle.isUpSwitchPress()
        downSwitchState = self._elevatorHandle.isDownSwitchPress()

        if self._elevatorHandle.isStopButtonPress():    # была экстренная остановка
            self._elevatorHandle.motorState = False  # вылючаем мотор
            self._elevatorState = _ElevatorStates.STOP

        if self._elevatorState == _ElevatorStates.STOP:     # конечный автомат
            if downButState:    # если нажата ктопка - ехать вниз
                self._elevatorHandle.motorDirection = False     # направление - вниз
                self._elevatorHandle.motorState = True  # включаем мотор
                self._elevatorState = _ElevatorStates.MIDDLE
            if upButState:    # если нажата ктопка - ехать вниз
                self._elevatorHandle.motorDirection = True     # направление - вверх
                self._elevatorHandle.motorState = True  # включаем мотор
                self._elevatorState = _ElevatorStates.MIDDLE

        elif self._elevatorState == _ElevatorStates.UP:
            if downButState:    # если нажата ктопка - ехать вниз
                self._elevatorHandle.motorDirection = False     # направление - вниз
                self._elevatorHandle.motorState = True  # включаем мотор
            if not upSwitchState:   # если верхний концевик был отжат
                self._elevatorState = _ElevatorStates.MIDDLE    # лифт где-то посередине

        elif self._elevatorState == _ElevatorStates.MIDDLE:
            if not self._elevatorHandle.sirenState:     # если сирена не орет
                self._elevatorHandle.sirenState = True  # теперь орет)

            if downSwitchState:
                self._elevatorHandle.motorState = False     # вылючаем мотор
                self._elevatorState = _ElevatorStates.DOWN  # переключаем состояние
                self._elevatorHandle.sirenState = False
            if upSwitchState:
                self._elevatorHandle.motorState = False     # включаем мотор
                self._elevatorState = _ElevatorStates.UP    # переключаем состояние
                self._elevatorHandle.sirenState = False

        elif self._elevatorState == _ElevatorStates.DOWN:
            if upButState:    # если нажата ктопка - ехать вниз
                self._elevatorHandle.motorDirection = True     # направление - вверх
                self._elevatorHandle.motorState = True  # включаем мотор
            if not downSwitchState:   # если нижний концевик был отжат
                self._elevatorState = _ElevatorStates.MIDDLE    # лифт где-то посередине

    def reset(self):
        """ сброс всей логики """
        self._elevatorHandle.motorState = False     # выключаем мотор
        self._elevatorState = _ElevatorStates.STOP  # переключаем состояние конечного автомата

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
