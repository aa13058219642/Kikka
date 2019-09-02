# coding=utf-8
import logging
import os
import time
import random
from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QRectF
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap
from PyQt5.QtWidgets import QActionGroup

import kikka
from shellwindow import ShellWindow
from dialogwindow import Dialog
from kikka_menu import MenuStyle, Menu
from soul import Soul

class GhostBase:
    def __init__(self, gid=-1, name=''):
        self.gid = gid if gid != -1 else kikka.core.newGhostID()
        self.name = name
        self.shell = None
        self.balloon = None

        self._souls = {}
        self._shell_image = {}
        self._balloon_image = {}


        self.eventlist = {}
        self.animation_list = {}

        self._shellwindows = {}
        self._dialogs = {}
        self._surfaces = {}
        self._surface_base_image = {}
        self._surface_image = {}
        self._balloon_image_cache = None
        self._menus = {}
        self._menustyle = None
        self._clothes = {}

        self.setShell(self.memoryRead('CurrentShellID', 0))
        self.setBalloon(self.memoryRead('CurrentBalloonID', 0))

    def show(self):
        for soul in self._souls.values():
            soul.show()

    def hide(self):
        for soul in self._souls.values():
            soul.hide()

    def showMenu(self, winid, pos):
        if winid in self._souls.keys():
            self._souls[winid].showMenu(pos)
        pass

    def addWindow(self, winid, surfaceID=0):
        self._souls[winid] = Soul(self, winid, surfaceID)

        return self._souls[winid].getShellWindow()

    def getShellWindow(self, winid):
        if winid in self._souls.keys():
            return self._souls[winid].getShellWindow()
        else:
            return None

    def getDialog(self, winid):
        if winid in self._souls.keys():
            return self._souls[winid].getDialog()
        else:
            return None

    def changeShell(self, shellID):
        self.hide()
        self.setShell(shellID)
        self.show()

    def setShell(self, shellID):
        if self.shell is not None and self.shell.id == shellID:
            return

        self.shell = kikka.shell.getShell(shellID)
        self.shell.load()
        self._menustyle = MenuStyle(self.shell.shellmenustyle)

        self._shell_image = {}
        for filename in self.shell.pnglist:
            p = os.path.join(self.shell.shellpath, filename)
            if p == self.shell.shellmenustyle.background_image \
                    or p == self.shell.shellmenustyle.foreground_image \
                    or p == self.shell.shellmenustyle.sidebar_image:
                continue
            self._shell_image[filename] = kikka.helper.getImage(p)

        for sid in self._souls.keys():
            self.setSurface(sid)
            self.updateClothesMenu(sid)
        self.memoryWrite('CurrentShellID', shellID)

    def getShell(self):
        return self.shell

    def setBalloon(self, balloowinid):
        self.balloon = kikka.balloon.getBalloon(balloowinid)
        self.balloon.load()

        for parent, dirnames, filenames in os.walk(self.balloon.balloonpath):
            for filename in filenames:
                if filename[len(filename) - 4:] == '.png':
                    p = os.path.join(self.balloon.balloonpath, filename)
                    self._balloon_image[filename] = kikka.helper.getImage(p)
        self._balloon_image_cache = self._balloon_image['background.png']

        for soul in self._souls.values():
            soul.setBalloon(self.balloon)

        # for i in range(len(self._dialogs)):
        #     self._dialogs[i].setBalloon(self.balloon)
        #     self._dialogs[i].repaint()
        self.memoryWrite('CurrentBalloonID', balloowinid)


    def getBalloon(self):
        return self.balloon

    def setMenu(self, winid, menu):
        if winid in self._souls.keys():
            self._souls[winid].setMenu(menu)

    def getMenu(self, winid=0) :
        if winid in self._souls.keys():
            return self._souls[winid].getMenu()
        else:
            return None

    # ###################################################################################

    def setSurface(self, winid, surfaceID=-1):
        if winid in self._souls.keys():
            self._souls[winid].setSurface(surfaceID)

    def getBalloonImage(self, size: QSize, flip=False, winid=-1):
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
                pass
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
            painter.drawText(3, 24, "Ghost: %d" % self.gid)
            painter.drawText(3, 36, "Name: %s" % self.name)
            painter.drawText(3, 48, "winid: %d" % winid)
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

    def memoryRead(self, key, default, winid=0):
        key = '%s_%d_%d' % (key, self.gid, winid)
        if kikka.core.isDebug:
            value = kikka.memory.read(key, default)
        else:
            value = kikka.memory.readDeepMemory(key, default)
        return value

    def memoryWrite(self, key, value, winid=0):
        key = '%s_%d_%d' % (key, self.gid, winid)
        if kikka.core.isDebug:
            kikka.memory.write(key, value)
        else:
            kikka.memory.writeDeepMemory(key, value)
        pass

    def event_selector(self, event, tag, **kwargs):
        if 'gid' not in kwargs: kwargs['gid'] = self.gid

        e = self.getEventList()
        if event in e and tag in e[event]:
            e[event][tag](**kwargs)

    def getEventList(self):
        return self.eventlist

    def updateClothesMenu(self, winid):
        if winid in self._souls.keys():
            self._souls[winid].updateClothesMenu()

