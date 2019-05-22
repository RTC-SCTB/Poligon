from pymodbus.client.sync import ModbusTcpClient

""" 
Файл базового контроллера, наследуемого остальными контроллерами
При наследовании в инициализации ниобходимо перечислить все доступные
реле, входы и выходы. 
Правила название реле входов и выходов:
Реле должно называться как Relay*, где * - номер реле,
Цифровые входы DI* и выходы DO*, где * - номер входа/выхода
Аналоговые входы AI* и выходы AO*, где * - номер входа/выхода
"""


class BaseModbusTcpController(object):
    """ Класс базового ModbusTcp контроллера """

    def __init__(self, host, unit=1):
        object.__init__(self)
        self._actorDict = {}
        self._unit = unit
        self._host = host
        self._client = ModbusTcpClient(host=host)

    def __del__(self):
        self._client.close()

    def __getattr__(self, item):
        if item != '_actorDict':
            if item not in self._actorDict and item[0] != "_":
                raise AttributeError("В данном контроллере нет " + item)
        if item[0:5] == 'Relay':
            return self._getRelayState(int(item[5:]))
        elif item[0:2] == "DO":
            return self._getDOState(int(item[2:]))
        elif item[0:2] == "DI":
            return self._getDIState(int(item[2:]))
        elif item[0:2] == "AO":
            return self._getAOState(int(item[2:]))
        elif item[0:2] == "AI":
            return self._getAIState(int(item[2:]))
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if key != '_actorDict':
            if key not in self._actorDict and key[0] != "_":
                raise AttributeError("В данном контроллере нет " + key)
        if key[0:5] == 'Relay':
            self._setRelayState(int(key[5:]), value)
        elif key[0:2] == "DO":
            self._setDOState(int(key[5:]), value)
        elif key[0:2] == "DI":
            self._setDIState(int(key[5:]), value)
        elif key[0:2] == "AO":
            self._setAOState(int(key[5:]), value)
        elif key[0:2] == "AI":
            self._setAIState(int(key[5:]), value)
        else:
            object.__setattr__(self, key, value)

    def _getRelayState(self, num):
        """ считывает значение с реле контроллера """
        return self._client.read_coils(num, 1, unit=self._unit).bits[0]

    def _setRelayState(self, num, val):
        """ устанавливает значение реле контроллера """
        self._client.write_coil(num, val, unit=self._unit)

    def _getDOState(self, num):
        """ считывает значение с реле контроллера """
        print(num)

    def _setDOState(self, num, val):
        """ устанавливает значение реле контроллера """
        print(num, val)

    def _getAOState(self, num):
        """ считывает значение с реле контроллера """
        print(num)

    def _setAOState(self, num, val):
        """ устанавливает значение реле контроллера """
        print(num, val)

    def _getDIState(self, num):
        """ считывает значение с реле контроллера """
        print(num)

    def _getAIState(self, num):
        """ считывает значение с реле контроллера """
        print(num)


if __name__ == "__main__":
    class Controller(BaseModbusTcpController):
        def __init__(self):
            BaseModbusTcpController.__init__(self, '127.0.0.1')
            self._actorDict = {
                "Relay1": 0x1,
                "DO": 0x2
            }


    controller = Controller()
    print(controller.Relay1)
    controller.Relay1 = True
    print(controller.Relay2)
