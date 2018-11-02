# coding=utf-8
import logging
import os

from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QImage, QPainter, QColor

import kikka
from mainwindow import MainWindow
from dialogwindow import Dialog


class Gohst:
    def __init__(self, gid, shellID, balloonID):
        self.gid = gid
        self.shell = None
        self.balloon = None
        self.mainwindows = []
        self.dialogs = []
        self.surfaces = []
        self.surface_base_image = []
        self._pngs = {}

        self.setShell(shellID)
        self.setBalloon(balloonID)
        self.addWindow(kikka.KIKKA)
        # self.addWindow(kikka.TOWA)

    def show(self):
        for w in self.mainwindows:
            w.show()
        for d in self.dialogs:
            d.show()

    def addWindow(self, nid):
        window = MainWindow(self, nid)
        dialog = Dialog(self, nid)

        self.mainwindows.append(window)
        self.dialogs.append(dialog)
        self.surface_base_image.append(None)
        self.surfaces.append(None)

        self.setSurface(nid, 0)

    def setShell(self, shellID):
        self.shell = kikka.shell.getShell(shellID)

        self._pngs = {}
        for filename, _ in self.shell.pngs.items():
            p = os.path.join(self.shell.shellpath, filename)
            if p == self.shell.shellmenustyle.background_image \
                    or p == self.shell.shellmenustyle.foreground_image \
                    or p == self.shell.shellmenustyle.sidebar_image:
                continue
            self._pngs[filename] = QImage(p)

    def setBalloon(self, balloonID):
        self.balloon = kikka.balloon.getBalloon(balloonID)

    def getMainWindow(self, nid):
        if 0 <= nid < len(self.mainwindows):
            return self.mainwindows[nid]
        else:
            return None

    def getDialog(self, nid):
        if 0 <= nid < len(self.dialogs):
            return self.dialogs[nid]
        else:
            return None

    def getShell(self):
        return self.shell

    def getBalloon(self):
        return self.balloon

    def setSurface(self, nid, surfaceID):
        try:
            if self.surfaces[nid] is not None and self.surfaces[nid].ID == surfaceID:
                return

            surface = self.shell.getSurface(surfaceID)
            if surface is None:
                return

            self.surfaces[nid] = surface
            # self._CurfaceID = surfaceID
            # surface = self.surfaces[surfaceID]

            # make base image
            self.surface_base_image[nid] = self._makeSurfaceBaseImage(surface)

            # start 'runonce' and 'always' animation
            for aid, ani in surface.animations.items():
                if ani.interval in ['runonce', 'always']:
                    ani.start()
        except ValueError:
            logging.warning("Gohst.setSurfaces: surfaceID: %d NOT exist" % surfaceID)
        finally:
            # self.repiant()
            pass

        img = self._getShellImage(nid)
        self.mainwindows[nid].setImage(img)
        # shell = kikka.shell.getCurShell()
        self.mainwindows[nid].setBoxes(self.shell.getCollisionBoxes(surfaceID), self.shell.getOffset())

    def update(self, updatetime):
        isNeedUpdate = False
        for surface in self.surfaces:
            for aid, ani in surface.animations.items():
                if ani.update(updatetime) is True:
                    id = surface.ID
                    self.mainwindows[id].setImage(self._getShellImage(id))
                    isNeedUpdate = True

        return isNeedUpdate

    def repiant(self):
        for s in self.surfaces:
            id = s.ID
            self.mainwindows[id].setImage(self._getShellImage(id))

    def _makeSurfaceBaseImage(self, surface):
        base_image = QImage(500, 500, QImage.Format_ARGB32)
        painter = QPainter(base_image)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(base_image.rect(), Qt.transparent)

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        if len(surface.elements) > 0:
            for i, ele in surface.elements.items():
                fn = ele.filename
                if fn in self._pngs:
                    painter.drawImage(self.shell.setting.offset + ele.offset, self._pngs[fn])
        else:
            fn = "surface%04d.png" % surface.ID
            if fn in self._pngs:
                painter.drawImage(self.shell.setting.offset, self._pngs[fn])
        painter.end()
        # self._base_image.save("_base_image.png")
        return base_image

    def _getShellImage(self, nid):
        img = QImage(self.surface_base_image[nid])

        painter = QPainter(img)

        surface = self.surfaces[nid]
        for aid, ani in surface.animations.items():
            fid, x, y = ani.getCurSurfaceData()
            # logging.info("aid=%d pid=%d faceid=%d xy=(%d, %d)" % (aid, ani.curPattern, fid, x, y))
            if fid == -1: continue

            image_name = "surface%04d.png" % fid
            face = self._pngs[image_name]
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

