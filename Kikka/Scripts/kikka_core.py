# coding=utf-8
import time
import random
import logging
import datetime
from enum import Enum

from PyQt5.QtCore import QTimer, QObject, pyqtSignal

import kikka


class KikkaCoreSignal(QObject):
    hide = pyqtSignal()
    show = pyqtSignal()
    screenClientSizeChange = pyqtSignal()


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
        self._lastclock = time.clock()
        self._timer_interval = 10
        self._Timer_Run = QTimer()
        self._Timer_Run.setSingleShot(False)
        self.setTimerInterval(self._timer_interval)
        self.isNeedUpdate = True
        self._ghosts = {}

        self.signal = KikkaCoreSignal()
        self.signal.show.connect(self.show)
        self.signal.hide.connect(self.hide)
        self.signal.screenClientSizeChange.connect(self.screenClientSizeChange)
        kikka.memory.createTable("kikka_core")

    def getAppState(self):
        return self._app_state

    def hide(self):
        self._app_state = KikkaCore.APP_STATE.HIDE
        self.stop()
        for _, g in self._ghosts.items():
            g.hide()

    def show(self):
        self._app_state = KikkaCore.APP_STATE.SHOW
        for _, g in self._ghosts.items():
            g.show()
        self.start()

    def screenClientSizeChange(self):
        self._app_state = KikkaCore.APP_STATE.SHOW
        for _, g in self._ghosts.items():
            g.resetWindowsPosition(False)
        self.start()

    def addGhost(self, ghost):
        self._ghosts[ghost.ID] = ghost
        if not ghost.initialized:
            ghost.init()
        return ghost.ID

    def getGhost(self, gid):
        if gid in self._ghosts:
            return self._ghosts[gid]
        else:
            logging.error("getGhost: gid NOT in ghost list")
            raise ValueError

    def newGhostID(self):
        id = len(self._ghosts)
        while id in self._ghosts:
            id = random.randint()
        return id

    def setGhostSurface(self, ghost_id, soul_id, surface_id):
        if ghost_id in self._ghosts:
            self._ghosts[ghost_id].setSurface(soul_id, surface_id)

    def setGhostShell(self, ghost_id, shell_id):
        if ghost_id in self._ghosts:
            self._ghosts[ghost_id].setShell(shell_id)

    def start(self):
        self._lastclock = time.clock()
        self._Timer_Run.timeout.connect(self.run)
        self._Timer_Run.start(self._timer_interval)

    def stop(self):
        self._Timer_Run.stop()

    def setTimerInterval(self, interval):
        self._timer_interval = interval
        self._Timer_Run.setInterval(interval)

    def getTimerInterval(self):
        return self._timer_interval

    def run(self):
        try:
            nowclock = time.clock()
            updatetime = (nowclock - self._lastclock) * 1000

            for gid, ghost in self._ghosts.items():
                ghost.onUpdate(updatetime)

            self._lastclock = nowclock
        except Exception as e:
            logging.exception('Core.run: run time error')
            raise SyntaxError('run time error')

        self.isNeedUpdate = False
        pass

    def repaintAllGhost(self):
        for _, g in self._ghosts.items():
            g.repaint()

    def getProperty(self, key):
        now = datetime.datetime.now()
        if key == '':
            return None
        elif key == 'system.year':
            return now.year
        elif key == 'system.month':
            return now.month
        elif key == 'system.day':
            return now.day
        elif key == 'system.hour':
            return now.hour
        elif key == 'system.minute':
            return now.minute
        elif key == 'system.second':
            return now.second
        elif key == 'system.millisecond':
            return now.microsecond
        elif key == 'system.dayofweek':
            return now.weekday()

        elif key == 'ghostlist.count':
            return len(self._ghosts)
        else:
            logging.warning("getProperty: Unknow Key")
            return None

