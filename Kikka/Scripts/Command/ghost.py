# coding=utf-8
import logging
import os

from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap

import kikka
from mainwindow import MainWindow
from dialogwindow import Dialog
from kikka_menu import MenuStyle
import mainmenu


class Gohst:
    def __init__(self, gid, shellID, balloonID):
        self.gid = gid
        self.shell = None
        self.balloon = None
        self._mainwindows = []
        self._dialogs = []
        self._surfaces = []
        self._surface_base_image = []
        self._balloon_base_image = None
        self._shell_image = {}
        self._balloon_image = {}
        self._menus = []
        self._menustyle = None

        self.setShell(shellID)
        self.setBalloon(balloonID)
        self.addWindow(kikka.KIKKA, 0)
        self.addWindow(kikka.TOWA, 10)

    def show(self):
        for w in self._mainwindows:
            w.show()

    def hide(self):
        for w in self._mainwindows:
            w.hide()
        for d in self._dialogs:
            d.hide()

    def showMenu(self, nid, pos):
        if 0 <= nid < len(self._menus) and self._menus[nid] is not None:
            self._menus[nid].setPosition(pos)
            self._menus[nid].show()
        pass

    def addWindow(self, nid, surfaceID):
        window = MainWindow(self, nid)
        dialog = Dialog(self, nid)

        self._mainwindows.append(window)
        self._dialogs.append(dialog)
        self._surface_base_image.append(None)
        self._surfaces.append(None)
        self._menus.append(kikka.menu.createKikkaMenu(self))

        self.setSurface(nid, surfaceID)

    def getMainWindow(self, nid):
        if 0 <= nid < len(self._mainwindows):
            return self._mainwindows[nid]
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

        for i in range(len(self._mainwindows)):
            self._mainwindows[i].setImage(self.getShellImage(i))

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
            self._dialogs[i].repaint()

    def getBalloon(self):
        return self.balloon

    def setMenu(self, nid, Menu):
        if 0 <= nid < len(self._menus):
            self._menus[nid] = Menu

    def getMenu(self, nid):
        if 0 <= nid < len(self._menus):
            return self._menus[nid]
        else:
            return None

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
            self._mainwindows[nid].setImage(img)
            self._mainwindows[nid].setBoxes(self.shell.getCollisionBoxes(surfaceID), self.shell.getOffset())
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

        surface = self._surfaces[nid]
        for aid, ani in surface.animations.items():
            fid, x, y = ani.getCurSurfaceData()
            # logging.info("aid=%d pid=%d faceid=%d xy=(%d, %d)" % (aid, ani.curPattern, fid, x, y))
            if fid == -1: continue

            image_name = "surface%04d.png" % fid
            if image_name in self._shell_image:
                face = self._shell_image[image_name]
                painter.drawImage(self.shell.setting.offset + QPoint(x, y), face)

        # logging.info("--getCurImage end--------")
        if kikka.shell.isDebug is True:
            # logging.info("debug draw")
            for cid, col in surface.CollisionBoxes.items():
                painter.setPen(Qt.red)
                rect = QRect(col.Point1, col.Point2)
                rect.moveTopLeft(col.Point1 + self.shell.setting.offset)
                painter.drawRect(rect)
                painter.fillRect(rect, QColor(255, 255, 255, 64))
                painter.setPen(Qt.black)
                painter.drawText(rect, Qt.AlignCenter, col.tag)

            painter.setPen(Qt.red)
            painter.drawRect(QRect(0, 0, img.width() - 1, img.height() - 1))
        return img

    def getBalloonImage(self, size: QSize, flip=False):
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
        p = QPainter(img)
        p.setCompositionMode(QPainter.CompositionMode_Source)

        for y in range(len(self.balloon.clipH)):
            for x in range(len(self.balloon.clipW)):
                p.drawPixmap(drect[y][x], pixmap, self.balloon.bgRect[y][x])
        p.end()

        # flip or not
        if self.balloon.flipBackground is True and flip is True:
            img = img.mirrored(True, False)
            if self.balloon.noFlipCenter is True and len(self.balloon.clipW) == 5 and len(self.balloon.clipH) == 5:
                p = QPainter(img)
                p.setCompositionMode(QPainter.CompositionMode_Source)
                p.drawPixmap(drect[2][2], pixmap, self.balloon.bgRect[2][2])
                p.end()

        return img

    def getMenuStyle(self):
        return self._menustyle

    def update(self, updatetime):
        isNeedUpdate = False

        for i in range(len(self._mainwindows)):
            for aid, ani in self._surfaces[i].animations.items():
                if ani.update(updatetime) is True:
                    self._mainwindows[i].setImage(self.getShellImage(i))
                    isNeedUpdate = True
        return isNeedUpdate

    def memoryRead(self, key, default, nid=0):
        key = '%s_%d_%d' % (key, self.gid, nid)
        return kikka.memory.readDeepMemory(key, default)

    def menoryWrite(self, key, value, nid=0):
        key = '%s_%d_%d' % (key, self.gid, nid)
        kikka.memory.writeDeepMemory(key, value)
        pass
