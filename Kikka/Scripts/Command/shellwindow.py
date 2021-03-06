# coding=utf-8
import logging
import math

from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage, QCursor
from PyQt5.QtWidgets import QWidget

from kikka_const import GhostEvent
import kikka


class ShellWindow(QWidget):
    def __init__(self, soul, win_id):
        QWidget.__init__(self)
        self._soul = soul
        self._ghost = self._soul.getGhost()
        self.ID = win_id

        self._isMoving = False
        self._offset = QPoint(0, 0)
        self._boxes = {}
        self._movepos = QPoint(0, 0)
        self._mousepos = QPoint(0, 0)
        self._pixmap = None
        self._touchType = None
        self._touchPlace = None
        self._touchTick = 0

        self._init()

    def _init(self):
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        # self.setContextMenuPolicy(Qt.ActionsContextMenu)

        # size and position
        rect = self._soul.memoryRead('ShellRect', [])
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

    def _boxCollision(self, eventType, event):
        if self._isMoving is True:
            return

        mx = self._mousepos.x()
        my = self._mousepos.y()
        for cid, box in self._boxes.items():
            rect = box[0]
            if rect.contains(mx, my) is False:
                continue

            tag = box[1]
            param = kikka.helper.makeGhostEventParam(self._ghost.ID, self._soul.ID, eventType, tag)
            param.data['ShellWindowID'] = self.ID
            param.data['QEvent'] = event
            self._ghost.emitGhostEvent(param)

            # Touch
            if self._touchType == eventType and self._touchPlace == tag:
                self._touchTick += 1
            else:
                self._touchTick = 1
                self._touchType = eventType
                self._touchPlace = tag

            TouchArea = rect.width() * rect.height()
            requestTick = max(30.0, math.sqrt(TouchArea))
            # print(self._touchTick, requestTick)
            if self._touchTick > requestTick:
                self._touchTick = 0
                param.eventType = GhostEvent.Shell_MouseTouch
                param.eventTag = tag
                self._ghost.emitGhostEvent(param)
            return tag

        param = kikka.helper.makeGhostEventParam(self._ghost.ID, self._soul.ID, eventType, 'None')
        param.data['ShellWindowID'] = self.ID
        param.data['QEvent'] = event
        self._ghost.emitGhostEvent(param)
        return None

    def _mouseLogging(self, event, button, x, y):
        if kikka.core.isDebug:
            page_sizes = dict((n, x) for x, n in vars(Qt).items() if isinstance(n, Qt.MouseButton))
            logging.debug("%s %s (%d, %d)", event, page_sizes[button], x, y)

    def getMousePose(self):
        return self._movepos.x(), self._movepos.y()

    def saveShellRect(self):
        rect = [self.pos().x(), self.pos().y(), self.size().width(), self.size().height()]
        self._soul.memoryWrite('ShellRect', rect)

    def debugDraw(self, image):

        def drawText(_painter, _line, _left, msg, color=Qt.white):
            _painter.setPen(color)
            _painter.drawText(_left, _line*12, msg)
            return _line+1

        def drawPoint(_painter, point, color=Qt.red):
            _painter.setPen(color)
            _painter.drawEllipse(QRect(point.x() - 5, point.y() - 5, 10, 10))
            _painter.drawPoint(point.x(), point.y())

        shell = self._ghost.getShell()
        shell_offset = shell.getOffset(self._soul.ID)
        surface_center = self._soul.getCenterPoint()
        draw_offset = self._soul.getDrawOffset()

        img = QImage(image.width()+250, max(image.height()+1, 120), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(img)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(0, 0, img.width(), img.height(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawImage(QPoint(), image)

        if kikka.core.isDebug is True:
            painter.fillRect(QRect(image.width(), 0, 250, img.height()), QColor(0, 0, 0, 255))
            painter.setPen(Qt.white)
            painter.drawRect(QRect(0, 0, image.width(), image.height()))

            left = image.width() + 3
            line = 1
            line = drawText(painter, line, left, "Ghost ID: %d" % self._ghost.ID)
            line = drawText(painter, line, left, "Name: %s" % self._ghost.name)
            line = drawText(painter, line, left, "Soul ID: %d" % self._soul.ID)
            line = drawText(painter, line, left, "surface: %d" % self._soul.getCurrentSurfaceID())
            line = drawText(painter, line, left, "bind: %s" % shell.getBind(self._soul.ID))
            line = drawText(painter, line, left, "animations: %s" % self._soul.getRunningAnimation())
            line = drawText(painter, line, left, "shell offset: %d %d" % (shell_offset.x(), shell_offset.y()), Qt.green)
            line = drawText(painter, line, left, "draw offset: %d %d" % (draw_offset.x(), draw_offset.y()), Qt.blue)
            line = drawText(painter, line, left, "surface center: %d %d" % (surface_center.x(), surface_center.y()), Qt.red)

        if kikka.shell.isDebug is True:
            painter.setPen(Qt.blue)
            painter.drawRect(self._soul.getBaseRect().translated(draw_offset))

            drawPoint(painter, shell_offset, Qt.green)
            drawPoint(painter, draw_offset, Qt.blue)
            drawPoint(painter, surface_center, Qt.red)

            surface = self._soul.getCurrentSurface()
            if surface is not None:
                for cid, col in surface.CollisionBoxes.items():
                    painter.setPen(Qt.red)
                    rect = QRect(col.Point1, col.Point2)
                    rect.moveTopLeft(col.Point1 + draw_offset)
                    painter.drawRect(rect)
                    painter.fillRect(rect, QColor(255, 255, 255, 64))
                    painter.setPen(Qt.black)
                    painter.drawText(rect, Qt.AlignCenter, col.tag)
            pass
        painter.end()
        return img

    def setImage(self, image):
        if kikka.core.isDebug | kikka.shell.isDebug:
            image = self.debugDraw(image)
        pixmap = QPixmap().fromImage(image, Qt.AutoColor)
        self._pixmap = pixmap

        self.setFixedSize(self._pixmap.size())
        self.setMask(self._pixmap.mask())
        self.repaint()

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
        # logging.info('contextMenuEvent')
        self._soul.showMenu(event.globalPos())

    def mousePressEvent(self, event):
        self._mouseLogging("mousePressEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._movepos = event.globalPos() - self.pos()
        if event.buttons() == Qt.LeftButton:
            self._isMoving = True
            event.accept()

        self._boxCollision(GhostEvent.Shell_MouseDown, event)

    def mouseMoveEvent(self, event):
        # self._mouseLogging("mouseMoveEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._mousepos = event.pos()
        if self._isMoving and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._movepos)

            self._soul.getDialog().updatePosition()
            event.accept()
        else:
            self._isMoving = False

        tag = self._boxCollision(GhostEvent.Shell_MouseMove, event)
        if tag == 'Bust':
            self.setCursor(QCursor(Qt.OpenHandCursor))
        elif tag is None:
            self.setCursor(QCursor(Qt.ArrowCursor))
        else:
            self.setCursor(QCursor(Qt.PointingHandCursor))

    def mouseReleaseEvent(self, event):
        self._mouseLogging("mouseReleaseEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        self._isMoving = False
        self.saveShellRect()

        self._boxCollision(GhostEvent.Shell_MouseUp, event)

    def mouseDoubleClickEvent(self, event):
        self._mouseLogging("mouseDoubleClickEvent", event.buttons(), event.globalPos().x(), event.globalPos().y())
        if event.buttons() == Qt.LeftButton:
            self._isMoving = False

        self._boxCollision(GhostEvent.Shell_MouseDoubleClick, event)

    def wheelEvent(self, event):
        # self._mouseLogging("wheelEvent", btn, event.pos().x(), event.pos().y())
        self._boxCollision(GhostEvent.Shell_WheelEvent, event)

    def dragEnterEvent(self, event):

        event.accept()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            logging.info("drop file: %s" % url.toLocalFile())
        pass

    def move(self, *__args):
        if len(__args) == 1 and isinstance(__args[0], QPoint):
            x = __args[0].x()
            y = __args[0].y()
        elif len(__args) == 2 and isinstance(__args[0], int) and isinstance(__args[1], int):
            x = __args[0]
            y = __args[1]
        else:
            super().move(*__args)
            return

        if self._ghost.getIsLockOnTaskbar() is True:
            y = kikka.helper.getScreenClientRect()[1]-self.height()
        super().move(x, y)

    ###############################################################################################################
    # paint event

    def show(self):
        param = kikka.helper.makeGhostEventParam(self._ghost.ID, self._soul.ID, kikka.const.GhostEvent.Shell_Show, 'Show')
        self._ghost.emitGhostEvent(param)

        super().show()
        self.move(self.pos())

    def paintEvent(self, event):
        if self._pixmap is None:
            return
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self._pixmap)


