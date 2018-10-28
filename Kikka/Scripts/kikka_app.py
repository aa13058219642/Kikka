# coding=utf-8
import logging
import threading
import psutil
import time
import win32gui
import ctypes

from PyQt5.QtWidgets import QApplication

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
        logging.info("Hey~ Kikka here %s" % ("-" * 40))
        pass

    def start(self):
        self._createGuardThread()

    def exitApp(self):
        logging.info("Bye Bye~")
        QApplication.instance().exit(0)
        pass

    def _createGuardThread(self):
        try:
            t1 = threading.Thread(target=self._guard)
            t1.setDaemon(True)
            t1.start()
        except Exception:
            logging.exception("error:create guard thread fail")

    def _guard(self):
        time.sleep(1)
        while 1:
            result = self._watchFullScreenProgress()
            if result != self._hasFullScreenProgress:
                self._hasFullScreenProgress = result
                if result: kikka.core.hide()
                else: kikka.core.show()

            if self.isDebug is False:
                result = self._watchKikkaExeProgress()
                if result is False:
                    logging.warning("Kikka.exe lost")
                    self.exitApp()

            time.sleep(0.5)
        # exit while

    def _watchFullScreenProgress(self):
        hasFullScreenProgress = False
        hwnd = win32gui.GetForegroundWindow()
        dhwnd = win32gui.GetDesktopWindow()
        if hwnd != 0 and dhwnd != 0:
            drect = win32gui.GetWindowRect(dhwnd)
            if hwnd != dhwnd and hwnd != ctypes.windll.user32.GetShellWindow():
                rect = win32gui.GetWindowRect(hwnd)
                if rect[0] <= drect[0] \
                        and rect[1] <= drect[1] \
                        and rect[2] <= drect[2] \
                        and rect[3] <= drect[3]:
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
