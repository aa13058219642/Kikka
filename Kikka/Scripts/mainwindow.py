import logging

from PyQt5.QtCore import Qt, QRect, QPoint, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QWidget

from systemmenu import SystemMenu
from mouseevent import MouseEvent
from kikkamenu import Menu, KikkaMenu


class MainWindow(QWidget):
    def __init__(self, isDebug=False):
        QWidget.__init__(self)
        self._isDebug = isDebug
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.CollisionBoxes = {}

        pixmap = QPixmap(1,1)
        self._pixmap = pixmap
        self._message = ""
        self._color = QColor.black
        self._alignment = Qt.AlignLeft

        self.setFixedSize(self._pixmap.size())
        self.setMask(self._pixmap.mask())

        self._isMoving = False
        self._boxes = {}
        self._movepos = QPoint(0, 0)

        self.menu = KikkaMenu.this()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showSystemMenu)

    def showSystemMenu(self, pos):
        self.menu.setPos(self.pos() + pos)
        self.menu.show()

    ###############################################################################################################
    # Event

    def setBoxes(self, boxes):
        self._boxes = {}
        for cid, col in boxes.items():
            rect = QRect(QPoint(col.Point1[0], col.Point1[1]), QPoint(col.Point2[0], col.Point2[1]))
            self._boxes[cid] = (rect, col.tag)

    def _boxCollision(self):
        mx = self._mousepos.x()
        my = self._mousepos.y()
        for cid, box in self._boxes.items():
            rect = box[0]
            if rect.contains(mx,my) is True:
                return box[1]
        return ''
    
    def _mouseLogging(self, event, button, x, y):
        if self._isDebug is False:
            return
        page_sizes = dict((n, x) for x, n in vars(Qt).items() if isinstance(n, Qt.MouseButton))
        logging.debug("%s %s (%d, %d)", event, page_sizes[button], x, y)


    def mousePressEvent(self, event):
        btn = event.buttons()
        self._mouseLogging("mousePressEvent", btn, event.pos().x(), event.pos().y())
        if event.buttons() == Qt.LeftButton:
            #self.menu.Hide()
            self._movepos = event.globalPos()
            event.accept()
            self._isMoving = True

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.MouseDown, boxevent)

    def mouseMoveEvent(self, event):
        btn = event.buttons()
        self._mouseLogging("mouseMoveEvent", btn, event.pos().x(), event.pos().y())

        self._mousepos = event.pos()
        if btn == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self._movepos)
            self._movepos = event.globalPos()
            event.accept()
        else:
            self._isMoving = False

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.MouseMove, boxevent)

    def mouseDoubleClickEvent(self, event):
        btn = event.buttons()
        self._mouseLogging("mouseDoubleClickEvent", btn, event.pos().x(), event.pos().y())
        if btn == Qt.LeftButton:
            self._isMoving = False

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.MouseDoubleClick, boxevent)

    def wheelEvent(self, event):
        btn = event.buttons()
        self._mouseLogging("wheelEvent", btn, event.pos().x(), event.pos().y())
        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.WheelEvent, boxevent)

    def dragEnterEvent(self, event):

        event.accept()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            logging.info("drop file: %s"%url.toLocalFile())
        pass

    def getMousePose(self):

        return self._movepos.x(), self._movepos.y()

    ###############################################################################################################
    # paint event

    def paintEvent(self, event):
        textbox = QRect(self.rect())
        textbox.setRect(textbox.x() + 5, textbox.y() + 5,
                        textbox.width() - 10, textbox.height() - 10)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._pixmap)
        # pen = QtGui.QPen(QBrush(QtGui.QColor.yellow),2,)
        painter.setPen(Qt.red)
        painter.drawText(textbox, self._alignment, self._message)

    def clearMessage(self):
        self._message.clear()
        self.repaint()

    def showMessage(self, message, alignment=Qt.AlignLeft,color=QColor.black):
        self._message = message
        self._alignment = alignment
        self._color = color
        self.repaint()

    def setImage(self, image):
        # painter = QPainter(image)
        pixmap = QPixmap().fromImage(image, Qt.AutoColor)
        self._pixmap = pixmap
        self._message = "132"
        self._color = QColor.black
        self._alignment = Qt.AlignLeft
    
        self.setFixedSize(self._pixmap.size())
        self.setMask(self._pixmap.mask())
    
        self.repaint()












