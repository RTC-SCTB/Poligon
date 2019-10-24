from poligon.cells.basecell import BaseCell
from poligon.controllers.basecontroller import BaseModbusTcpController
import time

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "Bank": "DI0",  # индикатор маяка-банки
    "HatchRelay": "Relay0",  # реле, открывающее/закрывающее створки люка
    "SirenRelay": "Relay1",  # реле, включающее серену
}

_timeToDie = 5  # время задержки перед открытим люка в секундах


class _HatchHandle:
    """ Класс работы с устройствами в люке """
    configList = ("Bank", "HatchRelay", "SirenRelay")

    def __init__(self, controller: BaseModbusTcpController, config):
        self._controller = controller  # контроллер испытания
        self._config = config

    def isBankInPlace(self):    # на месте ли банка
        return self._controller.__getattr__(self._config["Bank"])

    @property
    def sirenState(self):
        """ свойство - возращающее состояние сирены - активна или нет """
        return self._controller.__getattr__(self._config["SirenRelay"])

    @sirenState.setter
    def sirenState(self, state):
        self._controller.__setattr__(self._config["SirenRelay"], state)  # меняем состояние сирены

    @property
    def hatchState(self):
        """ свойство - возращающее состояние люка - открыт или закрыт """
        return self._controller.__getattr__(self._config["HatchRelay"])

    @hatchState.setter
    def hatchState(self, state):
        self._controller.__setattr__(self._config["HatchRelay"], state)  # меняем состояние люка


class Hatch(BaseCell):
    """ Класс автономного испытания - люк """

    def __init__(self, host, controler, config=_baseConfig, invfreq=0.2, *args, **kwargs):
        err = [attr for attr in _HatchHandle.configList if attr not in config]  # проверка конфигурации(первая)
        if len(err) != 0:
            raise AttributeError("В конфигурации не были указаны следующие параметры: {err}".format(err=err))

        BaseCell.__init__(self, host, controler, config, invfreq, *args, **kwargs)
        self._hatchHandle = _HatchHandle(self._controller, config)  # создаем экземляр handle подъемника
        self._time = time.time()   # таймер
        self._hatchActivatedFlag = False    # флаг - показывающий было ли активировано открытие люка

    def _update(self):
        """ метод обновления логики """
        if not self._hatchHandle.isBankInPlace():
            self._hatchActivatedFlag = True     # активируем флаг от открытии люка
            self._hatchHandle.sirenState = True     # включаем сирену
            self._time = time.time()    # засекаем время

        if self._hatchActivatedFlag and ((time.time() - self._time) > _timeToDie):
            self._hatchActivatedFlag = False    # сбрасываем флаг
            self._hatchHandle.hatchState = False    # открываем люк
            time.sleep(1)     # спим, чтоб люк успел открыться
            self._hatchHandle.sirenState = False  # выключаем сирену

    def reset(self):
        """ сброс всей логики """
        self._hatchHandle.hatchState = True     # закрываем люк
        self._hatchHandle.sirenState = False    # выключаем сирену


if __name__ == "__main__":
    import time

    # 1 тест

    # обычный пуск
    hatch = Hatch(host="192.168.255.1", controler="et_7060", invfreq=0.1, unit=1)
    hatch.start()

    while True:
        time.sleep(0.5)


    # 2 тест
    """
    # уже созданный контроллер
    from poligon.controllers.et_7060 import ET_7060
    controller = ET_7060("192.168.255.1")
    hatch = Hatch(host="192.168.255.1", controler=controller, invfreq=0.1, unit=1)
    hatch.start()

    while True:
        time.sleep(0.5)
    """

    # 3 тест
    """
    # несуществующий контроллер
    hatch = Hatch(host="192.168.255.1", controler="et_70", invfreq=0.1, unit=1)
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
    hatch = Hatch(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1)
    """

    # 5 test
    """
    # ошибка конфигурации, несуществующие выходы контроллера
    conf = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
        "Bank": "DI10",  # индикатор маяка-банки
        "HatchRelay": "Relay0",  # реле, открывающее/закрывающее створки люка
        "SirenRelay": "Relay1",  # реле, включающее серену
    }
    hatch = Hatch(host="192.168.255.1", controler="et_7060", config=conf, invfreq=0.1, unit=1) 
    """




