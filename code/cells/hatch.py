import threading
from controllers.basecontroller import BaseModbusTcpController
import time
from controllers.et_7060 import ET_7060

_baseConfig = {  # базовый конфигурационный словарь, перечисляет все входы и выходы, задействованные испытанием
    "Bank": "DI0",  # индикатор маяка-банки
    "HatchRelay": "Relay0",  # реле, открывающее/закрывающее створки люка
    "SirenRelay": "Relay1",  # реле, включающее серену
}

_timeToDie = 5  # время задержки перед открытим люка в секундах


class _HatchHandle:
    """ Класс работы с устройствами в люке """

    def __init__(self, controller: BaseModbusTcpController, config):
        self._controller = controller  # контроллер испытания
        self._config = config
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере данного испытания нет устройства " + item)

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


class Hatch(threading.Thread):
    """ Класс автономного испытания - люк """

    def __init__(self, host, config=_baseConfig, invfreq=0.2):
        threading.Thread.__init__(self, daemon=True)
        self._host = host
        self._controller = ET_7060(self._host)  # создаем экземпляр контроллера
        self._hatchHandle = _HatchHandle(self._controller, config)  # создаем экземляр handle подъемника
        self._invfreq = invfreq  # частота обновления испытания
        self._exit = False  # метка выхода из потока

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
        self._controller.close()    # закрываем соединение







