# coding=utf-8
import logging
import time
from enum import Enum

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QApplication
from PyQt5.QtCore import QTimer

import kikka
from mainwindow import MainWindow
from dialogwindow import Dialog
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
        self._mainwindows = []
        self._dialogs = []
        self._ghosts = []
        pass

    def getMainWindow(self, nid):
        if 0 <= nid < len(self._mainwindows):
            return self._mainwindows[nid]
        else:
            return None

    def getDialog(self, nid):
        if 0 <= nid < len(self._dialogs):
            return self._dialogs[nid]
        else:
            return None

    def getAppState(self):

        return self._app_state

    def hide(self):
        self._app_state = KikkaCore.APP_STATE.HIDE
        for window in self._mainwindows:
            window.hide()
        for dialog in self._dialogs:
            dialog.hide()

    def show(self):
        self._app_state = KikkaCore.APP_STATE.SHOW
        # for window in self._mainwindows:
        #     window.show()
        for g in self._ghosts:
            g.show()


    def start(self):
        # self._app_state = APP_STATE.SHOW
        # window = MainWindow(kikka.KIKKA)
        # self._mainwindows.append(window)
        # dialog = Dialog(window, kikka.balloon.getCurrentBalloon())
        # self._dialogs.append(dialog)
        # self.setSurface(kikka.KIKKA, 0)

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

            # if self.isNeedUpdate is False:
            #     self.isNeedUpdate = kikka.shell.update(updatetime)

            #if self.isNeedUpdate is True:
                #img = kikka.shell.getImage()
                #self._mainwindows[kikka.KIKKA].setImage(img)
            self._ghosts[kikka.KIKKA].update(updatetime)

            self._lasttime = nowtime
        except Exception as e:
            logging.exception('Core.run: run time error')
            raise SyntaxError('run time error')

        self.isNeedUpdate = False
        pass

    def setSurface(self, gid, nid, surfaceID):
        self._ghosts[gid].setSurface(nid, surfaceID)
        # kikka.shell.getCurShell().setSurfaces(surfaceID)
        #
        # img = kikka.shell.getImage()
        # self._mainwindows[nid].setImage(img)
        #
        # shell = kikka.shell.getCurShell()
        # self._mainwindows[nid].setBoxes(shell.getCollisionBoxes(), shell.getOffset())

    def updateMenu(self):
        QApplication.instance().trayIcon.setContextMenu(kikka.menu.getMenu())
        #self._mainwindows[kikka.KIKKA].setMenu(kikka.menu)

    def update(self):
        self.isNeedUpdate = True