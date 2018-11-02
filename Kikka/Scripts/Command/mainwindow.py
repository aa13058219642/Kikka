# coding=utf-8
import logging

from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt5.QtWidgets import QWidget

from mouseevent import MouseEvent
import kikka


class MainWindow(QWidget):
    def __init__(self, parent, nid):
        QWidget.__init__(self)
        self._parent = parent
        self.nid = nid
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self._isMoving = False
        self._boxes = {}
        self._movepos = QPoint(0, 0)
        self._mousepos = QPoint(0, 0)
        self._pixmap = None

        # size and position
        rect = kikka.memory.read('KikkaRect', [])
        if len(rect) > 0:
            self.move(rect[0], rect[1])
            self.resize(rect[2], rect[3])

    def setBoxes(self, boxes, offset):
        self._boxes = {}
        for cid, col in boxes.items():
            rect = QRect(col.Point1, col.Point2)
            rect.moveTopLeft(col.Point1 + offset)
            self._boxes[cid] = (rect, col.tag)

    def _boxCollision(self):
        mx = self._mousepos.x()
        my = self._mousepos.y()
        for cid, box in self._boxes.items():
            rect = box[0]
            if rect.contains(mx, my) is True:
                return box[1]
        return ''
    
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
        self._parent.showMenu(event.globalPos())

    def mousePressEvent(self, event):
        self._mouseLogging("mousePressEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._movepos = event.globalPos() - self.pos()
        if event.buttons() == Qt.LeftButton:
            self._isMoving = True
            event.accept()

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.MouseDown, boxevent)

    def mouseMoveEvent(self, event):
        # self._mouseLogging("mouseMoveEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())

        self._mousepos = event.pos()
        if self._isMoving and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._movepos)
            self._parent.getDialog(self.nid).updatePosition()
            event.accept()
        else:
            self._isMoving = False

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '':
                MouseEvent.event_selector(MouseEvent.MouseMove, boxevent)

    def mouseReleaseEvent(self, event):
        self._mouseLogging("mouseReleaseEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._isMoving = False
        kikka.memory.write('KikkaRect', [self.pos().x(), self.pos().y(), self.size().width(), self.size().height()])

    def mouseDoubleClickEvent(self, event):
        self._mouseLogging("mouseDoubleClickEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        if event.buttons() == Qt.LeftButton:
            self._isMoving = False
            self._parent.getDialog(self.nid).show()

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.MouseDoubleClick, boxevent)

    def wheelEvent(self, event):
        # self._mouseLogging("wheelEvent", btn, event.pos().x(), event.pos().y())
        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.WheelEvent, boxevent)

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
        painter.setPen(Qt.green)
        painter.drawRect(QRect(0, 0, self.size().width()-1, self.size().height()-1))

    def setImage(self, image):
        # image = QImage(r"C:\\test.png")
        pixmap = QPixmap().fromImage(image, Qt.AutoColor)
        self._pixmap = pixmap

        self.setFixedSize(self._pixmap.size())
        self.setMask(self._pixmap.mask())
        self.repaint()

