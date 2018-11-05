# coding=utf-8
import os
import logging

import kikka
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
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
        self._balloons = []
        self.balloondir = ''

    def loadBalloon(self, balloonpath):
        balloon = Balloon(balloonpath)
        if balloon.isInitialized is False:
            return

        isExist = False
        for s in self._balloons:
            if balloon.id == s.id and balloon.name == s.name:
                isExist = True
                break

        if not isExist:
            logging.info("scan balloon: %s", balloon.name)
            self._balloons.append(balloon)
        pass

    def loadAllBalloon(self, balloondir):
        self.balloondir = balloondir

        for parent, dirnames, filenames in os.walk(balloondir):
            for dirname in dirnames:
                balloonpath = os.path.join(parent, dirname)
                self.loadBalloon(balloonpath)

        logging.info("balloon count: %d", len(self._balloons))

    def getBalloon(self, index):
        if 0 <= index < len(self._balloons):
            balloon = self._balloons[index]
            balloon.load()
            return balloon
        else:
            logging.error("getBalloon: index NOT in balloon list")
            raise ValueError

    def getBalloonCount(self):
        return len(self._balloons)


class Balloon:
    def __init__(self, balloonpath):
        self.balloonpath = balloonpath  # root path of this shell
        self.name = ''
        self.id = ''
        self.type = ''
        self.author = AuthorInfo()
        self.isInitialized = False
        self.isLoaded = False
        self.pnglist = []

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

            self.bgRect = srect
            self.isLoaded = True
        pass

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
