# coding=utf-8
import logging
import os
import time
import random

from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap

import kikka
from kikka_menu import MenuStyle
from soul import Soul
from ghostevent import GhostEvent


class KikkaGhostSignal(QObject):
    ghostEvent = pyqtSignal(GhostEvent, str, dict)


class GhostBase:

    def __init__(self, ghost_id=-1, name=''):
        self.ID = ghost_id if ghost_id != -1 else kikka.core.newGhostID()
        self.name = name
        self.shell = None
        self.balloon = None
        self.signal = KikkaGhostSignal()

        self._souls = OrderedDict()
        self._shell_image = {}
        self._balloon_image = {}

        self._eventlist = {}
        self.animation_list = {}

        self._balloon_image_cache = None
        self._menustyle = None
        self._isLockOnTaskbar = True

        self.init()

    def init(self):
        kikka.memory.createTable(str('ghost_' + self.name))
        self.loadClothBind()
        self.setShell(self.memoryRead('CurrentShellName', ''))
        self.setBalloon(self.memoryRead('CurrentBalloonName', ''))
        self.setIsLockOnTaskbar(self.memoryRead('isLockOnTaskbar', True))
        self.signal.ghostEvent.connect(self.ghostEvent)

    def show(self):
        for soul in reversed(self._souls.values()):
            soul.show()

    def hide(self):
        for soul in self._souls.values():
            soul.hide()

    def showMenu(self, soul_id, pos):
        if soul_id in self._souls.keys():
            self._souls[soul_id].showMenu(pos)
        pass

    def addWindow(self, soul_id, surface_id=0):
        self._souls[soul_id] = Soul(self, soul_id, surface_id)
        return self._souls[soul_id].getShellWindow()

    def getShellWindow(self, soul_id):
        if soul_id in self._souls.keys():
            return self._souls[soul_id].getShellWindow()
        else:
            return None

    def getDialog(self, soul_id):
        if soul_id in self._souls.keys():
            return self._souls[soul_id].getDialog()
        else:
            return None

    def changeShell(self, shellname):
        self.hide()
        self.setShell(shellname)
        self.show()

    def reloadShell(self, shellname=None):
        if shellname==None:
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

        for sid in self._souls.keys():
            self.setSurface(sid)
            self.updateClothesMenu(sid)

    def setShell(self, shellname):
        if self.shell is not None and self.shell.name == shellname:
            return
        self.reloadShell(shellname)
        self.memoryWrite('CurrentShellName', self.shell.name)

    def getShell(self):
        return self.shell

    def setBalloon(self, name):
        self.balloon = kikka.balloon.getBalloon(name)
        if self.balloon is None:
            self.balloon = kikka.balloon.getBalloonByIndex(0)
            if self.balloon is None:
                raise ValueError("setBalloon: load defalut balloon fail.")

        self.balloon.load()

        for parent, dirnames, filenames in os.walk(self.balloon.resource_path):
            for filename in filenames:
                if filename[len(filename) - 4:] == '.png':
                    p = os.path.join(self.balloon.resource_path, filename)
                    self._balloon_image[filename] = kikka.helper.getImage(p)
        self._balloon_image_cache = self._balloon_image['background.png']

        for soul in self._souls.values():
            soul.setBalloon(self.balloon)

        self.memoryWrite('CurrentBalloonName', self.balloon.name)

    def getBalloon(self):
        return self.balloon

    def setMenu(self, soul_id, menu):
        if soul_id in self._souls.keys():
            self._souls[soul_id].setMenu(menu)

    def getMenu(self, soul_id=0) :
        if soul_id in self._souls.keys():
            return self._souls[soul_id].getMenu()
        else:
            return None

    def saveClothBind(self):
        data = {}
        count = kikka.shell.getShellCount()
        for i in range(count):
            shell = kikka.shell.getShellByIndex(i)
            data[shell.name] = shell.bind
        self.memoryWrite('ClothBind', data)

    def loadClothBind(self):
        data = self.memoryRead('ClothBind', {})
        if len(data)<=0:
            return

        for name in data.keys():
            shell = kikka.shell.getShell(name)
            if shell is None:
                continue
            shell.bind = data[name]

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

    # ###################################################################################

    def setSurface(self, soul_id, surface_id=-1):
        if soul_id in self._souls.keys():
            self._souls[soul_id].setSurface(surface_id)

    def getBalloonImage(self, size: QSize, flip=False, soul_id=-1):
        if self.balloon is None:
            logging.warning("getBalloonImage: balloon is None")
            return kikka.helper.getDefaultImage()

        drect = []
        # calculate destination rect
        if len(self.balloon.clipW) == 3:
            dw = [self.balloon.clipW[0],
                  size.width() - self.balloon.clipW[0] - self.balloon.clipW[2],
                  self.balloon.clipW[2]]
        elif len(self.balloon.clipW) == 5:
            sw = size.width() - self.balloon.clipW[0] - self.balloon.clipW[2] - self.balloon.clipW[4]
            dw = [self.balloon.clipW[0],
                  sw // 2,
                  self.balloon.clipW[2],
                  sw - sw // 2,
                  self.balloon.clipW[4]]
        else:
            sw = size.width() // 3
            dw = [sw, size.width() - sw*2, sw]

        if len(self.balloon.clipH) == 3:
            dh = [self.balloon.clipH[0],
                  size.height() - self.balloon.clipH[0] - self.balloon.clipH[2],
                  self.balloon.clipH[2]]
        elif len(self.balloon.clipH) == 5:
            sh = size.height() - self.balloon.clipH[0] - self.balloon.clipH[2] - self.balloon.clipH[4]
            dh = [self.balloon.clipH[0],
                  sh // 2,
                  self.balloon.clipH[2],
                  sh - sh // 2,
                  self.balloon.clipH[4]]
        else:
            sh = size.height() // 3
            dh = [sh, size.height() - sh*2, sh]

        for y in range(len(self.balloon.clipH)):
            dr = []
            for x in range(len(self.balloon.clipW)):
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

        for y in range(len(self.balloon.clipH)):
            for x in range(len(self.balloon.clipW)):
                painter.drawPixmap(drect[y][x], pixmap, self.balloon.bgRect[y][x])
        painter.end()

        # flip or not
        if self.balloon.flipBackground is True and flip is True:
            img = img.mirrored(True, False)
            if self.balloon.noFlipCenter is True and len(self.balloon.clipW) == 5 and len(self.balloon.clipH) == 5:
                painter = QPainter(img)
                painter.setCompositionMode(QPainter.CompositionMode_Source)
                painter.drawPixmap(drect[2][2], pixmap, self.balloon.bgRect[2][2])
                painter.end()

        # debug draw
        if kikka.shell.isDebug is True:
            painter = QPainter(img)
            painter.fillRect(QRect(0, 0, 200, 64), QColor(0, 0, 0, 64))
            painter.setPen(Qt.red)
            for y in range(len(self.balloon.clipH)):
                for x in range(len(self.balloon.clipW)):
                    if x in (0, 2, 4) and y in (0, 2, 4):
                        continue
                    rectf = QRect(drect[y][x])
                    text = "(%d, %d)\n%d x %d" % (rectf.x(), rectf.y(), rectf.width(), rectf.height())
                    painter.drawText(rectf, Qt.AlignCenter, text)
                if y > 0:
                    painter.drawLine(drect[y][0].x(), drect[y][0].y(), drect[y][0].x() + img.width(), drect[y][0].y())

            for x in range(1, len(self.balloon.clipW)):
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

    def update(self, updatetime):
        isNeedUpdate = False

        for soul in self._souls.values():
            if soul.update(updatetime) is True:
                isNeedUpdate = True

        return isNeedUpdate

    def repaint(self):
        for soul in self._souls.values():
            soul.repaint()

    def getShellImage(self):
        return self._shell_image

    # #####################################################################################

    def memoryRead(self, key, default, soul_id=0, table_name=None):
        if table_name is None:
            table_name = str('ghost_' + self.name)
        return kikka.memory.read(table_name, key, default, soul_id)

    def memoryWrite(self, key, value, soul_id=0, table_name=None):
        if table_name is None:
            table_name = str('ghost_' + self.name)
        kikka.memory.write(table_name, key, value, soul_id)

    def updateClothesMenu(self, soul_id):
        if soul_id in self._souls.keys():
            self._souls[soul_id].updateClothesMenu()

    def bindGhostEvent(self, eventType, tag, callbackFunc):
        if eventType not in self._eventlist.keys():
            self._eventlist[eventType] = {}

        if tag not in self._eventlist[eventType].keys():
            self._eventlist[eventType][tag] = []

        self._eventlist[eventType][tag].append(callbackFunc)

    def removeGhostEvent(self, eventType, tag=None, callbackFunc=None):
        if eventType not in self._eventlist.keys():
            return

        if tag is None:
            self._eventlist[eventType].clear()
            return

        if tag in self._eventlist[eventType].keys():
            if callbackFunc is None:
                self._eventlist[eventType][tag].clear()
            else:
                self._eventlist[eventType][tag].remove(callbackFunc)
        pass

    def emitGhostEvent(self, eventType, tag, param=None):
        argv = param if param is not None else {}
        if 'GhostID' not in argv.keys():
            argv['GhostID'] = self.ID
        self.signal.ghostEvent.emit(eventType, tag, argv)

    def ghostEvent(self, eventType, tag, argv=None):
        if eventType in self._eventlist.keys() \
        and tag in self._eventlist[eventType].keys() \
        and len(self._eventlist[eventType][tag])>0:
            for eventFunc in self._eventlist[eventType][tag]:
                eventFunc(argv)
        pass