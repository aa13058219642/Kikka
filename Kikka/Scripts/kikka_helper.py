# coding=utf-8
import os
import sys
import hashlib
import logging
import copy

from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QApplication


class GhostEventParam:
    def __init__(self, ghostID, eventType=0, eventTag='', data=None):
        self.ghostID = ghostID
        self.eventType = eventType
        self.eventTag = eventTag
        self.data = {} if data is None else data

    def copy(self):
        return GhostEventParam(self.ghostID, self.eventType, self.eventTag, copy.deepcopy(self.data))


class KikkaHelper:
    _instance = None
    PATH_ROOT = 0
    PATH_SCRIPTS = 1
    PATH_BIN = 11
    PATH_MOUDLES = 12
    PATH_RESOURCES = 2
    PATH_SHELL = 21
    PATH_BALLOON = 22

    def __init__(self, **kwargs):
        raise SyntaxError('The class is Singletion, please use KikkaHelper.this() or kikka.helper')

    @staticmethod
    def this():
        if KikkaHelper._instance is None:
            KikkaHelper._instance = object.__new__(KikkaHelper)
            KikkaHelper._instance._init()
        return KikkaHelper._instance

    def _init(self):
        fn = os.path.join(sys.path[0], 'Resources/default.png')
        if os.path.exists(fn): self._defaultImage = QImage(fn)
        else: self._defaultImage = QImage(1, 1, QImage.Format_RGBA8888)

    @staticmethod
    def getPath(tag):
        path = ''
        if tag == KikkaHelper.PATH_ROOT: path = sys.path[0]
        elif tag == KikkaHelper.PATH_SCRIPTS: path = os.path.join(sys.path[0], 'Scripts')
        elif tag == KikkaHelper.PATH_BIN: path = os.path.join(sys.path[0], 'Scripts/Bin')
        elif tag == KikkaHelper.PATH_MOUDLES: path = os.path.join(sys.path[0], 'Scripts/Moudles')
        elif tag == KikkaHelper.PATH_RESOURCES: path = os.path.join(sys.path[0], 'Resources')
        elif tag == KikkaHelper.PATH_SHELL: path = os.path.join(sys.path[0], 'Resources/Shell')
        elif tag == KikkaHelper.PATH_BALLOON: path = os.path.join(sys.path[0], 'Resources/Balloon')
        return path

    @staticmethod
    def checkEncoding(filepath):
        CODES = ['UTF-8', 'GBK', 'Shift-JIF', 'GB18030', 'BIG5', 'UTF-16']

        # UTF-8 BOM前缀字节
        UTF_8_BOM = b'\xef\xbb\xbf'

        f = None
        b = ""
        filecode = None
        for code in CODES:
            try:
                f = open(filepath, 'rb')
                b = f.read()
                b.decode(encoding=code)
                f.close()
                filecode = code
                break
            except Exception:
                f.close()
                continue

        if 'UTF-8' == filecode and b.startswith(UTF_8_BOM):
            filecode = 'UTF-8-SIG'

        if filecode is None:
            raise SyntaxError('Uknow file encoding: %s' % filepath)

        return filecode

    @staticmethod
    def getScreenResolution():
        rect = QApplication.instance().desktop().screenGeometry()
        return (rect.width(), rect.height())

    @staticmethod
    def getScreenClientRect():
        rect = QApplication.instance().desktop().availableGeometry()
        return (rect.width(), rect.height())

    def getDefaultImage(self):
        return QImage(self._defaultImage)

    def getImage(self, filepath):
        if os.path.exists(filepath):
            return QImage(filepath)
        else:
            logging.warning("Image lost: %s" % filepath)
            return QImage(self._defaultImage)

    @staticmethod
    def drawImage(destImage, srcImage, x, y, drawtype):
        if destImage is None or srcImage is None:
            return

        if drawtype == 'base' or drawtype == 'overlay':
            mode = QPainter.CompositionMode_SourceOver
        elif drawtype == 'overlayfast':
            mode = QPainter.CompositionMode_SourceAtop
        elif drawtype == 'replace':
            mode = QPainter.CompositionMode_Source
        elif drawtype == 'interpolate':
            mode = QPainter.CompositionMode_DestinationOver
        elif drawtype == 'asis':
            mode = QPainter.CompositionMode_DestinationAtop
        else:
            mode = QPainter.CompositionMode_SourceOver

        painter = QPainter(destImage)
        painter.setCompositionMode(mode)
        painter.drawImage(QPoint(x, y), srcImage)
        painter.end()

    @staticmethod
    def getMD5(s):
        md5 = hashlib.md5()
        md5.update(s.encode())
        return md5.hexdigest()

    @staticmethod
    def getShortMD5(s):
        md5 = hashlib.md5()
        md5.update(s.encode())
        return md5.hexdigest()[8:24]

    @staticmethod
    def makeGhostEventParam(ghostID, eventType=0, eventTag='', data=None):
        return GhostEventParam(ghostID, eventType, eventTag, data)
