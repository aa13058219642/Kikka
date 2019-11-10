# coding=utf-8
import os
import time
import logging
import datetime

from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap

import kikka
from kikka_menu import MenuStyle
from soul import Soul
from kikka_helper import GhostEventParam


class KikkaGhostSignal(QObject):
    ghostEvent = pyqtSignal(GhostEventParam)


class GhostBase:

    def __init__(self, ghost_id=-1, name=''):
        self.ID = ghost_id if ghost_id != -1 else kikka.core.newGhostID()
        self.name = name
        self.initialized = False
        self.shell = None
        self.signal = KikkaGhostSignal()

        self._souls = OrderedDict()
        self._shell_image = {}
        self._balloon_image = {}

        self._eventlist = {}
        self._balloon = None
        self._balloon_image_cache = None
        self._menustyle = None
        self._isLockOnTaskbar = True
        self._datetime = datetime.datetime.now()

    def init(self):
        # create ghost table
        kikka.memory.createTable(str('ghost_' + self.name))

        # update boot time
        boot_last = datetime.datetime.fromtimestamp(self.memoryRead('BootThis', time.time()))
        boot_this = datetime.datetime.now()
        self.memoryWrite('BootLast', boot_last.timestamp())
        self.memoryWrite('BootThis', boot_this.timestamp())

        # get option
        self.setShell(self.memoryRead('CurrentShellName', ''))
        self.setBalloon(self.memoryRead('CurrentBalloonName', ''))
        self.setIsLockOnTaskbar(self.memoryRead('isLockOnTaskbar', True))
        self.signal.ghostEvent.connect(self.ghostEvent)

        self.initialized = True

    def show(self):
        for soul in reversed(self._souls.values()):
            soul.show()

    def hide(self):
        for soul in self._souls.values():
            soul.hide()

    def addSoul(self, soul_id, surface_id=0):
        if soul_id in self._souls.keys():
            logging.error("addSoul: the soul ID %d exits" % soul_id)
            return None
        self._souls[soul_id] = Soul(self, soul_id, surface_id)
        return self._souls[soul_id]

    def getSoul(self, soul_id):
        return self._souls[soul_id] if soul_id in self._souls.keys() else None

    def getSoulCount(self):
        return len(self._souls)

    def changeShell(self, shellname):
        self.hide()
        self.setShell(shellname)
        self.show()

    def reloadShell(self, shellname=None):
        if shellname is None:
            shellname = self.shell.name
        self.shell = kikka.shell.getShell(shellname)
        if self.shell is None:
            self.shell = kikka.shell.getShellByIndex(0)
            if self.shell is None:
                raise ValueError("setShell: load defalut shell fail.")

        self.shell.load()
        self._menustyle = MenuStyle(self.shell.shellmenustyle)

        self._shell_image = {}
        for filename in self.shell.pnglist:
            p = os.path.join(self.shell.resource_path, filename)
            if p == self.shell.shellmenustyle.background_image \
                    or p == self.shell.shellmenustyle.foreground_image \
                    or p == self.shell.shellmenustyle.sidebar_image:
                continue
            self._shell_image[filename] = kikka.helper.getImage(p)

        for sid, soul in self._souls.items():
            soul.setSurface(-1)
            soul.updateClothesMenu()
            soul.move(soul.pos())

    def setShell(self, shellname):
        if self.shell is not None and self.shell.name == shellname:
            return
        self.reloadShell(shellname)
        self.memoryWrite('CurrentShellName', self.shell.name)

    def getShell(self):
        return self.shell

    def setBalloon(self, name):
        self._balloon = kikka.balloon.getBalloon(name)
        if self._balloon is None:
            self._balloon = kikka.balloon.getBalloonByIndex(0)
            if self._balloon is None:
                raise ValueError("setBalloon: load defalut balloon fail.")

        self._balloon.load()

        for parent, dirnames, filenames in os.walk(self._balloon.resource_path):
            for filename in filenames:
                if filename[len(filename) - 4:] == '.png':
                    p = os.path.join(self._balloon.resource_path, filename)
                    self._balloon_image[filename] = kikka.helper.getImage(p)
        self._balloon_image_cache = self._balloon_image['background.png']

        for soul in self._souls.values():
            soul.setBalloon(self._balloon)

        self.memoryWrite('CurrentBalloonName', self._balloon.name)

    def getBalloon(self):
        return self._balloon

    def resetWindowsPosition(self, usingDefaultPos=True, lockOnTaskbar=False):
        rightOffect = 0
        for soul in self._souls.values():
            soul.resetWindowsPosition(usingDefaultPos, lockOnTaskbar | self._isLockOnTaskbar, rightOffect)
            rightOffect += soul.getSize().width()

    def setIsLockOnTaskbar(self, isLock):
        self._isLockOnTaskbar = isLock
        self.memoryWrite("isLockOnTaskbar", isLock)
        self.resetWindowsPosition(False)

    def getIsLockOnTaskbar(self):
        return self._isLockOnTaskbar

    # surface ###################################################################################

    def getBalloonImage(self, size: QSize, flip=False, soul_id=-1):
        if self._balloon is None:
            logging.warning("getBalloonImage: balloon is None")
            return kikka.helper.getDefaultImage()

        drect = []
        # calculate destination rect
        if len(self._balloon.clipW) == 3:
            dw = [self._balloon.clipW[0],
                  size.width() - self._balloon.clipW[0] - self._balloon.clipW[2],
                  self._balloon.clipW[2]]
        elif len(self._balloon.clipW) == 5:
            sw = size.width() - self._balloon.clipW[0] - self._balloon.clipW[2] - self._balloon.clipW[4]
            dw = [self._balloon.clipW[0],
                  sw // 2,
                  self._balloon.clipW[2],
                  sw - sw // 2,
                  self._balloon.clipW[4]]
        else:
            sw = size.width() // 3
            dw = [sw, size.width() - sw*2, sw]

        if len(self._balloon.clipH) == 3:
            dh = [self._balloon.clipH[0],
                  size.height() - self._balloon.clipH[0] - self._balloon.clipH[2],
                  self._balloon.clipH[2]]
        elif len(self._balloon.clipH) == 5:
            sh = size.height() - self._balloon.clipH[0] - self._balloon.clipH[2] - self._balloon.clipH[4]
            dh = [self._balloon.clipH[0],
                  sh // 2,
                  self._balloon.clipH[2],
                  sh - sh // 2,
                  self._balloon.clipH[4]]
        else:
            sh = size.height() // 3
            dh = [sh, size.height() - sh*2, sh]

        for y in range(len(self._balloon.clipH)):
            dr = []
            for x in range(len(self._balloon.clipW)):
                pt = QPoint(0, 0)
                if x > 0: pt.setX(dr[x-1].x() + dw[x-1])
                if y > 0: pt.setY(drect[y-1][0].y() + dh[y-1])
                sz = QSize(dw[x], dh[y])
                dr.append(QRect(pt, sz))
            drect.append(dr)
        pass  # exit for

        # paint balloon image
        img = QImage(size, QImage.Format_ARGB32)
        pixmap = QPixmap().fromImage(self._balloon_image_cache, Qt.AutoColor)
        painter = QPainter(img)
        painter.setCompositionMode(QPainter.CompositionMode_Source)

        for y in range(len(self._balloon.clipH)):
            for x in range(len(self._balloon.clipW)):
                painter.drawPixmap(drect[y][x], pixmap, self._balloon.bgRect[y][x])
        painter.end()

        # flip or not
        if self._balloon.flipBackground is True and flip is True:
            img = img.mirrored(True, False)
            if self._balloon.noFlipCenter is True and len(self._balloon.clipW) == 5 and len(self._balloon.clipH) == 5:
                painter = QPainter(img)
                painter.setCompositionMode(QPainter.CompositionMode_Source)
                painter.drawPixmap(drect[2][2], pixmap, self._balloon.bgRect[2][2])
                painter.end()

        # debug draw
        if kikka.shell.isDebug is True:
            painter = QPainter(img)
            painter.fillRect(QRect(0, 0, 200, 64), QColor(0, 0, 0, 64))
            painter.setPen(Qt.red)
            for y in range(len(self._balloon.clipH)):
                for x in range(len(self._balloon.clipW)):
                    if x in (0, 2, 4) and y in (0, 2, 4):
                        continue
                    rectf = QRect(drect[y][x])
                    text = "(%d, %d)\n%d x %d" % (rectf.x(), rectf.y(), rectf.width(), rectf.height())
                    painter.drawText(rectf, Qt.AlignCenter, text)
                if y > 0:
                    painter.drawLine(drect[y][0].x(), drect[y][0].y(), drect[y][0].x() + img.width(), drect[y][0].y())

            for x in range(1, len(self._balloon.clipW)):
                painter.drawLine(drect[0][x].x(), drect[0][x].y(), drect[0][x].x(), drect[0][x].y() + img.height())

            painter.setPen(Qt.green)
            painter.drawRect(QRect(0, 0, img.width() - 1, img.height() - 1))
            painter.drawText(3, 12, "DialogWindow")
            painter.drawText(3, 24, "Ghost: %d" % self.ID)
            painter.drawText(3, 36, "Name: %s" % self.name)
            painter.drawText(3, 48, "soul_id: %d" % soul_id)
        return img

    def getMenuStyle(self):
        return self._menustyle

    def onUpdate(self, updatetime):
        isNeedUpdate = False

        for soul in self._souls.values():
            if soul.onUpdate(updatetime) is True:
                isNeedUpdate = True

        return isNeedUpdate

    def repaint(self):
        for soul in self._souls.values():
            soul.repaint()

    def getShellImage(self):
        return self._shell_image

    # event #####################################################################################

    def memoryRead(self, key, default, soul_id=0, table_name=None):
        if table_name is None:
            table_name = str('ghost_' + self.name)
        return kikka.memory.read(table_name, key, default, soul_id)

    def memoryWrite(self, key, value, soul_id=0, table_name=None):
        if table_name is None:
            table_name = str('ghost_' + self.name)
        kikka.memory.write(table_name, key, value, soul_id)

    def emitGhostEvent(self, param):
        self.signal.ghostEvent.emit(param)

    def ghostEvent(self, param):
        pass


