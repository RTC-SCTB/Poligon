import json
import platform  # For getting the operating system name
import subprocess  # For executing a shell command
from poligon.cells import availableCells


def checkConfig(conffile, logger=None, withCreate=False):
    """ Проверка валидности конфигурационного файла """
    musthavecellkey = ("ip", "name", "controller", "invfreq")
    with open(conffile, "r") as file:
        data = json.load(file)

    if logger is not None:
        logger.info("Проверка конфигурационного файла [{f}] на валидность".format(f=conffile))

    for key in data.keys():
        if key not in availableCells.keys():
            if logger is not None:
                logger.error("Нет доступного испытания с ключом: [{k}] в списке доступных {l}".format(k=key,
                                                                                                      l=availableCells.keys()))
            raise KeyError("Нет доступного испытания с ключом: {k}".format(k=key))

    for key in data.keys():
        for i, cell in enumerate(data[key]):
            err = [attr for attr in musthavecellkey if attr not in cell]
            if len(err) != 0:
                if logger is not None:
                    logger.error(
                        "В конфигурациионном файле у испытаний {n} + [{i}] не были указаны следующие параметры: {err}".format(
                            n=key, i=i, err=err))
                raise KeyError(
                    "В конфигурациионном файле у испытаний {n} + [{i}] не были указаны следующие параметры: {err}".format(
                        n=key, i=i, err=err))

    if not withCreate:  # была произведена только предварительная проверка, без проверки подключения
        if logger is not None:
            logger.info("Предварительная проверка конфигурационного файла, без проверки подключения")
            logger.info("Проверка завершена успешно")
        return True

    for key in data.keys():
        for i, cell in enumerate(data[key]):
            cellobj = availableCells[key](host=None, controller=cell["controller"], config=cell["connection"],
                                          # создаем(внутри идет проверка подключения)
                                          name=cell["name"], invfreq=cell["invfreq"], logger=logger)
            del cellobj  # удаляем

    if logger is not None:
        logger.info("Произведена полная проверка конфигурационного файла с проверкой подключения")
        logger.info("Проверка завершена успешно")
    return True


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=subprocess.PIPE) == 0


def findAvaibleCells(conffile, logger=None):
    """ Поиск доступных испытаний """
    out = {}

    with open(conffile, "r") as file:
        data = json.load(file)

    if logger is not None:
        logger.info("Проверка наличия в сети испытаний из файла [{f}]".format(f=conffile))

    for key in data.keys():
        for i, cell in enumerate(data[key]):
            if ping(cell["ip"]):
                if out.get(key) is None:
                    out.update({key: [cell]})
                else:
                    out[key].append(cell)

                if logger is not None:
                    logger.info("[{n}] host is up: [{ip}]".format(n=cell["name"], ip=cell["ip"]))
            else:
                if logger is not None:
                    logger.info("[{n}] host is down: [{ip}]".format(n=cell["name"], ip=cell["ip"]))

    return out


def parseConfig(confDict, logger=None):
    """ Создание экземпляров испытаний из полученного словаря """
    cells = []
    for cellKey in confDict.keys():
        cellClass = availableCells[cellKey]
        for cellDesc in confDict[cellKey]:
            cell = cellClass(host=cellDesc["ip"], controller=cellDesc["controller"],
                             config=cellDesc["connection"], invfreq=cellDesc["invfreq"],
                             logger=logger, name=cellDesc["name"])
            cells.append(cell)
    return cells


if __name__ == "__main__":
    import logging

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger('test')
    fileHandler = logging.FileHandler("{0}.log".format('example'))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.INFO)

    checkConfig("testconfig.json", logger=rootLogger, withCreate=True)

    print(findAvaibleCells("testconfig.json", logger=rootLogger))