# coding=utf-8
import logging
import time
import psutil
import ctypes
import win32gui
import win32con
import win32api
import threading
import pywintypes

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
        kikka.menu.setAppMenu(kikka.core.getGhost(gid).getSoul(0).getMenu())

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
        qapp = QApplication.instance()
        qapp.trayIcon.hide()
        qapp.exit(0)

        kikka.memory.close()
        logging.info("Bye Bye~")

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

            width = 0
            height = 0
            while 1:
                self._watchFullScreenProgress()

                width, height = self._watchScreenClientSizeChange(width, height)

                if self.isDebug is False:
                    self._watchKikkaExeProgress()

                time.sleep(3)
        except Exception:
            logging.exception("error:_guard error")
        # exit while

    def _getDesktopHwnd(self):
        def _enumWindowsCallback(hwnd, extra):
            class_name = win32gui.GetClassName(hwnd)
            if class_name != "WorkerW":
                return True
            child = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", "")
            if child == 0:
                return True
            extra.append(win32gui.FindWindowEx(child, 0, "SysListView32", "FolderView"))
            return False

        dt_hwnd = win32gui.GetDesktopWindow()
        shell_hwnd = ctypes.windll.user32.GetShellWindow()
        shell_dll_defview = win32gui.FindWindowEx(shell_hwnd, 0, "SHELLDLL_DefView", "")

        if shell_dll_defview == 0:
            sys_listview_container = []
            try:
                win32gui.EnumWindows(_enumWindowsCallback, sys_listview_container)
            except pywintypes.error as e:
                if e.winerror != 0:
                    err = win32api.GetLastError()
                    logging.warning("_getDesktopHwnd Fail: %d" % err)

            if len(sys_listview_container) > 0:
                sys_listview = sys_listview_container[0]
                shell_dll_defview = win32gui.GetParent(sys_listview)
            else:
                sys_listview = 0
        else:
            sys_listview = win32gui.FindWindowEx(shell_dll_defview, 0, "SysListView32", "FolderView")
        workerW = win32gui.GetParent(shell_dll_defview) if shell_dll_defview != 0 else 0

        # logging.info("dt_hwnd:%X  shell_hwnd:%X workerW:%X shell_dll_defview:%X sys_listview:%X " % (
        #     dt_hwnd, shell_hwnd, workerW, shell_dll_defview, sys_listview))
        return [dt_hwnd, shell_hwnd, workerW, shell_dll_defview, sys_listview]

    def _watchFullScreenProgress(self):
        hasProgress = False
        sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        fg_hwnd = win32gui.GetForegroundWindow()
        ignore_hwnd = self._getDesktopHwnd()

        if fg_hwnd not in ignore_hwnd:
            try:
                fg_rect = win32gui.GetWindowRect(fg_hwnd)
                if fg_rect[0] == 0 and fg_rect[1] == 0 and fg_rect[2] == sw and fg_rect[3] == sh:
                    hasProgress = True
            except:
                hasProgress = False

        if hasProgress != self._hasFullScreenProgress:
            self._hasFullScreenProgress = hasProgress
            if hasProgress:
                kikka.core.signal.hide.emit()
            else:
                kikka.core.signal.show.emit()

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

        if kikkaHere is False:
            logging.warning("Kikka.exe lost")
            self.exitApp()
        pass

    def _watchScreenClientSizeChange(self, old_width, old_height):
        rect = QApplication.instance().desktop().availableGeometry()
        width = rect.width()
        height = rect.height()
        if width != old_width or height != old_height:
            kikka.core.signal.screenClientSizeChange.emit()
        return width, height

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
