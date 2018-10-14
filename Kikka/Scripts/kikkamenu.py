import logging
import os
import sys

from PyQt5.QtCore import QRect, QSize, Qt, QRectF, QPoint, QMargins, QEvent
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QMenu, QStyle, QStyleOptionMenuItem, QStyleOption, QApplication, QWidget, QScrollArea, \
    QVBoxLayout, QFrame
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QImage, QPainter, QFontMetrics, QFont, QPalette, QColor, QPixmap

import kikkahelper


class KikkaMenu:
    _instance = None

    def __init__(self, **kwargs):
        raise SyntaxError('can not instance, please use KikkaMenu.this()')

    @staticmethod
    def this():
        if KikkaMenu._instance is None:
            KikkaMenu._instance = object.__new__(KikkaMenu)
            KikkaMenu._instance._init()
        return KikkaMenu._instance

    def _init(self):
        self._menu = MenuWidget("Main Menu")
        self._menu.addSubMenu("submenu")
        #self._menu.getmenu().addItem("submenu", self.show)
        # self._menu = Menu(QWidget())
        # self._menu.createAction()
        pass

    def hide(self):

        self._menu.Hide()
        # self._menu.hide()

    def show(self):
        self._menu.Show()
        # self._menu.show()
        self._menu.activateWindow()

    def setPos(self, pos):
        self._menu.updateSize()

        pos = QPoint(pos)
        w, h = kikkahelper.getScreenResolution()
        if pos.y() + self._menu.height() > h:
            pos.setY(h - self._menu.height())
        elif pos.y() < 0:
            pos.setY(0)

        if pos.x() + self._menu.width() > w:
            pos.setX(w - self._menu.width())
        elif pos.x() < 0:
            pos.setX(0)

        self._menu.move(pos)

    def addAction(self):
        pass




class MenuWidget(QWidget):
    def __init__(self, title='', level=0):
        QWidget.__init__(self, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.level = level
        self.submenu = {}
        self.setMinimumSize(250, 100)
        self.setMaximumSize(300, 700)
        self.installEventFilter(self)

        self._menu = Menu(self)
        self._menu.setTitle(title)
        self._menu.createAction()

        self._scrollarea = QScrollArea(self)
        self._scrollarea.setWidget(self._menu)
        self._scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scrollarea.setFrameShape(QFrame.NoFrame)

        self._vbox = QVBoxLayout()
        self._vbox.addWidget(self._scrollarea, alignment=Qt.AlignLeft)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._vbox)

    def Hide(self):

        self.hide()

    def Show(self):
        self.show()
        self.activateWindow()

    def setTitle(self, text):

        self._menu.setTitle(text)

    def updateSize(self):
        self.setFixedHeight(min(self._menu.height(), 700))
        self.setFixedWidth(min(self._menu.width(), 275))
        self._scrollarea.setFixedSize(self.size())

        pass

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.WindowDeactivate:
                logging.info("WindowDeactivate")
                self.Hide()
                return True
            elif event.type() == QEvent.Enter:
                logging.info("%s Enter"% self._menu.title())
                for i, m in self.submenu.items():
                    if m.level>self.level:
                        m.Hide()
                #self.Hide()
                return True

        return False

    def getmenu(self):
        return self._menu

    def addSubMenu(self, title):
        self.submenu[title] = MenuWidget(title, self.level + 1)
        #m = Menu(self, title)
        #m.addAction(QAction("menu2", self, triggered=self.Show))
        #self._menu.addAction(QAction(QIcon(r"D:\Projects\Kikka\Kikka\icon.ico"), title, self))
        self._menu.addItem(title, self.Show)
        self.updateSize()
        pass


    def showSubMenu(self, title):
        if title not in self.submenu: return
        self.submenu[title].Show()
    pass




class Menu(QMenu):
    def __init__(self, parent, title=''):
        QMenu.__init__(self, title, parent)
        self._parent = parent

        self.bg = QImage(os.path.join(kikkahelper.getPath(kikkahelper.PATH_SHELL), r"_Default_Kikka2\background.png"))
        self.fg = QImage(os.path.join(kikkahelper.getPath(kikkahelper.PATH_SHELL), r"_Default_Kikka2\foreground.png"))
        self.side = QImage(os.path.join(kikkahelper.getPath(kikkahelper.PATH_SHELL), r"_Default_Kikka2\sidebar.png"))

        self.setStyleSheet("QMenu { menu-scrollable: 1; }")
        self.setMaximumWidth(275)
        # self.createAction()

    def createAction(self):
        # icon = QIcon(r"D:\Projects\_Kikka\Kikka\Scripts\img.png")
        icon = QIcon(r"D:\Projects\Kikka\Kikka\icon.ico")
        self.addAction(QAction(icon, "Exittttttttttttttttttttttt", self._parent, triggered=self.onExit))

        # m = Menu(self._parent, '12345')
        # m.addAction(QAction(icon, "menu2", self._parent, triggered=self.onExit))
        # self.addMenu(m)

        for i in range(10):
            text = str("exit%d" % i)
            self.addAction(QAction(icon, text, self._parent, triggered=self.onExit))

        c = len(self.actions())
        self.actions()[0].setDisabled(True)

        self.actions()[3].setIcon(QIcon())
        self.actions()[3].setCheckable(True)
        self.actions()[3].setChecked(True)

        self.actions()[2].setCheckable(True)
        # self.setStyleSheet(self.sheet)

    def addItem(self, text, callbackfunc, iconfile=None):
        if iconfile != None and os.path.exists(iconfile):
            icon = QIcon(iconfile)
            self.addAction(QAction(icon, text, self._parent, triggered=callbackfunc))
        else:
            self.addAction(QAction(text, self._parent, triggered=callbackfunc))
        pass

        self._updateActionRect()
        self.resize(self.sizeHint())

    def onExit(self):
        logging.info("SystemMenu-onExit")
        from kikka import KikkaApp

        #KikkaApp.get_instance().exitApp()
        # sys.exit(0)
        pass

    def printRect(self, rect, text=''):
        s = str("rect(%d, %d, %d, %d)" % (rect.x(), rect.y(), rect.width(), rect.height()))
        logging.info("%s %s", text, s)
        return s

    def _updateActionRect(self):
        """
        void QMenuPrivate::updateActionRects(const QRect &screen) const
        https://cep.xray.aps.anl.gov/software/qt4-x11-4.8.6-browser/da/d61/class_q_menu_private.html#acf93cda3ebe88b1234dc519c5f1b0f5d
        """
        self.aRect = {}
        c = len(self.actions())
        style = self.style()
        opt = QStyleOption()
        opt.initFrom(self)
        hmargin = style.pixelMetric(QStyle.PM_MenuHMargin, opt, self)
        vmargin = style.pixelMetric(QStyle.PM_MenuVMargin, opt, self)
        icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
        fw = style.pixelMetric(QStyle.PM_MenuPanelWidth, opt, self)
        deskFw = style.pixelMetric(QStyle.PM_MenuDesktopFrameWidth, opt, self)
        tearoffHeight = style.pixelMetric(QStyle.PM_MenuTearoffHeight, opt, self) if self.isTearOffEnabled() else 0

        # dh = QApplication.desktop().screenGeometry(self).height()
        dh = self.height()
        max_column_width = 0
        tabWidth = 0
        maxIconWidth = 0
        hasCheckableItems = False
        ncols = 1
        sloppyAction = 0
        y = 0

        for i in range(len(self.actions())):
            act = self.actions()[i]
            if act.isSeparator() or act.isVisible() is False:
                continue
            hasCheckableItems |= act.isCheckable()
            ic = act.icon()
            if ic.isNull() is False:
                maxIconWidth = max(maxIconWidth, icone + 4)

        # calculate size
        qfm = self.fontMetrics()
        previousWasSeparator = True  # this is true to allow removing the leading separators
        for i in range(len(self.actions())):
            act = self.actions()[i]

            if act.isVisible() is False \
                    or (self.separatorsCollapsible() and previousWasSeparator and act.isSeparator()):
                # we continue, this action will get an empty QRect
                self.aRect[i] = QRect()
                continue

            previousWasSeparator = act.isSeparator()

            # let the style modify the above size..
            opt = QStyleOptionMenuItem()
            self.initStyleOption(opt, act)
            fm = opt.fontMetrics
            sz = QSize()
            # sz = self.sizeHint().expandedTo(self.minimumSize()).expandedTo(self.minimumSizeHint()).boundedTo(self.maximumSize())
            if act.isSeparator():
                sz = QSize(2, 2)
            else:
                s = act.text()
                if '\t' in s:
                    t = s.index('\t')
                    act.setText(s[t + 1:])
                    tabWidth = max(int(tabWidth), qfm.width(s[t + 1:]))
                else:
                    seq = act.shortcut()
                    if seq.isEmpty() is False:
                        tabWidth = max(int(tabWidth), qfm.width(seq))

                sz.setWidth(fm.boundingRect(QRect(), Qt.TextSingleLine | Qt.TextShowMnemonic, s).width())
                sz.setHeight(fm.height())

                if act.icon().isNull() == False:
                    is_sz = QSize(icone, icone)
                    if is_sz.height() > sz.height(): sz.setHeight(is_sz.height())

                sz = style.sizeFromContents(QStyle.CT_MenuItem, opt, sz, self)

            if sz.isEmpty() is False:
                max_column_width = max(max_column_width, sz.width())
                # wrapping

                if y + sz.height() + vmargin > dh - deskFw * 2:
                    ncols += 1
                    y = vmargin
                y += sz.height()
                self.aRect[i] = QRect(0, 0, sz.width(), sz.height())
        pass

        # max_column_width += tabWidth;

        # calculate position
        topmargin = 0
        leftmargin = 0
        base_y = vmargin + fw + topmargin + tearoffHeight + 0

        x = hmargin + fw + leftmargin
        y = base_y

        for i in range(len(self.actions())):
            if (self.aRect[i].isNull()):
                continue
            if y + self.aRect[i].height() > dh - deskFw * 2:
                x += max_column_width + hmargin
                y = base_y

            self.aRect[i].translate(x, y)  # move
            self.aRect[i].setWidth(max_column_width)  # uniform width

            y += self.aRect[i].height()

    def mouseMoveEvent(self, event):
        #logging.info("mouseMoveEvent")
        act = self.actionAt(event.pos())
        if act is None: return

        m = act.menu()
        if m is None:
            super().mouseMoveEvent(event)
        else:
            #self.paintEvent(event)
            super().mouseMoveEvent(event)
            self._parent.showSubMenu(act.text())
            pass


    def paintEvent(self, event):
        """
        https://cep.xray.aps.anl.gov/software/qt4-x11-4.8.6-browser/d8/d24/class_q_menu.html#a8863816ad5113a5e8b21d01e85939d76
        """

        logging.info("%s paintEvent##################################################" % self.title())
        p = QPainter(self)
        leftW = self.side.width()
        p.fillRect(0, 0, self.width(), self.height(), Qt.black)
        p.drawImage(0, self.height() - self.side.height(), self.side)
        p.drawImage(leftW, self.height() - self.bg.height(), self.bg)

        self._updateActionRect()
        style = self.style()
        actioncount = len(self.actions())

        dh = self.height()
        for i in range(actioncount):
            act = self.actions()[i]
            arect = QRect(self.aRect[i])
            if event.rect().intersects(arect) is False:
                continue

            opt = QStyleOptionMenuItem()
            self.initStyleOption(opt, act)
            opt.rect = arect
            fw = self.style().pixelMetric(QStyle.PM_MenuPanelWidth, opt, self)



            checkable = opt.checkType != QStyleOptionMenuItem.NotCheckable
            checked = opt.checked if checkable else False
            dis = not (int(opt.state) & int(QStyle.State_Enabled))
            active = int(opt.state) & int(QStyle.State_Selected)

            if opt.state & QStyle.State_Selected \
            and opt.state & QStyle.State_Enabled:
                # 被选中项
                logging.info("%s 被选中项%d: %d" % (self.title(), i, opt.menuItemType))
                irect = QRectF(arect)
                irect.moveLeft(leftW + irect.x())
                irect.setWidth(irect.width() - leftW)

                srect = QRectF(arect)
                srect.moveBottom(self.bg.height() - self.height() + srect.bottom())
                srect.setWidth(srect.width() - leftW)
                p.drawImage(irect, self.fg, srect)

                self._drawMenuItem(p, opt, arect, act.icon(), Qt.red)
            else:
                if opt.menuItemType == QStyleOptionMenuItem.Separator:
                    # 分隔线
                    logging.info("%s 分隔线%d: %d" % (self.title(), i, opt.menuItemType))
                    p.setPen(Qt.black)
                    p.drawLine(leftW, arect.y(), arect.width(), arect.y())
                if opt.menuItemType == QStyleOptionMenuItem.SubMenu:
                    # 子菜单
                    logging.info("%s 子菜单%d: %d" % (self.title(), i, opt.menuItemType))
                    pass
                    self._drawMenuItem(p, opt, arect, act.icon(), Qt.green)
                else:
                    #page_sizes = dict((n, x) for x, n in vars(QStyleOptionMenuItem).items() if isinstance(n, QStyleOptionMenuItem))
                    logging.info("%s 其他菜单项%d: %d" % (self.title(), i, opt.menuItemType))


                    # 其他菜单项
                    self._drawMenuItem(p, opt, arect, act.icon(), Qt.white)


    def _drawMenuItem(self, p, opt, arect, icon, pencolor):
        style = self.style()

        checkable = opt.checkType != QStyleOptionMenuItem.NotCheckable
        checked = opt.checked if checkable else False
        dis = not (int(opt.state) & int(QStyle.State_Enabled))
        active = int(opt.state) & int(QStyle.State_Selected)

        fw = style.pixelMetric(QStyle.PM_MenuPanelWidth, opt, self)
        leftW = self.side.width()

        p.setPen(pencolor)
        tr = QRect(arect)
        p.setFont(opt.font)
        text_flag = Qt.AlignVCenter | Qt.TextShowMnemonic | Qt.TextDontClip | Qt.TextSingleLine
        s = opt.text
        if '\t' in s:
            ss = s[s.index('\t') + 1:]
            fontwidth = opt.fontMetrics.width(ss)
            tr.moveLeft(opt.rect.right() - fontwidth)
            tr = QStyle.visualRect(opt.direction, opt.rect, tr)
            p.drawText(tr, text_flag, ss)
        tr.moveLeft(leftW + arect.x())
        tr = QStyle.visualRect(opt.direction, opt.rect, tr)
        p.drawText(tr, text_flag, s)

        # https://cep.xray.aps.anl.gov/software/qt4-x11-4.8.6-browser/df/d91/class_q_style_sheet_style.html#ab92c0e0406eae9a15bc126b67f88c110
        if opt.icon.isNull() is False:
            mode = QIcon.Disabled if dis else QIcon.Normal
            if active != 0 and not dis: mode = QIcon.Active

            # pixmap = QPixmap()
            icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
            # iconRule = QRenderRule()
            iconRect = QRectF(arect.x() - fw, arect.y(), leftW, arect.height())

            if checked:
                pixmap = icon.pixmap(QSize(icone, icone), mode, QIcon.On)
            else:
                pixmap = icon.pixmap(QSize(icone, icone), mode)

            pixw = pixmap.width()
            pixh = pixmap.height()
            pmr = QRectF(0, 0, pixw, pixh)
            pmr.moveCenter(iconRect.center())
            if checked:
                p.drawRect(QRectF(pmr.x() - 1, pmr.y() - 1, pixw + 2, pixh + 2))
            p.drawPixmap(pmr.topLeft(), pixmap)
        elif checkable:
            iconRect = QRect(0, arect.y(), leftW, arect.height())
            if checked:
                pe = QStyle.PE_IndicatorMenuCheckMark
                opt.rect = iconRect
                style.drawPrimitive(pe, opt, p, self)
        pass




