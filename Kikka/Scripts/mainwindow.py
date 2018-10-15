import logging

from PyQt5.QtCore import Qt, QRect, QPoint, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor, QInputMethodQueryEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QApplication

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

        pixmap = QPixmap(1, 1)
        self._pixmap = pixmap
        self._message = ""
        self._color = QColor.black
        self._alignment = Qt.AlignLeft

        self.setFixedSize(self._pixmap.size())
        self.setMask(self._pixmap.mask())

        self._isMoving = False
        self._boxes = {}
        self._movepos = QPoint(0, 0)
        self._mousepos = QPoint(0, 0)

        self.menu = KikkaMenu.this()
        self.menu.addMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showSystemMenu)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        text = ''
        if event.type() == QEvent.UpdateRequest:text = 'UpdateRequest'
        elif event.type() == QEvent.Leave:text = 'Leave'
        elif event.type() == QEvent.Enter:text = 'Enter'
        elif event.type() == QEvent.ToolTip:text = 'ToolTip'
        elif event.type() == QEvent.StatusTip:text = 'StatusTip'
        elif event.type() == QEvent.ZOrderChange:text = 'ZOrderChange'
        elif event.type() == QEvent.Show:text = 'Show'
        elif event.type() == QEvent.ShowToParent:text = 'ShowToParent'
        elif event.type() == QEvent.UpdateLater:text = 'UpdateLater'
        elif event.type() == QEvent.MouseMove:text = 'MouseMove'
        elif event.type() == QEvent.Close:text = 'Close'
        elif event.type() == QEvent.Hide:text = 'Hide'
        elif event.type() == QEvent.HideToParent:text = 'HideToParent'
        elif event.type() == QEvent.Timer:text = 'Timer'
        elif event.type() == QEvent.Paint:text = 'Paint'
        elif event.type() == QEvent.Move:text = 'Move'
        elif event.type() == QEvent.InputMethodQuery:text = 'InputMethodQuery';self._InputMethodQuery = event
        elif event.type() == QEvent.MouseButtonPress:text = 'MouseButtonPress(%d %d)' % (event.globalPos().x(), event.globalPos().y())

        logging.info("%s %d %s"%("MainWindow", event.type(), text))
        return False

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
            if rect.contains(mx, my) is True:
                return box[1]
        return ''
    
    def _mouseLogging(self, event, button, x, y):
        if self._isDebug is False:
            return
        page_sizes = dict((n, x) for x, n in vars(Qt).items() if isinstance(n, Qt.MouseButton))
        logging.debug("%s %s (%d, %d)", event, page_sizes[button], x, y)

    def leaveEvent(self, QEvent):
        logging.info("leaveEvent")
        self._isMoving = False

    def enterEvent(self, QEvent):
        logging.info("enterEvent")
        self.activateWindow()
        #self._isMoving = False

    def inputMethodEvent(self, event):
        logging.info("inputMethodEvent")

    def mousePressEvent(self, event):
        btn = event.buttons()
        self._mouseLogging("mousePressEvent", btn, event.globalPos().x(), event.globalPos().y())
        self._movepos = event.globalPos() - self.pos()
        if event.buttons() == Qt.LeftButton:

            self._isMoving = True
            #e =QInputMethodQueryEvent(queries=0x101)
            #e = QInputMethodQuery()
            #QApplication.sendEvent(self, QEvent.InputMethodQuery)
            event.accept()

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.MouseDown, boxevent)

    def mouseMoveEvent(self, event):
        #logging.info("mouseMoveEvent##################")
        btn = event.buttons()
        self._mouseLogging("mouseMoveEvent", btn, event.globalPos().x(), event.globalPos().y())

        self._mousepos = event.pos()
        if self._isMoving and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._movepos)
            event.accept()
        else:
            self._isMoving = False

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '':
                MouseEvent.event_selector(MouseEvent.MouseMove, boxevent)

    def mouseDoubleClickEvent(self, event):
        btn = event.buttons()
        #self._mouseLogging("mouseDoubleClickEvent", btn, event.globalPos().x(), event.globalPos().y())
        if btn == Qt.LeftButton:
            self._isMoving = False

        if self._isMoving is False:
            boxevent = self._boxCollision()
            if boxevent != '': MouseEvent.event_selector(MouseEvent.MouseDoubleClick, boxevent)

    def wheelEvent(self, event):
        btn = event.buttons()
        #self._mouseLogging("wheelEvent", btn, event.pos().x(), event.pos().y())
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
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._pixmap)

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












