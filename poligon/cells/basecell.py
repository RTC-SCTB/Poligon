import threading
import time
from poligon.controllers.basecontroller import BaseModbusTcpController
from poligon.controllers import availableControllers
from pymodbus.exceptions import ModbusIOException, ConnectionException
import logging


class BaseCell(threading.Thread):
    """ Класс - интерфейс испытания """

    def __init__(self, host, controller, config, invfreq, logger=None, name=None, *args, **kwargs):
        threading.Thread.__init__(self, daemon=True)
        if logger is not None:
            if not isinstance(logger, logging.Logger):
                raise ValueError("Параметр logger должен иметь тип: " + str(logging.Logger))

        if name is not None:
            self.name = name

        self._logger = logger  # место, куда будут идти логи
        self._host = host
        self._controller = None
        self._config = config
        self._invfreq = invfreq
        self.__exit = False  # метка выхода из потока

        if self._logger is not None:
            self._logger.info("[{n}]: Проверка наличия указанного контроллера: [{c}]".format(n=self.name, c=controller))
        # проверка контроллера
        if isinstance(controller, BaseModbusTcpController):  # если экземпляр контроллера уже создан
            self._controller = controller
            if self._logger is not None:
                self._logger.info(
                    "[{n}]: Указанный контроллер [{c}] найден".format(n=self.name, c=controller.__repr__()))
        elif controller in availableControllers:  # если предложенный контроллер(строка) есть в словаре доступных
            # контроллеров
            self._controller = availableControllers[controller](self._host, *args, **kwargs)  # создаем экземпляр
            # контроллера
            if self._logger is not None:
                self._logger.info("[{n}]: Указанный контроллер [{c}] найден".format(n=self.name, c=controller))
        else:
            if self._logger is not None:
                self._logger.error("[{n}]: Указанный контроллер [{c}] не найден".format(n=self.name, c=controller))
            raise ValueError("Невозможно найти оболочку для данного контроллера: {c}".format(c=controller))

        if self._logger is not None:
            self._logger.info(
                "[{n}]: Проверка наличия выходов контролера, указанных в конфигурации".format(n=self.name))
        for item in self._config.values():  # проверка на допустимость конфигурации
            if item not in self._controller.actorDict:
                if self._logger is not None:
                    self._logger.error("[{n}]: [{o}] не доступен".format(n=self.name, o=item))
                raise AttributeError("В контроллере {c}, данного испытания, нет устройства {i}".format(c=controller,
                                                                                                       i=item))
            if self._logger is not None:
                self._logger.info("[{n}]: [{o}] доступен".format(n=self.name, o=item))

    def _update(self):
        """ метод обновления логики испытания, перегружаемый """
        pass

    def reset(self):
        """ сброс всей логики, перегружаемый """
        pass

    def run(self):
        """ тут производится обновление """
        if self._logger is not None:
            self._logger.info("[{n}]: Попытка запуска испытания".format(n=self.name))
        try:
            self.reset()
        except ConnectionException:
            if self._logger is not None:
                self._logger.error("[{n}]: Невозможно подключиться к хосту [{h}]".format(n=self.name, h=self._host))
            raise ConnectionException("Не удалось подключиться к хосту {h}".format(h=self._host))

        if self._logger is not None:
            self._logger.info("[{n}]: Испытание запущено".format(n=self.name))

        try:
            while not self.__exit:
                self._update()
                time.sleep(self._invfreq)
        except AttributeError:
            if self._logger is not None:
                self._logger.error("[{n}]: Связь была прервана, необходим перезапуск испытания".format(n=self.name))
            raise ModbusIOException("Связь была оборвана")
        except ConnectionException:
            if self._logger is not None:
                self._logger.error("[{n}]: Невозможно подключиться к хосту [{h}]".format(n=self.name, h=self._host))
            raise ConnectionException("Не удалось подключиться к хосту {h}".format(h=self._host))

    def exit(self):
        """ функция выхода из потока """
        self.__exit = True
        self._controller.close()  # закрываем соединение
        if self._logger is not None:
            self._logger.info("[{n}]: Испытание остановлено, соединение закрыто".format(n=self.name))
