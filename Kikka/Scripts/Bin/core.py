import sys
import os
import logging
import time
from enum import Enum


class Core:
    _instance = None

    class APP_STATE(Enum):
        HIDE = 0
        SHOW = 1
        FULL_SCREEN = 2

    def __init__(self, **kwargs):

        raise SyntaxError('can not instance, please use get_instance')

    def _init(self):
        from .shell import ShellManager
        self._shellMgr = ShellManager.get_instance()
        self._shellMgr.loadAllShell(os.path.join(sys.path[0],  r'..\Resources\Shell'))

        self._isfullscreen = False
        self._app_state = Core.APP_STATE.HIDE
        pass

    def get_instance():
        if Core._instance is None:
            Core._instance = object.__new__(Core)
            Core._instance._init()
        return Core._instance

    def isDebug(self):

        return self._debug

    def getMainWindow(self):

        return self._mainwindow

    def getAppState(self):

        return self._app_state

    def hide(self):
        self._app_state=Core.APP_STATE.HIDE
        self._mainwindow.hide()

    def show(self):
        self._app_state=Core.APP_STATE.SHOW
        self._mainwindow.show()

    def start(self, isDebug=False):
        self._debug=isDebug
        #self._app_state = APP_STATE.SHOW
        from .mainwindow import MainWindow
        self._mainwindow = MainWindow(self._debug)
        self.setSurface(0)

        from PyQt5.QtCore import QTimer
        self._lasttime = time.clock()
        self._Timer_Run = QTimer()
        self._Timer_Run.timeout.connect(self.run)
        self._Timer_Run.start(1)
        self.show()
        pass

    def run(self):
        try:
            nowtime = time.clock() 
            updatetime = (nowtime - self._lasttime) * 1000

            ret = self._shellMgr.update(updatetime)
            if ret == True:
                img = self._shellMgr.getCurImage(self.isDebug())
                self._mainwindow.setImage(img)

            self._lasttime = nowtime
        except Exception as e:
            logging.exception('Core.run: run time error')
            raise SyntaxError('run time error')
        pass

    def setSurface(self, index):
        self._shellMgr.getCurShell().setSurfaces(index)

        img = self._shellMgr.getCurImage(self.isDebug())
        self._mainwindow.setImage(img)
        
        boxes = self._shellMgr.getCollisionBoxes()
        self._mainwindow.setBoxes(boxes)


