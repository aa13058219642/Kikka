# coding=utf-8
import logging
import time
from enum import Enum

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QApplication
from PyQt5.QtCore import QTimer

import kikka
from mainwindow import MainWindow


class KikkaCore:
    _instance = None
    isDebug = False

    class APP_STATE(Enum):
        HIDE = 0
        SHOW = 1
        FULL_SCREEN = 2

    def __init__(self, **kwargs):
        raise SyntaxError('The class is Singletion, please use Core.this() or kikka.core')

    @staticmethod
    def this():
        if KikkaCore._instance is None:
            KikkaCore._instance = object.__new__(KikkaCore)
            KikkaCore._instance._init()
        return KikkaCore._instance

    def _init(self):
        self._app_state = KikkaCore.APP_STATE.HIDE
        self._Timer_Run = None
        self._lasttime = 0
        self.isNeedUpdate = True
        self._timer_interval = 10
        self._Timer_Run = QTimer()
        pass

    def getMainWindow(self):

        return self._mainwindow

    def getAppState(self):

        return self._app_state

    def hide(self):
        self._app_state = KikkaCore.APP_STATE.HIDE
        self._mainwindow.hide()

    def show(self):
        self._app_state = KikkaCore.APP_STATE.SHOW
        self._mainwindow.show()

    def start(self):
        # self._app_state = APP_STATE.SHOW
        self._createTrayIcon()

        self._mainwindow = MainWindow(self.isDebug)
        self.setSurface(0)

        self._lasttime = time.clock()

        self._Timer_Run.timeout.connect(self.run)
        self._Timer_Run.start(self._timer_interval)
        self.show()

    def setTimerInterval(self, interval):
        self._timer_interval = interval
        self._Timer_Run.setInterval(interval)

    def getTimerInterval(self):
        return self._timer_interval

    def run(self):
        try:
            nowtime = time.clock() 
            updatetime = (nowtime - self._lasttime) * 1000

            if self.isNeedUpdate is False:
                self.isNeedUpdate = kikka.shell.update(updatetime)

            if self.isNeedUpdate is True:
                img = kikka.shell.getCurImage()
                self._mainwindow.setImage(img)

            self._lasttime = nowtime
        except Exception as e:
            logging.exception('Core.run: run time error')
            raise SyntaxError('run time error')

        self.isNeedUpdate = False
        pass

    def setSurface(self, index):
        kikka.shell.getCurShell().setSurfaces(index)

        img = kikka.shell.getCurImage()
        self._mainwindow.setImage(img)

        shell = kikka.shell.getCurShell()
        self._mainwindow.setBoxes(shell.getCollisionBoxes(), shell.getOffset())

    def _createTrayIcon(self):
        qapp = QApplication.instance()
        icon = QIcon("icon.ico")
        qapp.setWindowIcon(icon)

        qapp.trayIcon = QSystemTrayIcon(qapp)
        qapp.trayIcon.setIcon(icon)
        qapp.trayIcon.setContextMenu(kikka.menu.getMenu())
        qapp.trayIcon.show()
        qapp.trayIcon.activated.connect(self._trayIconActivated)

    def _trayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            core = kikka.core
            if core.getAppState() == core.APP_STATE.HIDE:
                core.show()
            else:
                core.hide()
        pass

    def updateMenu(self):
        QApplication.instance().trayIcon.setContextMenu(kikka.menu.getMenu())
        self._mainwindow.setMenu(kikka.menu)

    def update(self):
        self.isNeedUpdate = True