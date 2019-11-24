from poligon.controllers.basecontroller import BaseModbusTcpController


class ET_7060(BaseModbusTcpController):
    """ Контроллер ET-7060 от ICP-DAS """
    def __init__(self, host, *args, **kwargs):
        BaseModbusTcpController.__init__(self, host, *args, **kwargs)
        self._actorDict = {
            'Relay0': 0x0,
            'Relay1': 0x1,
            'Relay2': 0x2,
            'Relay3': 0x3,
            'Relay4': 0x4,
            'Relay5': 0x5,
            'DI0': 0x00,
            'DI1': 0x01,
            'DI2': 0x02,
            'DI3': 0x03,
            'DI4': 0x04,
            'DI5': 0x05,
        }

