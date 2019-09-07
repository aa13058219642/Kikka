# coding=utf-8
import sys
import logging

from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, \
    QStyleOption, QStyle

import kikka
from kikka_balloon import Balloon


class Dialog(QWidget):
    def __init__(self, soul, nid):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_DeleteOnClose)
        # self.setMouseTracking(True)
        # self.setAcceptDrops(True)
        self._soul = soul
        self.nid = nid
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

        self.init()

    def init(self):
        rect = self._ghost.memoryRead('DialogRect', [], self.nid)
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
            self._ghost.memoryWrite('DialogRect', rectdata, self.nid)
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
            self._ghost.memoryWrite('DialogRect', rectdata, self.nid)

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
            balloon = self._ghost.getBalloon()
            if balloon is not None:
                self._bgImage = self._ghost.getBalloonImage(self._rect.size(), self.isFlip, self.nid)
                self._bgPixmap = QPixmap().fromImage(self._bgImage, Qt.AutoColor)
                self._bgMask = self._bgPixmap.mask()

        super().move(new_x, new_y)
        pass

    def show(self):
        super().show()
        self.updatePosition()
        pass

    def closeEvent(self, event):
        self.setFramelessWindowHint(True)
        event.ignore()
        pass

    def resizeEvent(self, event):
        balloon = self._ghost.getBalloon()
        if balloon is not None:
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
        self._bgImage = self._ghost.getBalloonImage(self.size(), self.isFlip, self.nid)
        self._bgPixmap = QPixmap().fromImage(self._bgImage, Qt.AutoColor)
        self._bgMask = self._bgPixmap.mask()
        super().repaint()


