# coding=utf-8
import os
import re
import logging
import random
import time
from enum import Enum

import kikka
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QImage, QPixmap, QPainter
from kikka_shell import AuthorInfo


class KikkaBalloon:
    _instance = None
    isDebug = True

    def __init__(self, **kwargs):
        raise SyntaxError('The class is Singletion, please use KikkaBalloon.this() or kikka.balloon')

    @staticmethod
    def this():
        if KikkaBalloon._instance is None:
            KikkaBalloon._instance = object.__new__(KikkaBalloon)
            KikkaBalloon._instance._init()
        return KikkaBalloon._instance

    def _init(self):
        self.balloons = []
        self.isNeedUpdate = True
        self.shelldir = ''
        self.currentBalloonIndex = -1

    def loadBalloon(self, balloonpath):
        balloon = Balloon(balloonpath)
        if balloon.isInitialized is False:
            return

        isExist = False
        for s in self.balloons:
            if balloon.id == s.id and balloon.name == s.name:
                isExist = True
                break

        if not isExist:
            logging.info("scan balloon: %s", balloon.name)
            self.balloons.append(balloon)
        pass

    def loadAllBalloon(self, balloondir):
        self.balloondir = balloondir

        for parent, dirnames, filenames in os.walk(balloondir):
            for dirname in dirnames:
                balloonpath = os.path.join(parent, dirname)
                self.loadBalloon(balloonpath)

        logging.info("balloon count: %d", len(self.balloons))
        self.setCurrentBalloon(kikka.memory.readDeepMemory('CurrentBalloon', 1))

    def getCurrentBalloon(self):

        return self.balloons[self.currentBalloonIndex] if self.currentBalloonIndex != -1 else None

    def setCurrentBalloon(self, index):
        if self.currentBalloonIndex != index and 0 <= index < len(self.balloons):
            balloon = self.getCurrentBalloon()
            if balloon is not None: balloon.clear()

            self.currentBalloonIndex = index
            balloon = self.getCurrentBalloon()
            balloon.load()
            # kikka.menu.setMenuStyle(balloon.getShellMenuStyle())
            kikka.memory.writeDeepMemory('CurrentBalloon', index)

            logging.info("change balloon to %s" % self.balloons[index].name)
        else:
            logging.warning("setCurrentBalloon: index NOT in balloons list")

    def getCurrentBalloonImage(self, size: QSize):
        balloon = self.getCurrentBalloon()
        if balloon is not None:
            return balloon.getBalloonImage(size)
        else:
            return None

    def getBalloon(self, index):
        if 0 <= self.currentBalloonIndex < len(self.balloons):
            balloon = self.balloons[self.currentBalloonIndex]
            balloon.load()
            return balloon
        else:
            return None


class Balloon:
    def __init__(self, balloonpath):
        self.balloonpath = balloonpath  # root path of this shell
        self.name = ''
        self.id = ''
        self.type = ''
        self.author = AuthorInfo()
        self.isInitialized = False
        self.isLoaded = False
        self._pngs = {}

        self.clipW = []
        self.clipH = []
        self._bgSource = None
        self._bgImage = None
        self._bgPixmap = None
        self._bgMask = None
        self._bgRect = None

        self.minimumsize = QSize(200, 200)
        self.flipBackground = False
        self.noFlipCenter = False
        self.stylesheet = None

        self._load_descript()
        pass

    def load(self):
        if self.isLoaded is False:
            logging.info("load balloon: %s", self.name)
            self._load_stylesheet()

            # load PNG
            for parent, dirnames, filenames in os.walk(self.balloonpath):
                for filename in filenames:
                    if filename[len(filename) - 4:] == '.png':
                        p = os.path.join(self.balloonpath, filename)
                        self._pngs[filename] = kikka.helper.getImage(p)
            self._bgSource = self._pngs['background.png']

            # load rect
            srect = []
            sw = self.clipW
            sh = self.clipH
            for y in range(len(self.clipH)):
                sr = []
                for x in range(len(self.clipW)):
                    pt = QPoint(0, 0)
                    if x > 0: pt.setX(sr[x - 1].x() + sw[x - 1])
                    if y > 0: pt.setY(srect[y - 1][0].y() + sh[y - 1])
                    sz = QSize(sw[x], sh[y])
                    sr.append(QRect(pt, sz))
                    pass
                srect.append(sr)
            pass  # exit for

            self._bgRect = srect
            self.isLoaded = True
        pass

    def clear(self):
        self._pngs = {}
        self.isLoaded = False
        pass

    # def _loadPNGindex(self):
    #     for parent, dirnames, filenames in os.walk(self.balloonpath):
    #         for filename in filenames:
    #             if filename[len(filename) - 4:] == '.png':
    #                 self._pngs[filename] = None
    #     pass

    def _load_descript(self):
        # load descript
        map = {}
        descript_path = os.path.join(self.balloonpath, 'descript.txt')
        if not os.path.exists(descript_path): return
        charset = kikka.helper.checkEncoding(descript_path)

        f = open(descript_path, 'r', encoding=charset)
        for line in f:
            line = line.replace("\n", "").replace("\r", "")
            line = line.strip(' ')

            if line == '': continue
            if line.find('\\') == 0: continue
            if line.find('//') == 0: continue
            if line.find('#') == 0: continue

            index = line.index(',')

            key = line[0:index]
            value = line[index + 1:]

            map[key] = value
        pass  # exit for

        # load key from descript.txt
        for keys, values in map.items():
            key = keys.split('.')
            value = values.split(',')

            if key[0] == 'clip':
                if key[1] == 'width':
                    l = int(value[0])
                    if l == 3 and len(value) == 4:
                        self.clipW = [int(value[1]), int(value[2]), int(value[3])]
                    elif l == 5 and len(value) == 6:
                        self.clipW = [int(value[1]), int(value[2]), int(value[3]), int(value[4]), int(value[5])]
                elif key[1] == 'height':
                    l = int(value[0])
                    if l == 3 and len(value) == 4:
                        self.clipH = [int(value[1]), int(value[2]), int(value[3])]
                    elif l == 5 and len(value) == 6:
                        self.clipH = [int(value[1]), int(value[2]), int(value[3]), int(value[4]), int(value[5])]
                else:
                    self._IgnoreParams(keys, values)

            elif key[0] == 'minimumsize':
                self.minimumsize = QSize(int(value[0]), int(value[1]))
            elif key[0] == 'flipbackground':
                self.flipBackground = int(value[0]) == 1
            elif key[0] == 'noflipcenter':
                self.noFlipCenter = int(value[0]) == 1

            elif key[0] == 'id':
                self.id = value[0]
            elif key[0] == 'name':
                self.name = value[0]
            elif key[0] == 'type':
                self.type = value[0]
            elif key[0] == 'craftman' or key[0] == 'craftmanw':
                self.author.name = value[0]
            elif key[0] == 'crafmanurl':
                self.author.webside = value[0]
            elif key[0] == 'homeurl':
                self.author.updateurl = value[0]
            elif key[0] == 'readme':
                self.author.readme = value[0]

            # skip params
            elif key[0] == 'charset':
                # self._IgnoreParams(keys, values)
                pass

            # unknow params
            else:
                self._IgnoreParams(keys, values)
        pass  # exit for
        self.isInitialized = True

    def _load_stylesheet(self):
        stylesheet_path = os.path.join(self.balloonpath, 'stylesheet.txt')
        if not os.path.exists(stylesheet_path): return

        charset = kikka.helper.checkEncoding(stylesheet_path)
        f = open(stylesheet_path, 'r', encoding=charset)
        self.stylesheet = f.read()
        f.close()

        pass

    def _IgnoreParams(self, key, values):
        print('unknow shell params: %s,%s' % (key, values))
        pass

    def getBalloonImage(self, size: QSize, flip=False):
        if self.isLoaded is False:
            self.load()

        drect = []
        # calculate destination rect
        if len(self.clipW) == 3:
            dw = [self.clipW[0],
                  size.width() - self.clipW[0] - self.clipW[2],
                  self.clipW[2]]
        elif len(self.clipW) == 5:
            sw = size.width() - self.clipW[0] - self.clipW[2] - self.clipW[4]
            dw = [self.clipW[0],
                  sw // 2,
                  self.clipW[2],
                  sw - sw // 2,
                  self.clipW[4]]
        else:
            sw = size.width() // 3
            dw = [sw, size.width() - sw*2, sw]

        if len(self.clipH) == 3:
            dh = [self.clipH[0],
                  size.height() - self.clipH[0] - self.clipH[2],
                  self.clipH[2]]
        elif len(self.clipH) == 5:
            sh = size.height() - self.clipH[0] - self.clipH[2] - self.clipH[4]
            dh = [self.clipH[0],
                  sh // 2,
                  self.clipH[2],
                  sh - sh // 2,
                  self.clipH[4]]
        else:
            sh = size.height() // 3
            dh = [sh, size.height() - sh*2, sh]

        for y in range(len(self.clipH)):
            dr = []
            for x in range(len(self.clipW)):
                pt = QPoint(0, 0)
                if x > 0: pt.setX(dr[x-1].x() + dw[x-1])
                if y > 0: pt.setY(drect[y-1][0].y() + dh[y-1])
                sz = QSize(dw[x], dh[y])
                dr.append(QRect(pt, sz))
                pass
            drect.append(dr)
        pass  # exit for

        # paint balloon image
        self._bgImage = QImage(size, QImage.Format_ARGB32)
        pixmap = QPixmap().fromImage(self._bgSource, Qt.AutoColor)
        p = QPainter(self._bgImage)
        p.setCompositionMode(QPainter.CompositionMode_Source)

        for y in range(len(self.clipH)):
            for x in range(len(self.clipW)):
                p.drawPixmap(drect[y][x], pixmap, self._bgRect[y][x])
        p.end()

        # flip or not
        if self.flipBackground is True and flip is True:
            self._bgImage = self._bgImage.mirrored(True, False)
            if self.noFlipCenter is True and len(self.clipW) == 5 and len(self.clipH) == 5:
                p = QPainter(self._bgImage)
                p.setCompositionMode(QPainter.CompositionMode_Source)
                p.drawPixmap(drect[2][2], pixmap, self._bgRect[2][2])
                p.end()

        self._bgPixmap = QPixmap().fromImage(self._bgImage, Qt.AutoColor)
        self._bgMask = self._bgPixmap.mask()
        return self._bgPixmap, self._bgMask
        pass
