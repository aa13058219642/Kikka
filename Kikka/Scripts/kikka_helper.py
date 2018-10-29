# coding=utf-8
import os
import sys
import hashlib

from win32api import GetSystemMetrics
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage


class KikkaHelper:
    PATH_ROOT = 0
    PATH_SCRIPTS = 1
    PATH_BIN = 11
    PATH_MOUDLES = 12
    PATH_RESOURCES = 2
    PATH_SHELL = 21

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
        else: self._defaultImage = QImage(QSize(1, 1))

        pass

    @staticmethod
    def getPath(tag):
        path = ''
        if tag == KikkaHelper.PATH_ROOT: path = sys.path[0]
        elif tag == KikkaHelper.PATH_SCRIPTS: path = os.path.join(sys.path[0], 'Scripts')
        elif tag == KikkaHelper.PATH_BIN: path = os.path.join(sys.path[0], 'Scripts/Bin')
        elif tag == KikkaHelper.PATH_MOUDLES: path = os.path.join(sys.path[0], 'Scripts/Moudles')
        elif tag == KikkaHelper.PATH_RESOURCES: path = os.path.join(sys.path[0], 'Resources')
        elif tag == KikkaHelper.PATH_SHELL: path = os.path.join(sys.path[0], 'Resources/Shell')
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
        w = GetSystemMetrics(0)
        h = GetSystemMetrics(1)
        return w, h

    def getDefaultImage(self):
        return QImage(self._defaultImage)

    def getImage(self, filepath):
        if os.path.exists(filepath):
            return QImage(filepath)
        else:
            return QImage(self._defaultImage)

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





