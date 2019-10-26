# coding=utf-8
import logging
import random

from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout

import kikka
from kikka_const import SurfaceEnum, GhostEvent
from ghostbase import GhostBase

KIKKA = 0
TOWA = 1

class GhostKikka(GhostBase):

    def __init__(self, gid=-1, name='Kikka'):
        GhostBase.__init__(self, gid, name)
        w_kikka = self.addWindow(KIKKA, 0)
        w_towa = self.addWindow(TOWA, 10)

        self.initLayout()
        self.initMenu()

    def initMenu(self):
        # mainmenu = self.getMenu(KIKKA)
        # menu = Menu(mainmenu.parent(), self.ID, "kikka menu")
        # mainmenu.insertMenu(mainmenu.actions()[0], menu)
        #
        # def _test_callback(index=0, title=''):
        #     logging.info("GhostKikka_callback: click [%d] %s" % (index, title))
        #
        # act = menu.addMenuItem("111", _test_callback)
        # act.setShortcut(QKeySequence("Ctrl+T"))
        # act.setShortcutContext(Qt.ApplicationShortcut)
        # act.setShortcutVisibleInContextMenu(True)
        #
        #
        # w = self.getShellWindow(KIKKA)
        # w.addAction(act)
        pass

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

        callback_ResizeWindow = lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, GhostEvent.CustomEvent, 'ResizeWindow', {'bool':False, 'SoulID':KIKKA}))
        callback_CloseDialog = lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, GhostEvent.CustomEvent, 'CloseDialog', {'bool':False, 'SoulID':KIKKA}))

        # 2.1 page1
        for i in range(3):
            girdlayout = self._girdlayouts[i]
            for j in range(5):
                but = QPushButton("move%d(%d)" % (i, j))
                but.clicked.connect(callback_ResizeWindow)
                girdlayout.addWidget(but, j, 0)

                but2 = QPushButton("close%d(%d)" % (i, j))
                but2.clicked.connect(callback_CloseDialog)
                girdlayout.addWidget(but2, j, 1)
            but = QPushButton("move%d(%d)" % (i, 5))
            but.clicked.connect(callback_ResizeWindow)
            girdlayout.addWidget(but, 5, 0)
        dlg.setLayout(self._mainLayout)

    def ghostEvent(self, param):
        super().ghostEvent(param)

        self.surfaceEvent(param)
        if param.eventType == GhostEvent.CustomEvent:
            if param.eventTag == 'ResizeWindow':
                self.resizeWindow(param)
            elif param.eventTag == 'CloseDialog':
                self.closeDlg(param)

    def surfaceEvent(self, param):
        ghost = kikka.core.getGhost(param.ghostID)
        sid = param.data['SoulID']
        if sid == KIKKA:
            if param.eventType == GhostEvent.MouseTouch:
                if param.eventTag == 'Head':
                    faceID = random.choice([SurfaceEnum.NORMAL, SurfaceEnum.SHY, SurfaceEnum.HAPPINESS, SurfaceEnum.SHY2])
                    ghost.setSurface(sid, faceID)
                elif param.eventTag == 'Face':
                    ghost.setSurface(sid, SurfaceEnum.EYE_CLOSURE)
                elif param.eventTag == 'Bust':
                    ghost.setSurface(sid, SurfaceEnum.DISAPPOINTED)
        elif sid == TOWA:
            pass
        pass

    def changeShell(self, shellID):
        logging.debug("Please don't peek at me to change clothes!")
        GhostBase.changeShell(self, shellID)

    # ########################################################################################################
    def resizeWindow(self, param):
        dlg = kikka.core.getGhost(param.ghostID).getDialog(param.data['SoulID'])
        dlg.setFramelessWindowHint(param.data['bool'])

    def closeDlg(self, param):
        kikka.core.getGhost(param.ghostID).getDialog(param.data['SoulID']).hide()

