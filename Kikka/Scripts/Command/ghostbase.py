# coding=utf-8
import logging
import os

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QRectF
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap

import kikka
from shellwindow import ShellWindow
from dialogwindow import Dialog
from kikka_menu import MenuStyle, Menu


class GhostBase:
    def __init__(self, gid=-1, name=''):
        self.gid = gid if gid != -1 else kikka.core.newGhostID()
        self.name = name
        self.shell = None
        self.balloon = None
        self.eventlist = {}
        self._shellwindows = {}
        self._dialogs = {}
        self._surfaces = {}
        self._surface_base_image = {}
        self._balloon_base_image = None
        self._shell_image = {}
        self._balloon_image = {}
        self._menus = {}
        self._menustyle = None

    def show(self):
        for w in self._shellwindows.values():
            w.show()

    def hide(self):
        for w in self._shellwindows.values():
            w.hide()
        for d in self._dialogs.values():
            d.hide()

    def showMenu(self, nid, pos):
        if 0 <= nid < len(self._menus) and self._menus[nid] is not None:
            self._menus[nid].setPosition(pos)
            self._menus[nid].show()
        pass

    def addWindow(self, nid, surfaceID=0):
        window = ShellWindow(self, nid)
        dialog = Dialog(self, nid)

        self._shellwindows[nid] = window
        self._dialogs[nid] = dialog
        self._surface_base_image[nid] = None
        self._surfaces[nid] = None
        self._menus[nid] = kikka.menu.createSystemMenu(self)

        self.setSurface(nid, surfaceID)
        if self.balloon is not None:
            dialog.setBalloon(self.balloon)
        return window

    def getShellWindow(self, nid):
        if 0 <= nid < len(self._shellwindows):
            return self._shellwindows[nid]
        else:
            return None

    def getDialog(self, nid):
        if 0 <= nid < len(self._dialogs):
            return self._dialogs[nid]
        else:
            return None

    def setShell(self, shellID):
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

        for i in range(len(self._shellwindows)):
            self._shellwindows[i].setImage(self.getShellImage(i))

    def getShell(self):
        return self.shell

    def setBalloon(self, balloonID):
        self.balloon = kikka.balloon.getBalloon(balloonID)

        for parent, dirnames, filenames in os.walk(self.balloon.balloonpath):
            for filename in filenames:
                if filename[len(filename) - 4:] == '.png':
                    p = os.path.join(self.balloon.balloonpath, filename)
                    self._balloon_image[filename] = kikka.helper.getImage(p)
        self._balloon_base_image = self._balloon_image['background.png']

        for i in range(len(self._dialogs)):
            self._dialogs[i].setBalloon(self.balloon)
            self._dialogs[i].repaint()

    def getBalloon(self):
        return self.balloon

    def setMenu(self, nid, Menu):
        if 0 <= nid < len(self._menus):
            self._menus[nid] = Menu

    def getMenu(self, nid=0) -> Menu:
        if 0 <= nid < len(self._menus):
            return self._menus[nid]
        else:
            return None

    # ###################################################################################

    def setSurface(self, nid, surfaceID):
        try:
            if self._surfaces[nid] is not None and self._surfaces[nid].ID == surfaceID:
                return

            surface = self.shell.getSurface(surfaceID)
            if surface is None:
                return

            self._surfaces[nid] = surface
            self._surface_base_image[nid] = self._makeSurfaceBaseImage(surface)

            # start 'runonce' and 'always' animation
            for aid, ani in surface.animations.items():
                if ani.interval in ['runonce', 'always']:
                    ani.start()

            img = self.getShellImage(nid)
            self._shellwindows[nid].setImage(img)
            self._shellwindows[nid].setBoxes(self.shell.getCollisionBoxes(surfaceID), self.shell.getOffset())
        except ValueError:
            logging.warning("Gohst.setSurfaces: surfaceID: %d NOT exist" % surfaceID)
        pass

    def _makeSurfaceBaseImage(self, surface):
        base_image = QImage(500, 500, QImage.Format_ARGB32)
        painter = QPainter(base_image)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(base_image.rect(), Qt.transparent)

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        if len(surface.elements) > 0:
            for i, ele in surface.elements.items():
                fn = ele.filename
                if fn in self._shell_image:
                    painter.drawImage(self.shell.setting.offset + ele.offset, self._shell_image[fn])
        else:
            fn = "surface%04d.png" % surface.ID
            if fn in self._shell_image:
                painter.drawImage(self.shell.setting.offset, self._shell_image[fn])
        painter.end()
        # self._base_image.save("_base_image.png")
        return base_image

    def getShellImage(self, nid):
        img = QImage(self._surface_base_image[nid])
        painter = QPainter(img)

        # draw surface and animations
        surface = self._surfaces[nid]
        for aid, ani in surface.animations.items():
            fid, x, y = ani.getCurSurfaceData()
            # logging.info("aid=%d pid=%d faceid=%d xy=(%d, %d)" % (aid, ani.curPattern, fid, x, y))
            if fid == -1: continue

            image_name = "surface%04d.png" % fid
            if image_name in self._shell_image:
                face = self._shell_image[image_name]
                painter.drawImage(self.shell.setting.offset + QPoint(x, y), face)

        # debug draw
        if kikka.shell.isDebug is True:
            painter.fillRect(QRect(0, 0, 200, 64), QColor(0, 0, 0, 64))
            painter.setPen(Qt.green)
            painter.drawRect(QRect(0, 0, img.width() - 1, img.height() - 1))
            painter.drawText(3, 12, "MainWindow")
            painter.drawText(3, 24, "Ghost: %d" % self.gid)
            painter.drawText(3, 36, "Name: %s" % self.name)
            painter.drawText(3, 48, "nid: %d" % nid)

            for cid, col in surface.CollisionBoxes.items():
                painter.setPen(Qt.red)
                rect = QRect(col.Point1, col.Point2)
                rect.moveTopLeft(col.Point1 + self.shell.setting.offset)
                painter.drawRect(rect)
                painter.fillRect(rect, QColor(255, 255, 255, 64))
                painter.setPen(Qt.black)
                painter.drawText(rect, Qt.AlignCenter, col.tag)

        return img

    def getBalloonImage(self, size: QSize, flip=False, nid=-1):
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
        pixmap = QPixmap().fromImage(self._balloon_base_image, Qt.AutoColor)
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
            painter.drawText(3, 48, "nid: %d" % nid)
        return img

    def getMenuStyle(self):
        return self._menustyle

    def update(self, updatetime):
        isNeedUpdate = False

        for nid, w in self._shellwindows.items():
            for aid, ani in self._surfaces[nid].animations.items():
                if ani.update(updatetime) is True:
                    w.setImage(self.getShellImage(nid))
                    isNeedUpdate = True

        return isNeedUpdate

    def repaint(self):
        for w in self._shellwindows.values():
            w.setImage(self.getShellImage(w.nid))
            w.repaint()
        for d in self._dialogs.values():
            d.repaint()

    # #####################################################################################

    def memoryRead(self, key, default, nid=0):
        key = '%s_%d_%d' % (key, self.gid, nid)
        if kikka.core.isDebug:
            value = kikka.memory.read(key, default)
        else:
            value = kikka.memory.readDeepMemory(key, default)
        return value

    def menoryWrite(self, key, value, nid=0):
        key = '%s_%d_%d' % (key, self.gid, nid)
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
