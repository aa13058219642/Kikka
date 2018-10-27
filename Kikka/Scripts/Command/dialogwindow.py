import sys
import logging

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage, QPalette, QBrush
from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout

import kikkahelper
import kikka


class Dialog(QWidget):
    def __init__(self, parent):
        self._parent = parent
        QWidget.__init__(self)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_DeleteOnClose)
        # self.setMouseTracking(True)
        # self.setAcceptDrops(True)

        self._isChangeSizeMode = False
        self._backgroundSource = None
        self._backgroundImage = None
        self._backgroundPixmap = None
        self._backgroundMask = None
        self._backgroundRect = None

        self.setBackgroundImage()
        style = '''
        QPushButton{
            border-style: solid;
            background-color: #FF0000;
            padding: 3px;
        } 
        QPushButton:hover{
            text-decoration: underline;
        } 
        '''
        self.setStyleSheet(style)
        self._initLayout()

        # image = QImage(r"C:\\test.png")
        # pixmap = QPixmap().fromImage(image, Qt.AutoColor)
        # self.resize(pixmap.size())
        # self.setMask(pixmap.mask())
        # self._mask = self.mask()
        pass

    def _initLayout(self):
        self.mainLayout = QVBoxLayout()
        self.stackedLayout = QStackedLayout()
        self.topLayout = QVBoxLayout()

        # 0 main Layout
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.stackedLayout)
        self.setLayout(self.mainLayout)

        # 1.0 top layout
        self.toplabel = QLabel("Hello")
        self.topLayout.addWidget(self.toplabel)

        # 1.2 tab layout
        self.tabLayout = QHBoxLayout()
        self.topLayout.addLayout(self.tabLayout)

        # 1.2.1 tab button
        p1 = QPushButton("page1")
        p2 = QPushButton("page2")
        p3 = QPushButton("page3")
        p1.clicked.connect(lambda: self.stackedLayout.setCurrentIndex(0))
        p2.clicked.connect(lambda: self.stackedLayout.setCurrentIndex(1))
        p3.clicked.connect(lambda: self.stackedLayout.setCurrentIndex(2))
        self.tabLayout.addWidget(p1)
        self.tabLayout.addWidget(p2)
        self.tabLayout.addWidget(p3)

        # 2.0 gird layouts
        self.girdlayouts = []
        for i in range(3):
            girdlayout = QGridLayout()
            self.girdlayouts.append(girdlayout)

            page = QWidget()
            page.setLayout(girdlayout)
            self.stackedLayout.addWidget(page)

        # 2.1 page1
        for i in range(3):
            girdlayout = self.girdlayouts[i]
            for j in range(5):
                but = QPushButton("move%d(%d)" % (i, j))
                but.clicked.connect(self.setChangeSizeMode)
                girdlayout.addWidget(but, j, 0)

                but2 = QPushButton("close%d(%d)" % (i, j))
                but2.clicked.connect(lambda: self.hide())
                girdlayout.addWidget(but2, j, 1)
            but = QPushButton("move%d(%d)" % (i, 5))
            but.clicked.connect(self.setChangeSizeMode)
            girdlayout.addWidget(but, 5, 0)

    def setChangeSizeMode(self):
        self._isChangeSizeMode = not self._isChangeSizeMode
        if self._isChangeSizeMode is True:
            self.clearMask()
            self.setWindowFlag(Qt.FramelessWindowHint, False)
            self.setWindowOpacity(0.8)
            self.setEnabled(False)

            self.show()
            offset = QPoint(self.geometry().x() - self.pos().x(), self.geometry().y() - self.pos().y())
            self.move(self.pos().x() - offset.x(), self.pos().y() - offset.y())
            self.update()
            self.activateWindow()
        else:
            sz = QSize(self.geometry().size())
            p_pos = self._parent.pos()
            geometry = QPoint(self.geometry().x(), self.geometry().y())
            pos = QPoint(self.pos().x(), self.pos().y())
            kikka.memory.write('DialogRect', [geometry.x() - p_pos.x(),
                                              geometry.y() - p_pos.y(),
                                              sz.width(),
                                              sz.height()])

            self.setWindowFlag(Qt.FramelessWindowHint, True)
            self.setWindowOpacity(1)
            self.setEnabled(True)
            self.setMask(self._backgroundMask)
            self.show()
            self.move(pos.x(), pos.y())

    def updatePosition(self):
        if self._isChangeSizeMode is True:
            return

        p_pos = self._parent.pos()
        p_size = self._parent.size()
        rect = kikka.memory.read('DialogRect', [])
        if len(rect) > 0:
            x = rect[0] + p_pos.x()
            y = rect[1] + p_pos.y()
            self.resize(rect[2], rect[3])
        else:
            x = int(p_pos.x() - self.size().width())
            y = int(p_pos.y() + p_size.height() / 2 - self.size().height())
            self.resize(200, 220)
            kikka.memory.write('DialogRect', [x - p_pos.x(),
                                              y - p_pos.y(),
                                              self.size().width(),
                                              self.size().height()])
        pass

        sw, sh = kikkahelper.getScreenResolution()
        if x + self.width() > sw or x < 0:
            x = int(p_pos.x()*2 + p_size.width() - x - self.width())
            if x + self.width() > sw: x = p_pos.x() - self.width()
            if x < 0: x = p_pos.x() + p_size.width()

        super().move(x, y)
        self.getBackgroundImage()
        pass

    def show(self):
        super().show()
        self.updatePosition()
        pass

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.setChangeSizeMode()
        event.ignore()
        pass

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        logging.info("resizeEvent")
        self.getBackgroundImage()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._backgroundPixmap)
        super().paintEvent(event)

    def setBackgroundImage(self, image=None):
        self._backgroundSource = QImage(r"C:\\d2.png")
        w0 = self._backgroundSource.size().width() // 3
        h0 = self._backgroundSource.size().height() // 3
        sw = [w0, w0, w0]
        sh = [h0, h0, h0]

        srect = []
        for y in range(3):
            sr = []
            for x in range(3):
                pt = QPoint(0, 0)
                if x > 0: pt.setX(sr[x-1].x() + sw[x-1])
                if y > 0: pt.setY(srect[y-1][0].y() + sh[y-1])
                sz = QSize(sw[x], sh[y])
                sr.append(QRect(pt, sz))
                pass
            srect.append(sr)
        pass  # exit for

        self._backgroundRect = srect

    def getBackgroundImage(self):
        #logging.info("getBackgroundImage: (%d, %d)" % (sz.width(), sz.height()))

        self._backgroundImage = QImage(self.size(), QImage.Format_ARGB32)
        pixmap = QPixmap().fromImage(self._backgroundSource, Qt.AutoColor)

        # ssw = self._backgroundSource.size().width()
        # bsh = self._backgroundSource.size().height()

        w0 = self._backgroundSource.size().width() // 3
        h0 = self._backgroundSource.size().height() // 3
        dw = [w0, self.size().width()-w0*2, w0]
        dh = [h0, self.size().height()-h0*2, h0]

        drect = []
        for y in range(3):
            dr = []
            for x in range(3):
                pt = QPoint(0, 0)
                if x > 0: pt.setX(dr[x-1].x() + dw[x-1])
                if y > 0: pt.setY(drect[y-1][0].y() + dh[y-1])
                sz = QSize(dw[x], dh[y])
                dr.append(QRect(pt, sz))
                pass
            drect.append(dr)
        pass  # exit for

        p = QPainter(self._backgroundImage)
        p.setCompositionMode(QPainter.CompositionMode_Source)

        # if self._isChangeSizeMode is True:
        #     p.fillRect(self.rect(), Qt.black)

        for y in range(3):
            for x in range(3):
                p.drawPixmap(drect[y][x], pixmap, self._backgroundRect[y][x])
        p.end()

        self._backgroundPixmap = QPixmap().fromImage(self._backgroundImage, Qt.AutoColor)
        self._backgroundMask = self._backgroundPixmap.mask()
        pass

