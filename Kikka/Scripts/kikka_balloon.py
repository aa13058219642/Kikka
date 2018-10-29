# coding=utf-8
import os
import re
import logging
import random
import time
from enum import Enum

import kikka
from PyQt5.QtCore import QSize
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
        self.shells = []
        self.isNeedUpdate = True
        self.shelldir = ''
        self.curShellIndex = -1

    def loadBalloon(self, shellpath):
        shell = Balloon(shellpath)
        if shell.isInitialized is False:
            return

        isExist = False
        for s in self.shells:
            if shell.id == s.id and shell.name == s.name:
                isExist = True
                break

        if not isExist:
            logging.info("scan balloon: %s", shell.name)
            self.shells.append(shell)
        pass

    def loadAllBalloon(self, shelldir):
        self.shelldir = shelldir

        for parent, dirnames, filenames in os.walk(shelldir):
            for dirname in dirnames:
                shellpath = os.path.join(parent, dirname)
                self.loadBalloon(shellpath)

        logging.info("balloon count: %d", len(self.shells))
        #self.setCurShell(kikka.memory.readDeepMemory('CurShell', 0))


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
        self.clipW = None
        self.minimumsize = None
        self.flipBackground = False
        self.noFlipCenter = False
        pass


    def load(self):
        if self.isLoaded is False:
            logging.info("load balloon: %s", self.name)
            self._load_surfaces()

            # load PNG
            self._loadPNGindex()
            for filename, _ in self._pngs.items():
                p = os.path.join(self.balloonpath, filename)
                self._pngs[filename] = kikka.helper.getImage(p)
            self.isLoaded = True
        pass

    def _loadPNGindex(self):
        for parent, dirnames, filenames in os.walk(self.balloonpath):
            for filename in filenames:
                a = filename[len(filename) - 4:]
                if filename[len(filename) - 4:] == '.png':
                    self._pngs[filename] = None
        pass

    def _load_descript(self, map):
        for keys, values in map.items():
            key = keys.split('.')
            value = values.split(',')

            if key[0] == 'clip':
                if key[1] == 'width':
                    l = int(value[0])
                    if l == 3 and len(value) == 4:
                        self.clipW = [int(value[1]), int(value[2]), int(value[3])]
                    elif l == 5 and len(value) == 6:
                        self.clipW = [int(value[1]), int(value[2]), int(value[3]), int(value[1]), int(value[1])]
                elif key[1] == 'height':
                    l = int(value[0])
                    if l == 3 and len(value) == 4:
                        self.clipH = [int(value[1]), int(value[2]), int(value[3])]
                    elif l == 5 and len(value) == 6:
                        self.clipH = [int(value[1]), int(value[2]), int(value[3]), int(value[1]), int(value[1])]
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
            elif key[0] == 'charset' \
                    or key[0] == 'kero' \
                    or key[0:4] == 'char' \
                    or key[0] == 'shiori' \
                    or key[0] == 'mode' \
                    or key[0] == 'seriko':
                # self._IgnoreParams(keys, values)
                pass

            # unknow params
            else:
                self._IgnoreParams(keys, values)
        pass

    def _IgnoreParams(self, key, values):
        print('unknow shell params: %s,%s' % (key, values))
        pass