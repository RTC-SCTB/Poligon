from pymodbus.client.sync import ModbusTcpClient

""" 
Файл базового контроллера, наследуемого остальными контроллерами
При наследовании в инициализации ниобходимо перечислить все доступные
реле, входы и выходы. 
Правила название реле входов и выходов:
Реле должно называться как Relay*, где * - номер реле,
Цифровые входы DI* и выходы DO*, где * - номер входа/выхода
Аналоговые входы AI* и выходы AO*, где * - номер входа/выхода
Перечисление производится в словаре _actorDict в формате - {Название устройства: адресс} 
Пример:
_actorDict = {
    Relay1: 0x01,
    DO: 0x05
}
"""


class BaseModbusTcpController(object):
    """ Класс базового ModbusTcp контроллера """
    def __init__(self, host, unit=1):
        object.__init__(self)
        self._actorDict = {}    # словарь доступных контроллеру устройств, с их аддресами
        self._unit = unit   # modbus адресс контроллера
        self._host = host   # адресс контроллера
        self._client = ModbusTcpClient(host=host)   # modbus - клиент

    def __del__(self):
        self._client.close()

    def __getattr__(self, item):
        if item != '_actorDict':
            if item not in self._actorDict and item[0] != "_":
                raise AttributeError("В данном контроллере нет " + item)
        if item[0:5] == 'Relay':
            return self._getRelayState(self._actorDict[item])
        elif item[0:2] == "DO":
            return self._getDOState(self._actorDict[item])
        elif item[0:2] == "DI":
            return self._getDIState(self._actorDict[item])
        elif item[0:2] == "AO":
            return self._getAOState(self._actorDict[item])
        elif item[0:2] == "AI":
            return self._getAIState(self._actorDict[item])
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if key != '_actorDict':
            if key not in self._actorDict and key[0] != "_":
                raise AttributeError("В данном контроллере нет " + key)
        if key[0:5] == 'Relay':
            self._setRelayState(self._actorDict[key], value)
        elif key[0:2] == "DO":
            self._setDOState(self._actorDict[key], value)
        elif key[0:2] == "DI":
            self._setDIState(self._actorDict[key], value)
        elif key[0:2] == "AO":
            self._setAOState(self._actorDict[key], value)
        elif key[0:2] == "AI":
            self._setAIState(self._actorDict[key], value)
        else:
            object.__setattr__(self, key, value)

    @property
    def actorDict(self):
        return self._actorDict

    def _getRelayState(self, addr):
        """ считывает значение с реле контроллера """
        return self._client.read_coils(addr, 1, unit=self._unit).bits[0]

    def _setRelayState(self, addr, val):
        """ устанавливает значение реле контроллера """
        self._client.write_coil(addr, val, unit=self._unit)

    def _getDOState(self, addr):
        """ считывает значение с дискретного выхода контроллера """
        pass    # TODO: Доделать, когда придет контроллер другого типа

    def _setDOState(self, addr, val):
        """ устанавливает значение дискретного выхода  контроллера """
        pass    # TODO: Доделать, когда придет контроллер другого типа

    def _getAOState(self, addr):
        """ считывает значение с аналогового выхода контроллера """
        pass    # TODO: Доделать, когда придет контроллер другого типа

    def _setAOState(self, addr, val):
        """ устанавливает значение аналогового выхода контроллера """
        pass    # TODO: Доделать, когда придет контроллер другого типа

    def _getDIState(self, addr):
        """ считывает значение с дискретного входа контроллера """
        return self._client.read_discrete_inputs(addr, 1, unit=1).bits[0]

    def _getAIState(self, addr):
        """ считывает значение с аналогового входа контроллера """
        pass    # TODO: Доделать, когда придет контроллер другого типа


if __name__ == "__main__":
    class Controller(BaseModbusTcpController):
        def __init__(self):
            BaseModbusTcpController.__init__(self, '127.0.0.1')
            self._actorDict = {
                "Relay1": 0x1,
                "DO": 0x2
            }


    controller = Controller()
    print(controller.actorDict)
    print(controller.Relay1)
    controller.Relay1 = True
    print(controller.Relay2)
