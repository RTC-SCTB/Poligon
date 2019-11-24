#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from poligon.util import checkConfig, findAvaibleCells
import logging
import sys
import getopt

logFormatter = logging.Formatter("%(message)s")
logger = logging.getLogger('test')
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)

configFilePath = None  # путь до файла конфигурации

""" чтение опций с коммандной строки """
try:
    opts, _ = getopt.getopt(sys.argv[1:], "hc:w", ["help", "configfile="])
    for opt, arg in opts:
        if (opt == '-h') or (opt == "--help"):
            logger.info("Используйте: \n" + sys.argv[0] + """ -c <configfilepath> \n\t """
                                                          """ --configfile=<configfilepath> """)
            sys.exit(0)
        elif (opt == '-c') or (opt == "--configfile"):
            configFilePath = arg

except getopt.GetoptError:
    logger.info("Используйте: \n" + sys.argv[0] + " --help")
    sys.exit(2)

if configFilePath is None:
    logger.info("Не был указан конфигурационный файл, используйте: \n " +
                sys.argv[0] + " -c <configfilepath>")
    sys.exit(2)

checkConfig(configFilePath, withCreate=False, logger=logger)
findAvaibleCells(configFilePath, logger=logger)
