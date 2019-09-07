# coding=utf-8
import os
import logging
import collections

from PyQt5.QtCore import Qt, QRect, QPoint, QSize

import kikka
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
        self._balloons = {}
        self.balloondir = ''

    def loadBalloon(self, balloondict, balloonpath):
        balloon = Balloon(balloonpath)
        if balloon.isInitialized is False:
            return

        isExist = False
        for name, b in balloondict.items():
            if balloon.name == name and balloon.unicode_name == b.unicode_name:
                isExist = True
                break

        if not isExist:
            logging.info("scan balloon: %s", balloon.unicode_name)
            balloondict[balloon.name] = balloon
        else:
            logging.warning("load fail. balloon exist: %s", balloon.unicode_name)
        pass

    def scanBalloon(self, balloondir):
        self.balloondir = balloondir

        balloondict = {}
        for parent, dirnames, filenames in os.walk(balloondir):
            for dirname in dirnames:
                balloonpath = os.path.join(parent, dirname)
                self.loadBalloon(balloondict, balloonpath)

        balloonordereddict = collections.OrderedDict(sorted(balloondict.items(), key=lambda t: t[0]))
        for name, balloon in balloonordereddict.items():
            self._balloons[name] = balloon

        logging.info("balloon count: %d", len(self._balloons))

    def getBalloon(self, balloonname):
        if balloonname in self._balloons:
            return self._balloons[balloonname]
        else:
            logging.warning("getBalloon: '%s' NOT in balloon list"%balloonname)
            return None
        pass

    def getBalloonByIndex(self, index):
        if 0 <= index < len(self._balloons):
            for balloon in self._balloons.values():
                if index>0:
                    index -= 1
                    continue
                else:
                    return balloon
        else:
            logging.warning("getBalloon: index=%d NOT in balloon list"%index)
            return None
        pass

    def getBalloonCount(self):
        return len(self._balloons)


class Balloon:
    def __init__(self, resource_path):
        self.resource_path = resource_path  # root path of this shell
        self.unicode_name = ''
        self.name = ''
        self.type = ''
        self.author = AuthorInfo()
        self.isInitialized = False
        self.isLoaded = False
        self.pnglist = []

        self.minimumsize = kikka.const.WindowConst.DialogWindowDefaultSize
        self.margin = kikka.const.WindowConst.DialogWindowDefaultMargin
        self.flipBackground = False
        self.noFlipCenter = False
        self.stylesheet = None

        self.init()

    def init(self):
        if not os.path.exists(self.resource_path):
            return
        descript_path = os.path.join(self.resource_path, 'descript.txt')
        if not os.path.exists(descript_path):
            return

        self._load_descript(descript_path)
        if self.name == '':
            self.name = os.path.basename(self.resource_path)

        self.isInitialized = True

    def load(self):
        if self.isLoaded is False:
            logging.info("load balloon: %s", self.unicode_name)
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

    def _load_descript(self, filepath):
        # load descript
        map = {}
        charset = kikka.helper.checkEncoding(filepath)

        f = open(filepath, 'r', encoding=charset)
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
            elif key[0] == 'margin':
                self.margin = [int(value[0]), int(value[1]), int(value[2]), int(value[3])]

            elif key[0] == 'name':
                self.name = value[0]
            elif key[0] == 'unicode_name':
                self.unicode_name = value[0]
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

    def _load_stylesheet(self):
        stylesheet_path = os.path.join(self.resource_path, 'stylesheet.txt')
        if not os.path.exists(stylesheet_path): return

        charset = kikka.helper.checkEncoding(stylesheet_path)
        f = open(stylesheet_path, 'r', encoding=charset)
        self.stylesheet = f.read()
        f.close()

        pass

    def _IgnoreParams(self, key, values):
        print('unknow shell params: %s,%s' % (key, values))
        pass
