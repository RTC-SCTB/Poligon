import threading
import time
from poligon.util import checkConfig, findAvaibleCells, parseConfig
import logging.config
from logging.handlers import QueueHandler
import datetime
import queue
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

PATH = "config.json"

logQueue = queue.Queue()
queueHandler = QueueHandler(logQueue)    # дополнительный Handler

logging.config.fileConfig('logging.conf')
rootLogger = logging.getLogger('poligonLogger')
rootLogger.addHandler(queueHandler)
formatter = rootLogger.handlers[0].formatter


rootLogger.info("Starting session on: ")
rootLogger.info(str(datetime.datetime.now()))

cells = None


def realize():
    global cells
    if cells is not None:
        raise BrokenPipeError("Объекты испытаний cells уже созданы")
    global rootLogger

    checkConfig(PATH, withCreate=True, logger=rootLogger)
    data = findAvaibleCells(PATH, logger=rootLogger)
    cells = parseConfig(data, logger=rootLogger)
    for cell in cells:
        cell.start()


def unrealize():
    global cells
    if cells is None:
        return

    for cell in cells:
        cell.exit()
        time.sleep(0.5)
        del cell
    del cells
    cells = None


def reset():
    unrealize()
    realize()


class Pult:
    def __init__(self):
        """ развертываем интерфейс из glade """
        self._isConnected = False
        self.realizeFlag = False
        self.unrealizeFlag = False
        self.resetFlag = False
        self.__exit = False

        self._builder = Gtk.Builder()
        self._builder.add_from_file("interface.glade")

        self._mainWindow = self._builder.get_object("mainWindow")
        self._connectButton = self._builder.get_object("connectButton")
        self._resetButton = self._builder.get_object("resetButton")
        self._logTextview = self._builder.get_object("logTextview")

        self._mainWindow.connect("delete-event", self.__delete_event)
        self._connectButton.connect("clicked", self.__connectButtonClick)
        self._resetButton.connect("clicked", self.__resetButtonClick)

        self._mainWindow.show_all()
        threading.Thread(daemon=True, target=self.__cyclicWrapper).start()  # включаем печать логов
        threading.Thread(daemon=True, target=Gtk.main).start()  # включаем печать логов

        while True:
            self.__cyclicCheckFlags()

    def __delete_event(self, widget, event, data=None):
        self.__exit = True
        Gtk.main_quit()

    def __connectButtonClick(self, w):
        # TODO: Перенести все, что связано с виджетами в основной поток
        def tryConnect():
            try:
                if not self._isConnected:
                    self.realizeFlag = True
                    self._clearLog()
                    realize()
                    self._resetButton.set_property("sensitive", True)
                    self._isConnected = True
                    self.realizeFlag = False
                    self._connectButton.set_label("Disconnect")
                else:
                    self.unrealizeFlag = True
                    self._resetButton.set_property("sensitive", False)
                    unrealize()
                    self._isConnected = False
                    self.unrealizeFlag = False
                    self._connectButton.set_label("Connect")
                self._connectButton.set_property("sensitive", True)
            except:
                self.realizeFlag = False
                self.unrealizeFlag = False
                self._connectButton.set_property("sensitive", True)
                self._printLog("[ERROR] - GUI error")
        threading.Thread(daemon=True, target=tryConnect).start()

    def __resetButtonClick(self, w):
        def tryReset():
            try:
                self._clearLog()
                self._connectButton.set_property("sensitive", False)
                self._resetButton.set_property("sensitive", False)
                reset()
                self._connectButton.set_property("sensitive", True)
                self._resetButton.set_property("sensitive", True)
            except:
                self._connectButton.set_property("sensitive", True)
                self._resetButton.set_property("sensitive", True)
                self._printLog("[ERROR] - GUI error")

        threading.Thread(daemon=True, target=tryReset).start()

    def _printLog(self, string):
        end_iter = self._logTextview.get_buffer().get_end_iter()  # получение итератора конца строки
        self._logTextview.get_buffer().insert(end_iter, string + '\n')

    def _clearLog(self):
        buffer = self._logTextview.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        buffer.remove_all_tags(start, end)

    def __cyclicWrapper(self):
        global logQueue
        global formatter
        while not self.__exit:
            self._printLog(formatter.format(logQueue.get()))
            time.sleep(0.05)

    def __cyclicCheckFlags(self):
        while not self.__exit:
            if self.realizeFlag or self.unrealizeFlag:
                self._connectButton.set_property("sensitive", False)
                self._resetButton.set_property("sensitive", False)
            else:
                self._connectButton.set_property("sensitive", True)
                self._resetButton.set_property("sensitive", True)
            time.sleep(0.5)


if __name__ == "__main__":
    Pult()
    Gtk.main()
