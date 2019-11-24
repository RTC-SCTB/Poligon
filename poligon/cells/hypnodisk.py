from poligon.controllers.basecontroller import BaseModbusTcpController
from poligon.cells.basecell import BaseCell

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "StopButton": "DI0",  # кнопка, при нажании на которую гипнодиск перестает вращаться
    "MotorStateRelay": "Relay0",  # реле, включающее/выключающее драйвер мотора
}


class _HypnodiskHandle:
    """ Класс работы с устройствами в гипнодиске """
    configList = ("StopButton", "MotorStateRelay")

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


class Hypnodisk(BaseCell):
    """ Класс автономного испытания - гипнодиск """
    def __init__(self, host, controller, config=_baseConfig, invfreq=0.2, *args, **kwargs):
        BaseCell.__init__(self, host, controller, config, invfreq, *args, **kwargs)

        if self._logger is not None:
            self._logger.info("[{n}]: Проверка ключей-параметров испытания, указанных в конфигурации".format(n=self.name))
        err = [attr for attr in _HypnodiskHandle.configList if attr not in config]  # проверка конфигурации(первая)
        if len(err) != 0:
            if self._logger is not None:
                self._logger.error("[{n}]: В конфигурации не были указаны следующие параметры: {err}".format(n=self.name,
                                                                                                             err=err))
            raise AttributeError("В конфигурации не были указаны следующие параметры: {err}".format(err=err))
        if self._logger is not None:
            self._logger.info("[{n}]: Проверка прошла успешно, все ключи указаны".format(n=self.name))

        self._hypnoHandle = _HypnodiskHandle(self._controller, config)  # создаем экземляр handle подъемника
        self._hypnoState = True

    def _update(self):
        """ метод обновления логики """
        if self._hypnoHandle.isStopButtonPress():
            self._hypnoState = False

        self._hypnoHandle.motorState = self._hypnoState

    def reset(self):
        """ сброс всей логики """
        pass


if __name__ == "__main__":
    import time

    # 1 тест

    # обычный пуск
    hypno = Hypnodisk(host="192.168.255.1", controler="et_7060", invfreq=0.1, unit=1)
    hypno.start()

    while True:
        time.sleep(0.5)


    # 2 тест
    """
    # уже созданный контроллер
    from poligon.controllers.et_7060 import ET_7060
    controller = ET_7060("192.168.255.1")
    hypno = Hypnodisk(host="192.168.255.1", controler=controller, invfreq=0.1, unit=1)
    hypno.start()

    while True:
        time.sleep(0.5)
    """

    # 3 тест
    """
    # несуществующий контроллер
    hypno = Hypnodisk(host="192.168.255.1", controler="et_70", invfreq=0.1, unit=1)
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
    hypno = Hypnodisk(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1)
    """

    # 5 test
    """
    # ошибка конфигурации, несуществующие выходы контроллера
    conf = {
        "StopButton": "DI10",
        "MotorStateRelay": "Relay0"}
    hypno = Hypnodisk(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1) 
    """
