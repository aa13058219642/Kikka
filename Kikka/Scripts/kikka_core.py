# coding=utf-8
import logging
import time
import random
from enum import Enum

from PyQt5.QtCore import QTimer

import kikka
from ghostbase import GhostBase


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
        self._ghosts = {}
        pass

    def getAppState(self):

        return self._app_state

    def hide(self):
        self._app_state = KikkaCore.APP_STATE.HIDE
        for _, g in self._ghosts.items():
            g.hide()

    def show(self):
        self._app_state = KikkaCore.APP_STATE.SHOW
        for _, g in self._ghosts.items():
            g.show()

    def addGhost(self, ghost):
        self._ghosts[ghost.gid] = ghost
        return ghost.gid

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

    def setGhostSurface(self, gid, nid, surfaceID):
        if gid in self._ghosts:
            self._ghosts[gid].setSurface(nid, surfaceID)

    def setGhostShell(self, gid, shellID):
        if gid in self._ghosts:
            self._ghosts[gid].setShell(shellID)

    def start(self):
        self._lasttime = time.clock()
        self._Timer_Run.timeout.connect(self.run)
        self._Timer_Run.start(self._timer_interval)

    def setTimerInterval(self, interval):
        self._timer_interval = interval
        self._Timer_Run.setInterval(interval)

    def getTimerInterval(self):
        return self._timer_interval

    def run(self):
        try:
            nowtime = time.clock()
            updatetime = (nowtime - self._lasttime) * 1000

            for gid, ghost in self._ghosts.items():
                ghost.update(updatetime)

            self._lasttime = nowtime
        except Exception as e:
            logging.exception('Core.run: run time error')
            raise SyntaxError('run time error')

        self.isNeedUpdate = False
        pass

    def repaint(self):
        for _, g in self._ghosts.items():
            g.repaint()
