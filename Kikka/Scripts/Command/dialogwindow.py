# coding=utf-8
import sys
import logging

from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, \
    QStyleOption, QStyle

import kikka
from kikka_balloon import Balloon


class DialogWindow(QWidget):
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

        self._talkLayout = QVBoxLayout()
        self._talkLabel = QLabel()
        self._talkLabel.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self._talkLabel.setWordWrap(True)
        self._talkLayout.addWidget(self._talkLabel)

        self._menuWidget = QWidget(self)
        self._menuWidget.setContentsMargins(0, 0, 0, 0)

        self._talkWidget = QWidget(self)
        self._talkWidget.setContentsMargins(0, 0, 0, 0)
        self._talkWidget.setLayout(self._talkLayout)

        self._mainLayout = QStackedLayout()
        self._mainLayout.addWidget(self._menuWidget)
        self._mainLayout.addWidget(self._talkWidget)
        self.setLayout(self._mainLayout)
        self.init()

    def init(self):
        rect = self._soul.memoryRead('DialogRect', [])
        if len(rect)>0:
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
        pass

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

    def show(self):
        super().show()
        self.updatePosition()

    def showMenu(self):
        self._mainLayout.setCurrentIndex(0)
        self.show()

    def showTalk(self):
        self._mainLayout.setCurrentIndex(1)
        self.show()

    def closeEvent(self, event):
        self.setFramelessWindowHint(True)
        event.ignore()
        pass

    def resizeEvent(self, event):
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

    def repaint(self):
        self._bgImage = self._ghost.getBalloonImage(self.size(), self.isFlip, self.ID)
        self._bgPixmap = QPixmap().fromImage(self._bgImage, Qt.AutoColor)
        self._bgMask = self._bgPixmap.mask()
        super().repaint()

    def setMenuLayout(self, layout):
        self._menuWidget.setLayout(layout)
        pass

    def talkClear(self):
        self._talkLabel.setText('')

    def onTalk(self, message, speed=50):
        text = self._talkLabel.text()
        text +=message
        self._talkLabel.setText(text)
        pass
