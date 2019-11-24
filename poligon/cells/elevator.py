import threading
import time
from poligon.controllers.basecontroller import BaseModbusTcpController
from poligon.cells.basecell import BaseCell

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
    configList = ("UpSwitch", "DownSwitch",  # конфигурационный список всех значений, которые нужно установить
                  "UpButton", "DownButton", "StopButton",
                  "SirenRelay", "MotorStateRelay", "MotorDirRelay")

    def __init__(self, controller: BaseModbusTcpController, config):
        self._controller = controller  # контроллер испытания
        self._config = config

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


class Elevator(BaseCell):
    """ Класс автономного испытания - подъемник """
    def __init__(self, host, controller, config=_baseConfig, invfreq=0.2, *args, **kwargs):
        BaseCell.__init__(self, host, controller, config, invfreq, *args, **kwargs)

        if self._logger is not None:
            self._logger.info("[{n}]: Проверка ключей-параметров испытания, указанных в конфигурации".format(n=self.name))
        err = [attr for attr in _ElevatorHandle.configList if attr not in config]  # проверка конфигурации(первая)
        if len(err) != 0:
            if self._logger is not None:
                self._logger.error("[{n}]: В конфигурации не были указаны следующие параметры: {err}".format(n=self.name,
                                                                                                             err=err))
            raise AttributeError("В конфигурации не были указаны следующие параметры: {err}".format(err=err))
        if self._logger is not None:
            self._logger.info("[{n}]: Проверка прошла успешно, все ключи указаны".format(n=self.name))

        self._elevatorHandle = _ElevatorHandle(self._controller, config)  # создаем экземляр handle подъемника
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


if __name__ == "__main__":
    import time

    # 1 тест

    # обычный пуск
    elevator = Elevator(host="192.168.255.1", controler="et_7060", invfreq=0.1, unit=1)
    elevator.start()

    while True:
        time.sleep(0.5)


    # 2 тест
    """
    # уже созданный контроллер
    from poligon.controllers.et_7060 import ET_7060
    controller = ET_7060("192.168.255.1")
    elevator = Elevator(host="192.168.255.1", controler=controller, invfreq=0.1, unit=1)
    elevator.start()

    while True:
        time.sleep(0.5)
    """

    # 3 тест
    """
    # несуществующий контроллер
    elevator = Elevator(host="192.168.255.1", controler="et_70", invfreq=0.1, unit=1)
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
    elevator = Elevator(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1)
    """

    # 5 test
    """
    # ошибка конфигурации, несуществующие выходы контроллера
    conf = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
        "UpSwitch": "DI1",  # верхний кончевик, при нажатии на который лифт останавливается
        "DownSwitch": "DI10",  # нижний концевик, при нажатии на который лифт останавливается
        "UpButton": "DI20",  # кнопка, при нажании на которую лифт едет вверх
        "DownButton": "DI3",  # кнопка, при нажании на которую лифт едет вниз
        "StopButton": "DI4",    # кнопка экстренной остановки лифта
        "SirenRelay": "Relay0",  # реле, включающее серену
        "MotorStateRelay": "Relay1",  # реле, включающее/выключающее драйвер мотора
        "MotorDirRelay": "Relay2"  # реле, переключающее направление вращение мотора на драйвере
    }
    elevator = Elevator(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1)
    """

