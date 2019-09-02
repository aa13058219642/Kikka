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
        self._ghost = self._soul.getGhost()
        self._shellwindow = self._ghost.getShellWindow(nid)
        self.nid = nid
        self._framelessWindowHint = True
        self.isFlip = False
        self.setWindowTitle(self._ghost.name)
        self.setContentsMargins(0, 0, 0, 0)

        self._bgImage = None
        self._bgPixmap = None
        self._bgMask = None
        pass

    def setFramelessWindowHint(self, boolean):
        self._framelessWindowHint = boolean
        if self._framelessWindowHint is False:
            self.clearMask()
            self.setWindowFlag(Qt.FramelessWindowHint, False)
            self.setWindowOpacity(0.8)
            self.setEnabled(False)

            self.show()
            offset = QPoint(self.geometry().x() - self.pos().x(), self.geometry().y() - self.pos().y())
            self.move(self.pos().x() - offset.x(), self.pos().y() - offset.y())
            self.update()
            self.activateWindow()
        else:
            sz = QSize(self.geometry().size())
            p_pos = self._ghost.getShellWindow(self.nid).pos()
            geometry = QPoint(self.geometry().x(), self.geometry().y())
            pos = QPoint(self.pos().x(), self.pos().y())
            self._ghost.memoryWrite('DialogRect',
                                    [geometry.x() - p_pos.x(), geometry.y() - p_pos.y(), sz.width(), sz.height()],
                                    self.nid)

            self.setWindowFlag(Qt.FramelessWindowHint, True)
            self.setWindowOpacity(1)
            self.setEnabled(True)
            self.setMask(self._bgMask)
            self.show()
            self.move(pos.x(), pos.y())

    def updatePosition(self):
        if self._framelessWindowHint is False:
            return

        shellwindow = self._ghost.getShellWindow(self.nid)
        p_pos = shellwindow.pos()
        p_size = shellwindow.size()
        rect = self._ghost.memoryRead('DialogRect', [], self.nid)

        if len(rect) > 0:
            x = rect[0] + p_pos.x()
            y = rect[1] + p_pos.y()
            self.resize(rect[2], rect[3])
        else:
            x = int(p_pos.x() - self.size().width())
            y = int(p_pos.y() + p_size.height() / 2 - self.size().height())
            self.resize(200, 220)
            self._ghost.memoryWrite('DialogRect',
                                    [x - p_pos.x(), y - p_pos.y(), self.size().width(), self.size().height()],
                                    self.nid)
        pass

        flip = False
        sw, sh = kikka.helper.getScreenResolution()
        if x + self.width() > sw or x < 0:
            flip = True
            x = int(p_pos.x()*2 + p_size.width() - x - self.width())
            if x + self.width() > sw:
                x = p_pos.x() - self.width()
            if x < 0:
                x = p_pos.x() + p_size.width()
        if self.isFlip != flip:
            self.isFlip = flip
            balloon = self._ghost.getBalloon()
            if balloon is not None:
                self._bgImage = self._ghost.getBalloonImage(self.size(), self.isFlip, self.nid)
                self._bgPixmap = QPixmap().fromImage(self._bgImage, Qt.AutoColor)
                self._bgMask = self._bgPixmap.mask()

        super().move(x, y)
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


