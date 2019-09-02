# coding=utf-8
import logging

from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage, QFont
from PyQt5.QtWidgets import QWidget

from ghostevent import GhostEvent
import kikka


class ShellWindow(QWidget):
    def __init__(self, soul, winid):
        QWidget.__init__(self)
        self._soul = soul
        self._ghost = self._soul.getGhost()
        self.winid = winid
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        #self.setContextMenuPolicy(Qt.ActionsContextMenu)

        self._isMoving = False
        self._offset = QPoint(0, 0)
        self._boxes = {}
        self._movepos = QPoint(0, 0)
        self._mousepos = QPoint(0, 0)
        self._pixmap = None

        # size and position
        rect = self._ghost.memoryRead('ShellRect', [], self.winid)
        if len(rect) > 0:
            self.move(rect[0], rect[1])
            self.resize(rect[2], rect[3])

    def setBoxes(self, boxes, offset):
        self._boxes = {}
        self._offset = offset
        for cid, col in boxes.items():
            rect = QRect(col.Point1, col.Point2)
            rect.moveTopLeft(col.Point1 + offset)
            self._boxes[cid] = (rect, col.tag)

    def _boxCollision(self, event):
        if self._isMoving is True:
            return

        mx = self._mousepos.x()
        my = self._mousepos.y()
        for cid, box in self._boxes.items():
            rect = box[0]
            if rect.contains(mx, my) is True:
                tag = box[1]
                self._ghost.event_selector(event, tag, nid=self.winid)
                return
        pass
    
    def _mouseLogging(self, event, button, x, y):
        page_sizes = dict((n, x) for x, n in vars(Qt).items() if isinstance(n, Qt.MouseButton))
        logging.debug("%s %s (%d, %d)", event, page_sizes[button], x, y)

    # ##############################################################################################################
    # Event

    # def eventFilter(self, obj, event):
    #     text = ''
    #     if event.type() == QEvent.UpdateRequest:text = 'UpdateRequest'
    #     elif event.type() == QEvent.Leave:text = 'Leave'
    #     elif event.type() == QEvent.Enter:text = 'Enter'
    #     elif event.type() == QEvent.ToolTip:text = 'ToolTip'
    #     elif event.type() == QEvent.StatusTip:text = 'StatusTip'
    #     elif event.type() == QEvent.ZOrderChange:text = 'ZOrderChange'
    #     elif event.type() == QEvent.Show:text = 'Show'
    #     elif event.type() == QEvent.ShowToParent:text = 'ShowToParent'
    #     elif event.type() == QEvent.UpdateLater:text = 'UpdateLater'
    #     elif event.type() == QEvent.MouseMove:text = 'MouseMove'
    #     elif event.type() == QEvent.Close:text = 'Close'
    #     elif event.type() == QEvent.Hide:text = 'Hide'
    #     elif event.type() == QEvent.HideToParent:text = 'HideToParent'
    #     elif event.type() == QEvent.Timer:text = 'Timer'
    #     elif event.type() == QEvent.Paint:text = 'Paint'
    #     elif event.type() == QEvent.Move:text = 'Move'
    #     elif event.type() == QEvent.InputMethodQuery:text = 'InputMethodQuery';self._InputMethodQuery = event
    #     elif event.type() == QEvent.MouseButtonPress:
    #         text = 'MouseButtonPress(%d %d)' % (event.globalPos().x(), event.globalPos().y())
    #
    #     logging.info("%s %d %s"%("MainWindow", event.type(), text))
    #     return False

    def contextMenuEvent(self, event):
        self._ghost.showMenu(self.winid, event.globalPos())
        logging.info('contextMenuEvent')

    def mousePressEvent(self, event):
        self._mouseLogging("mousePressEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._movepos = event.globalPos() - self.pos()
        if event.buttons() == Qt.LeftButton:
            self._isMoving = True
            event.accept()

        self._boxCollision(GhostEvent.MouseDown)
        # if self._isMoving is False:
        #     eventtag = self._boxCollision()
        #     if eventtag is not None:
        #         self._ghost.event_selector(self.nid, GhostEvent.MouseDown, eventtag)
        pass

    def mouseMoveEvent(self, event):
        # self._mouseLogging("mouseMoveEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._mousepos = event.pos()
        if self._isMoving and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._movepos)
            self._ghost.getDialog(self.winid).updatePosition()
            event.accept()
        else:
            self._isMoving = False

        self._boxCollision(GhostEvent.MouseMove)
        # if self._isMoving is False:
        #     eventtag = self._boxCollision()
        #     if eventtag is not None:
        #         self._ghost.event_selector(self.nid, GhostEvent.MouseMove, eventtag)
        pass

    def mouseReleaseEvent(self, event):
        self._mouseLogging("mouseReleaseEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._isMoving = False
        self._ghost.memoryWrite('ShellRect',
                                [self.pos().x(), self.pos().y(), self.size().width(), self.size().height()],
                                self.winid)

        self._boxCollision(GhostEvent.MouseUp)
        # eventtag = self._boxCollision()
        # if eventtag is not None:
        #     self._ghost.event_selector(self.nid, GhostEvent.MouseUp, eventtag)
        pass

    def mouseDoubleClickEvent(self, event):
        self._mouseLogging("mouseDoubleClickEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        if event.buttons() == Qt.LeftButton:
            self._isMoving = False
            self._ghost.getDialog(self.winid).show()

        self._boxCollision(GhostEvent.MouseDoubleClick)
        # if self._isMoving is False:
        #     eventtag = self._boxCollision()
        #     if eventtag is not None:
        #         self._ghost.event_selector(self.nid, GhostEvent.MouseDoubleClick, eventtag)
        pass

    def wheelEvent(self, event):
        # self._mouseLogging("wheelEvent", btn, event.pos().x(), event.pos().y())
        self._boxCollision(GhostEvent.WheelEvent)
        # if self._isMoving is False:
        #     eventtag = self._boxCollision()
        #     if eventtag is not None:
        #         self._ghost.event_selector(self.nid, GhostEvent.WheelEvent, eventtag)
        pass

    def dragEnterEvent(self, event):

        event.accept()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            logging.info("drop file: %s" % url.toLocalFile())
        pass

    def getMousePose(self):

        return self._movepos.x(), self._movepos.y()

    ###############################################################################################################
    # paint event

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._pixmap)

    def debugDraw(self, image):
        shell = self._ghost.getShell()
        img = QImage(image)
        painter = QPainter(img)

        if kikka.core.isDebug is True:
            painter.fillRect(QRect(0, 0, 256, 128), QColor(0, 0, 0, 64))
            painter.setPen(Qt.green)
            painter.drawRect(QRect(0, 0, image.width() - 1, image.height() - 1))
            painter.drawText(3, 12, "Ghost ID: %d" % self._ghost.gid)
            painter.drawText(3, 24, "Name: %s" % self._ghost.name)
            painter.drawText(3, 36, "Soul ID: %d" % self._soul.ID)
            painter.drawText(3, 48, "surface: %d" % self._soul.getCurrentSurfaceID())
            painter.drawText(3, 60, "shell offset: %d %d" % (self._offset.x(), self._offset.y()))
            painter.drawText(3, 72, "bind: %s" % self._soul.getBind())
            painter.drawText(3, 84, "animations: %s" % self._soul.getRunningAnimation())

        if kikka.shell.isDebug is True:
            painter.setPen(Qt.red)
            painter.drawEllipse(QRect(self._offset.x()-5,self._offset.y()-5,10,10))
            painter.drawPoint(self._offset)

            surface = self._soul.getCurrentSurface()
            for cid, col in surface.CollisionBoxes.items():
                painter.setPen(Qt.red)
                rect = QRect(col.Point1, col.Point2)
                rect.moveTopLeft(col.Point1 + self._offset)
                painter.drawRect(rect)
                painter.fillRect(rect, QColor(255, 255, 255, 64))
                painter.setPen(Qt.black)
                painter.drawText(rect, Qt.AlignCenter, col.tag)
            pass
        painter.end()
        return img

    def setImage(self, image):
        # image = QImage(r"C:\\test.png")

        img = self.debugDraw(image)
        pixmap = QPixmap().fromImage(img, Qt.AutoColor)
        self._pixmap = pixmap

        self.setFixedSize(self._pixmap.size())
        self.setMask(self._pixmap.mask())
        self.repaint()
