# coding=utf-8
import logging

from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel, QStyleOption, QStyle, QLineEdit, QPushButton

import kikka


class DialogWindow(QWidget):
    DIALOG_MAINMENU = 'mainmenu'
    DIALOG_TALK = 'talk'
    DIALOG_INPUT = 'input'

    def __init__(self, soul, win_id):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_DeleteOnClose)
        # self.setMouseTracking(True)
        # self.setAcceptDrops(True)

        self.ID = win_id
        self._soul = soul
        self._ghost = self._soul.getGhost()
        self._shellwindow = self._soul.getShellWindow()
        self._framelessWindowHint = True
        self.isFlip = False
        self.setWindowTitle(self._ghost.name)
        self.setContentsMargins(0, 0, 0, 0)

        self._bgImage = None
        self._bgPixmap = None
        self._bgMask = None
        self._rect = None

        self._curPage = 0
        self._widgets = {}
        self._talkLabel = None
        self._inputLineEdit = None
        self._callback = None
        self.init()

    def init(self):
        # rect
        rect = self._soul.memoryRead('DialogRect', [])
        if len(rect) > 0:
            self._rect = QRect(rect[0], rect[1], rect[2], rect[3])
            self.resize(self._rect.size())
        else:
            p_pos = self._shellwindow.pos()
            p_size = self._shellwindow.size()
            self.resize(kikka.const.WindowConst.DialogWindowDefaultSize)
            x = int(p_pos.x() - self.size().width())
            y = int(p_pos.y() + p_size.height() / 2 - self.size().height())

            self._rect = QRect(QPoint(x, y), self.size())
            rectdata = [x - p_pos.x(), y - p_pos.y(), self.size().width(), self.size().height()]
            self._soul.memoryWrite('DialogRect', rectdata)

        # default control
        self._talkLabel = QLabel()
        self._talkLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._talkLabel.setWordWrap(True)

        self._inputLabel = QLabel()
        self._inputLineEdit = QLineEdit()
        self._inputOk = QPushButton("OK")
        self._inputOk.clicked.connect(self.onInputOk)
        self._inputCancel = QPushButton("Cancel")
        self._inputCancel.clicked.connect(self.onInputCancel)

        # default UI
        talkLayout = QVBoxLayout()
        talkLayout.addWidget(self._talkLabel)
        talkWidget = QWidget(self)
        talkWidget.setContentsMargins(0, 0, 0, 0)
        talkWidget.setLayout(talkLayout)

        menuWidget = QWidget(self)
        menuWidget.setContentsMargins(0, 0, 0, 0)

        l = QHBoxLayout()
        l.addStretch()
        l.addWidget(self._inputOk)
        l.addWidget(self._inputCancel)
        inputLayout = QVBoxLayout()
        inputLayout.addWidget(self._inputLabel)
        inputLayout.addWidget(self._inputLineEdit)
        inputLayout.addLayout(l)
        inputLayout.addStretch()
        inputWidget = QWidget(self)
        inputWidget.setContentsMargins(0, 0, 0, 0)
        inputWidget.setLayout(inputLayout)

        self.setPage(self.DIALOG_MAINMENU, menuWidget)
        self.setPage(self.DIALOG_TALK, talkWidget)
        self.setPage(self.DIALOG_INPUT, inputWidget)

        self._mainLayout = QStackedLayout()
        self._mainLayout.addWidget(menuWidget)
        self.setLayout(self._mainLayout)

    def setFramelessWindowHint(self, boolean):
        self._framelessWindowHint = boolean
        if self._framelessWindowHint is False:
            self.clearMask()
            self.setWindowFlag(Qt.FramelessWindowHint, False)
            self.setWindowOpacity(0.8)
            self.setEnabled(False)

            self.show()
            self.move(2*self.pos().x() - self.geometry().x(), 2*self.pos().y() - self.geometry().y())
            self.update()
            self.activateWindow()
        else:
            self._rect.setX(self.geometry().x() - self._shellwindow.pos().x())
            self._rect.setY(self.geometry().y() - self._shellwindow.pos().y())
            self._rect.setSize(self.geometry().size())
            rectdata = [self._rect.x(), self._rect.y(), self._rect.width(), self._rect.height()]
            self._soul.memoryWrite('DialogRect', rectdata)

            pos = QPoint(self.pos().x(), self.pos().y())
            self.setWindowFlag(Qt.FramelessWindowHint, True)
            self.setWindowOpacity(1)
            self.setEnabled(True)
            self.setMask(self._bgMask)
            self.show()
            self.move(pos.x(), pos.y())

    def updatePosition(self):
        if self._framelessWindowHint is False:
            return

        p_pos = self._shellwindow.pos()
        p_size = self._shellwindow.size()
        new_x = self._rect.x() + p_pos.x()
        new_y = self._rect.y() + p_pos.y()
        self.resize(self._rect.size())

        flip = False
        sw, sh = kikka.helper.getScreenResolution()
        if new_x + self.width() > sw or new_x < 0:
            flip = True
            new_x = int(p_pos.x()*2 + p_size.width() - new_x - self.width())
            if new_x + self.width() > sw:
                new_x = p_pos.x() - self.width()
            if new_x < 0:
                new_x = p_pos.x() + p_size.width()
        if self.isFlip != flip:
            self.isFlip = flip
            self.repaint()

        super().move(new_x, new_y)

    def setPage(self, tag, qwidget):
        if tag in self._widgets:
            self._widgets[tag].deleteLater()
        qwidget.hide()
        qwidget.setParent(self)
        self._widgets[tag] = qwidget

    def getTalkLabel(self):
        return self._talkLabel

    def showInputBox(self, title, default='', callback=None):
        self._inputLabel.setText(title)
        self._inputLineEdit.setText(default)
        self._callback = callback
        self.show(self.DIALOG_INPUT)

    def show(self, pageTag=None):
        if pageTag is None:
            pageTag = self.DIALOG_MAINMENU
        elif pageTag not in self._widgets:
            logging.warning("show: page[%s] not exist" % pageTag)
            pageTag = self.DIALOG_MAINMENU

        if self._widgets[pageTag] != self._mainLayout.currentWidget():
            self._mainLayout.removeWidget(self._mainLayout.currentWidget())
            self._mainLayout.addWidget(self._widgets[pageTag])
            self._mainLayout.setCurrentIndex(0)
            self._curPage = pageTag

        param = kikka.helper.makeGhostEventParam(self._ghost.ID, self._soul.ID, kikka.const.GhostEvent.Dialog_Show, 'Show')
        param.data['pageTag'] = self._curPage
        self._ghost.emitGhostEvent(param)

        super().show()
        self.updatePosition()

    def closeEvent(self, event):
        self.setFramelessWindowHint(True)
        event.ignore()
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap().fromImage(self._bgImage, Qt.AutoColor)
        painter.drawPixmap(self.rect(), pixmap)

        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        super().paintEvent(event)

    def setBalloon(self, balloon):
        self.setMinimumSize(balloon.minimumsize)
        self.setContentsMargins(balloon.margin[0], balloon.margin[1], balloon.margin[2], balloon.margin[3])
        self.setStyleSheet(balloon.stylesheet)
        self.style().unpolish(self)
        self.style().polish(self)

    def repaint(self):
        self._bgImage = self._ghost.getBalloonImage(self.size(), self.isFlip, self.ID)
        self._bgPixmap = QPixmap().fromImage(self._bgImage, Qt.AutoColor)
        self._bgMask = self._bgPixmap.mask()
        super().repaint()

    def talkClear(self):
        self._talkLabel.setText('')

    def onTalk(self, message, speed=50):
        text = self._talkLabel.text()
        text += message
        self._talkLabel.setText(text)

    def onInputOk(self):
        if self._callback is not None:
            self._callback(self._inputLineEdit.text())
        self.hide()

    def onInputCancel(self):
        self.hide()