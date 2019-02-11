# coding=utf-8
import logging

from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPixmap, QPainter, QKeySequence
from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout

import kikka
from ghostevent import GhostEvent
from kikka_shell import Surface
from ghostbase import GhostBase
from kikka_menu import Menu


KIKKA = 0
TOWA = 1

class GhostKikka(GhostBase):
    def __init__(self, gid=-1, name='Kikka'):
        GhostBase.__init__(self, gid, name)
        self.setShell(16)
        self.setBalloon(0)
        w_kikka = self.addWindow(KIKKA, 0)
        w_towa = self.addWindow(TOWA, 10)

        self.initEvent()
        self.initLayout()
        self.initMenu()

    def initMenu(self):
        mainmenu = self.getMenu(KIKKA)
        menu = Menu(mainmenu.parent(), self.gid, "kikka menu")
        mainmenu.insertMenu(mainmenu.actions()[0], menu)

        def _test_callback(index=0, title=''):
            logging.info("GhostKikka_callback: click [%d] %s" % (index, title))

        act = menu.addMenuItem("111", _test_callback)
        act.setShortcut(QKeySequence("Ctrl+T"))
        act.setShortcutContext(Qt.ApplicationShortcut)
        # act.setShortcutContext(Qt.ApplicationShortcut)
        act.setShortcutVisibleInContextMenu(True)


        w = self.getShellWindow(KIKKA)
        w.addAction(act)


        # w.s




    def initLayout(self):
        dlg = self.getDialog(KIKKA)

        self._mainLayout = QVBoxLayout()
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._stackedLayout = QStackedLayout()
        self._topLayout = QVBoxLayout()

        # 0 main Layout
        self._mainLayout.addLayout(self._topLayout)
        self._mainLayout.addLayout(self._stackedLayout)

        # 1.0 top layout
        self._toplabel = QLabel("Hello")
        self._toplabel.setObjectName('Hello')
        self._topLayout.addWidget(self._toplabel)

        # 1.2 tab layout
        self._tabLayout = QHBoxLayout()
        self._topLayout.addLayout(self._tabLayout)

        # 1.2.1 tab button
        p1 = QPushButton("page1")
        p2 = QPushButton("page2")
        p3 = QPushButton("page3")
        p1.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(0))
        p2.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(1))
        p3.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(2))
        self._tabLayout.addWidget(p1)
        self._tabLayout.addWidget(p2)
        self._tabLayout.addWidget(p3)

        # 2.0 gird layouts
        self._girdlayouts = []
        for i in range(3):
            girdlayout = QGridLayout()
            self._girdlayouts.append(girdlayout)

            page = QWidget(dlg)
            page.setLayout(girdlayout)
            self._stackedLayout.addWidget(page)

        # 2.1 page1
        callbackfunc = lambda : self.event_selector(GhostEvent.CustomEvent, 'ResizeWindow', bool=False, nid=KIKKA)
        for i in range(3):
            girdlayout = self._girdlayouts[i]
            for j in range(5):
                but = QPushButton("move%d(%d)" % (i, j))
                but.clicked.connect(callbackfunc)
                girdlayout.addWidget(but, j, 0)

                but2 = QPushButton("close%d(%d)" % (i, j))
                but2.clicked.connect(lambda : self.event_selector(GhostEvent.CustomEvent, 'CloseDialog', nid=KIKKA))
                girdlayout.addWidget(but2, j, 1)
            but = QPushButton("move%d(%d)" % (i, 5))
            but.clicked.connect(callbackfunc)
            girdlayout.addWidget(but, 5, 0)
        dlg.setLayout(self._mainLayout)

    def initEvent(self):
        e = {}

        tag = ['Head', 'Face', 'Bust', 'Hand']
        e[GhostEvent.MouseDown] = {}
        e[GhostEvent.MouseDown]['Head'] = head_click
        e[GhostEvent.MouseDown]['Face'] = face_click
        e[GhostEvent.MouseDown]['Bust'] = bust_click
        e[GhostEvent.MouseDown]['Hand'] = hand_click

        e[GhostEvent.MouseMove] = {}
        e[GhostEvent.MouseMove]['Head'] = head_touch
        e[GhostEvent.MouseMove]['Face'] = face_touch
        e[GhostEvent.MouseMove]['Bust'] = bust_touch
        e[GhostEvent.MouseMove]['Hand'] = hand_touch

        e[GhostEvent.MouseDoubleClick] = {}
        e[GhostEvent.MouseDoubleClick]['Head'] = head_doubleclick
        e[GhostEvent.MouseDoubleClick]['Face'] = face_doubleclick
        e[GhostEvent.MouseDoubleClick]['Bust'] = bust_doubleclick
        e[GhostEvent.MouseDoubleClick]['Hand'] = hand_doubleclick

        e[GhostEvent.CustomEvent]={}
        e[GhostEvent.CustomEvent]['ResizeWindow'] = resizeWindow
        e[GhostEvent.CustomEvent]['CloseDialog'] = closeDlg
        self.eventlist = e

    def changeShell(self, shellID):
        logging.debug("Please don't peek at me to change clothes!")
        self.hide()
        self.setShell(shellID)
        self.show()

# ########################################################################################################
def resizeWindow(**kwargs):
    dlg = kikka.core.getGhost(kwargs['gid']).getDialog(kwargs['nid'])
    dlg.setFramelessWindowHint(kwargs['bool'])


def closeDlg(**kwargs):
    kikka.core.getGhost(kwargs['gid']).getDialog(kwargs['nid']).hide()


def head_touch(**kwargs):
    logging.info("head_touch")
    if kwargs['nid'] == KIKKA:
        kikka.core.getGhost(kwargs['gid']).setSurface(kwargs['nid'], Surface.ENUM_JOY)
    pass


def head_click(**kwargs):
    logging.info("head_click")
    pass


def head_doubleclick(**kwargs):
    logging.info("head_doubleclick")
    pass


def face_touch(**kwargs):
    logging.info("face_touch")
    if kwargs['nid'] == KIKKA:
        kikka.core.getGhost(kwargs['gid']).setSurface(kwargs['nid'], Surface.ENUM_ANGER2)
    pass


def face_click(**kwargs):
    logging.info("face_click")
    pass


def face_doubleclick(**kwargs):
    logging.info("face_doubleclick")
    pass


def bust_touch(**kwargs):
    logging.info("bust_touch")
    if kwargs['nid'] == KIKKA:
        kikka.core.getGhost(kwargs['gid']).setSurface(kwargs['nid'], Surface.ENUM_NORMAL)
    pass


def bust_click(**kwargs):
    logging.info("bust_click")
    pass


def bust_doubleclick(**kwargs):
    logging.info("bust_doubleclick")
    pass


def hand_touch(**kwargs):
    logging.info("hand_touch")
    pass


def hand_click(**kwargs):
    logging.info("hand_click")
    pass


def hand_doubleclick(**kwargs):
    logging.info("hand_doubleclick")
    pass





