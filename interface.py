#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from poligon.util import checkConfig, findAvaibleCells, parseConfig
import logging.config
import datetime

PATH = "config.json"

logging.config.fileConfig('logging.conf')
rootLogger = logging.getLogger('poligonLogger')

rootLogger.info("Starting session on: ")
rootLogger.info(str(datetime.datetime.now()))
rootLogger.info("Press Enter to connect/disconnect, Space to reset and ctrl+C to exit")

cells = None


def realize():
    global cells
    if cells is not None:
        raise BrokenPipeError("Объекты испытаний cells уже созданы")
    global rootLogger
    rootLogger.info("Создание экземпляров испытаний полигона")
    checkConfig(PATH, withCreate=True, logger=rootLogger)
    data = findAvaibleCells(PATH, logger=rootLogger)
    cells = parseConfig(data, logger=rootLogger)
    for cell in cells:
        cell.start()
    rootLogger.info("Создание экземпляров прошло успешно, произведен запуск найденных испытаний\n")


def unrealize():
    global cells
    if cells is None:
        return
    rootLogger.info("Удаление экземпляров испытаний полигона")
    for cell in cells:
        cell.exit()
        time.sleep(0.2)
        del cell
    del cells
    cells = None
    rootLogger.info("Экземпляры испытаний были уданены\n")


def reset():
    rootLogger.info("Перезапуск полигона")
    unrealize()
    realize()
    rootLogger.info("Перезапуск полигона прошел успешно\n")


if __name__ == "__main__":
    from pynput.keyboard import Key, Listener
    runFlag = False     # флаг, говорящий, что уже выполняется какое-то действие
    connectDisconnectFlag = False    # флаг отвечающий за включение или выключение
    stateFlag = False   # состояние полигона
    resetFlag = False

    def onPress(key):
        pass

    def onRelease(key):
        global runFlag
        global connectDisconnectFlag
        global resetFlag
        if key == Key.enter:
            if not runFlag:
                connectDisconnectFlag = True

        if key == Key.space:
            if not runFlag and not connectDisconnectFlag:
                resetFlag = True

    keyboard = Listener(on_press=onPress, on_release=onRelease)
    keyboard.start()

    try:
        while True:
            if connectDisconnectFlag:
                runFlag = True
                if not stateFlag:
                    realize()
                    stateFlag = True
                else:
                    unrealize()
                    stateFlag = False
                connectDisconnectFlag = False
                runFlag = False

            elif resetFlag:
                if stateFlag:
                    runFlag = True
                    reset()
                    runFlag = False
                resetFlag = False
            time.sleep(0.1)

    except KeyboardInterrupt:
        unrealize()
        keyboard.stop()
