from controllers.basecontroller import BaseModbusTcpController


class ET_7060(BaseModbusTcpController):
    """ Контроллер ET-7060 от ICP-DAS """
    def __init__(self, host):
        BaseModbusTcpController.__init__(self, host)
        self._actorDict = {
            'Relay1': 0x1,
            'Relay2': 0x2,
            'Relay3': 0x3,
            'Relay4': 0x4,
            'Relay5': 0x5,
            'Relay6': 0x6
        }

