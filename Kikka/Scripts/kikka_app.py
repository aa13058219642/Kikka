# coding=utf-8
import logging
import threading
import psutil
import time
import win32gui
import ctypes

from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QWidget

import kikka

class KikkaApp:
    _instance = None
    isDebug = False

    def __init__(self, **kwargs):
        raise SyntaxError('The class is Singletion, please use KikkaApp.this()')

    @staticmethod
    def this():
        if KikkaApp._instance is None:
            KikkaApp._instance = object.__new__(KikkaApp)
            KikkaApp._instance._init()
        return KikkaApp._instance

    def _init(self):
        self._hasFullScreenProgress = False
        self._hasKikkaExe = True

        self._loadingWindow = LoadingWindow()
        self._timer = QTimer()

        logging.info("")
        logging.info("Hey~ Kikka here %s" % ("-" * 40))
        kikka.memory.awake(kikka.const.KikkaMemoryFileName)

    def _load(self):
        time.sleep(1)
        # start

        kikka.shell.scanShell(kikka.helper.getPath(kikka.helper.PATH_SHELL))
        kikka.balloon.scanBalloon(kikka.helper.getPath(kikka.helper.PATH_BALLOON))

        kikka.core.start()
        kikka.app.start()

        # kikka.core.addGhost(kikka.KIKKA)
        from ghost_kikka import GhostKikka
        gid = kikka.core.addGhost(GhostKikka())
        kikka.menu.setAppMenu(kikka.core.getGhost(gid).getMenu())

        logging.info('kikka load done ################################')
        self._loadingWindow.close()
        kikka.core.show()
        pass

    def awake(self):
        self._loadingWindow.show()
        self._timer.timeout.connect(self._load)
        self._timer.setSingleShot(True)
        self._timer.start(100)

    def start(self):
        self._createGuardThread()
        self._createTrayIcon()

    def exitApp(self):
        logging.info("Bye Bye~")
        qapp = QApplication.instance()
        qapp.trayIcon.hide()
        qapp.exit(0)

    def _createGuardThread(self):
        try:
            t1 = threading.Thread(target=self._guard)
            t1.setDaemon(True)
            t1.start()
        except Exception:
            logging.exception("error:create guard thread fail")

    def _guard(self):
        try:
            time.sleep(1)
            while 1:
                result = self._watchFullScreenProgress()
                if result != self._hasFullScreenProgress:
                    self._hasFullScreenProgress = result
                    if result:
                        kikka.core.signal.hide.emit()
                    else:
                        kikka.core.signal.show.emit()

                if self.isDebug is False:
                    result = self._watchKikkaExeProgress()
                    if result is False:
                        logging.warning("Kikka.exe lost")
                        self.exitApp()

                time.sleep(3)
        except Exception:
            logging.exception("error:_guard error")
        # exit while

    def _watchFullScreenProgress(self):
        hasFullScreenProgress = False
        foreground_hwnd = win32gui.GetForegroundWindow()
        desktop_hwnd = win32gui.GetDesktopWindow()
        my_hwnd = ctypes.windll.user32.GetShellWindow()
        #logging.info("watchFullScreenProgress foreground_hwnd:%X desktop_hwnd:%X my_hwnd:%X"%(foreground_hwnd,desktop_hwnd,my_hwnd))

        if foreground_hwnd != 0 \
        and desktop_hwnd != 0 \
        and foreground_hwnd != desktop_hwnd \
        and foreground_hwnd != my_hwnd:
            frect = win32gui.GetWindowRect(foreground_hwnd)
            drect = win32gui.GetWindowRect(desktop_hwnd)

            #logging.info("%s, %s"%(frect,drect))
            if frect[0] == drect[0] \
            and frect[1] == drect[1] \
            and frect[2] == drect[2] \
            and frect[3] == drect[3]:
                hasFullScreenProgress = True
        return hasFullScreenProgress

    def _watchKikkaExeProgress(self):
        kikkaHere = False
        pids = psutil.pids()
        for pid in pids:
            try:
                p = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            if p.name() == 'Kikka.exe':
                kikkaHere = True
        return kikkaHere

    def _createTrayIcon(self):
        qapp = QApplication.instance()
        icon = QIcon("icon.ico")
        qapp.setWindowIcon(icon)

        qapp.trayIcon = QSystemTrayIcon(qapp)
        qapp.trayIcon.setIcon(icon)
        qapp.trayIcon.show()
        qapp.trayIcon.activated.connect(self._trayIconActivated)

    def _trayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if kikka.core.getAppState() == kikka.core.APP_STATE.HIDE:
                kikka.core.show()
            else:
                kikka.core.hide()
        pass


class LoadingWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self._image = kikka.helper.getImage(kikka.helper.getPath(kikka.helper.PATH_RESOURCES)+"/loading.png")
        self.resize(self._image.width(), self._image.height())
        (w, h) = kikka.helper.getScreenClientRect()
        self.move(w-self._image.width(), h-self._image.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self._image)
        super().paintEvent(event)
