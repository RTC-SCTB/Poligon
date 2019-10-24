import threading
import time
from poligon.controllers.basecontroller import BaseModbusTcpController
from poligon.controllers import availableControllers


class BaseCell(threading.Thread):
    """ Класс - интерфейс испытания """
    def __init__(self, host, controler, config, invfreq, *args, **kwargs):
        threading.Thread.__init__(self, daemon=True)
        self._host = host
        self._controller = None
        self._config = config
        self._invfreq = invfreq
        self.__exit = False     # метка выхода из потока

        # проверка контроллера
        if isinstance(controler, BaseModbusTcpController):  # если экземпляр контроллера уже создан
            self._controller = controler
        elif controler in availableControllers: # если предложенный контроллер(строка) есть в словаре доступных
            # контроллеров
            self._controller = availableControllers[controler](self._host, *args, **kwargs)  # создаем экземпляр контроллера
        else:
            raise ValueError("Невозможно найти оболочку для данного контроллера: {c}".format(c=controler))

        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                raise AttributeError("В контроллере {c}, данного испытания, нет устройства {i}".format(c=controler, i=item))

    def _update(self):
        """ метод обновления логики испытания, перегружаемый """
        pass

    def reset(self):
        """ сброс всей логики, перегружаемый """
        pass

    def run(self):
        """ тут производится обновление """
        while not self.__exit:
            self._update()
            time.sleep(self._invfreq)

    def start(self):
        """ запуск работы испытания """
        self.reset()
        threading.Thread.start(self)

    def exit(self):
        """ функция выхода из потока """
        self.__exit = True
        self._controller.close()    # закрываем соединение