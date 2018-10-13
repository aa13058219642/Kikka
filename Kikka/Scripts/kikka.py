import sys
import logging
import threading
import psutil
import time
import win32gui
import ctypes

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon

from systemmenu import SystemMenu
from core import Core


class KikkaApp(QApplication):
    _instance = None

    def __init__(self, **kwargs):
        raise SyntaxError('can not instance, please use get_instance')

    def get_instance():
        if KikkaApp._instance is None:
            KikkaApp._instance = KikkaApp.__new__(KikkaApp)
            KikkaApp._instance._init(sys.argv)
        return KikkaApp._instance

    def _init(self, *args):
        QApplication.__init__(self, *args)

        logging.info("Hey~ Kikka here #########################################")
        self.isdebug = False
        if len(args[0]) >= 1 and "-c" in args[0]:
            self.isdebug = True
            
        self.core = Core.get_instance()
        self.runGuardThread()
        self.core.start(self.isdebug)
        self.createTrayIcon()

    def createTrayIcon(self):
        icon = QIcon("icon.ico")
        self.setWindowIcon(icon)
        self.systemmenu = SystemMenu(self)
        self.systemmenu.setCursor(Qt.PointingHandCursor)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(icon)
        self.trayIcon.setContextMenu(self.systemmenu)
        self.trayIcon.show()
        self.trayIcon.activated.connect(self.trayIconActivated)

    def trayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            core = Core.get_instance()
            if core.getAppState() == core.APP_STATE.HIDE:
                core.show()
            else:
                core.hide()
        pass

    def runGuardThread(self):
        def _guard():
            time.sleep(5)
            while 1:
                # watch fullscreen progress
                hwnd = win32gui.GetForegroundWindow()
                dhwnd = win32gui.GetDesktopWindow()
                if hwnd !=0 and dhwnd !=0:
                    drect = win32gui.GetWindowRect(dhwnd)
                    if hwnd != dhwnd and hwnd != ctypes.windll.user32.GetShellWindow():
                        rect = win32gui.GetWindowRect(hwnd)
                        if rect[0] <= drect[0] and rect[1] <= drect[1] and rect[2] <= drect[2] and rect[3] <= drect[3]:
                            Core.get_instance().hide()
                        else:
                            Core.get_instance().show()

                # watch progress Kikka.exe
                if not self.isdebug :
                    KikkaHere = False
                    pids = psutil.pids()
                    for pid in pids:
                        p = psutil.Process(pid)
                        if p.name() == 'Kikka.exe':
                            KikkaHere = True

                    if KikkaHere is False:
                        logging.warning("Kikka.exe lost")
                        self.exitApp()
                time.sleep(0.2)

        try:
            # guard thread (python thread)
            t1 = threading.Thread(target=_guard)
            t1.setDaemon(True)
            t1.start()
        except Exception:
            logging.exception("error:create guard thread fail")
        pass

    def exitApp(self):
        logging.info("Bye Bye~")
        self.exit(0)
        pass
