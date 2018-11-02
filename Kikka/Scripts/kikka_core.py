# coding=utf-8
import logging
import time
from enum import Enum

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

import kikka
from ghost import Gohst


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
        self._ghosts = []
        pass

    def getAppState(self):

        return self._app_state

    def hide(self):
        self._app_state = KikkaCore.APP_STATE.HIDE
        for g in self._ghosts:
            g.hide()

    def show(self):
        self._app_state = KikkaCore.APP_STATE.SHOW
        for g in self._ghosts:
            g.show()

    def start(self):
        # self._app_state = APP_STATE.SHOW
        self._ghosts.append(Gohst(kikka.KIKKA, 1, 0))

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

            self._ghosts[kikka.KIKKA].update(updatetime)

            self._lasttime = nowtime
        except Exception as e:
            logging.exception('Core.run: run time error')
            raise SyntaxError('run time error')

        self.isNeedUpdate = False
        pass

    def setSurface(self, gid, nid, surfaceID):
        self._ghosts[gid].setSurface(nid, surfaceID)

    def setShell(self, gid, shellID):
        self._ghosts[gid].setShell(shellID)

    def updateMenu(self):
        QApplication.instance().trayIcon.setContextMenu(kikka.menu.getMenu())
        #self._mainwindows[kikka.KIKKA].setMenu(kikka.menu)

    def update(self):
        self.isNeedUpdate = True