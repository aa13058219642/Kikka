import logging
import os
import sys

from PyQt5.QtCore import QRect, QSize, Qt, QRectF, QPoint, QMargins, QEvent, QTimer
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QMenu, QStyle, QStyleOptionMenuItem, QStyleOption, QApplication, QWidget, QScrollArea, \
    QVBoxLayout, QFrame
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QImage, QPainter, QFontMetrics, QFont, QPalette, QColor, QPixmap, QMouseEvent

import kikkahelper
from shell import ShellMenu

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
        self._menustyle = None
        self._shellMenu = None
        pass

    def hide(self):

        self._menu.hide()

    def show(self):
        self._menu.show()

    def setPos(self, pos):
        self._menu.setPosition(pos)

    def addAction(self):
        pass

    def addMenu(self, parent):
        # self._menu = Menu(parent, "Main")
        # self._menu2 = Menu(self._menu, "Sub")
        # self._menu.addMenu(self._menu2)
        # self._menu3 = Menu(self._menu2, "SubSub")
        # self._menu2.addMenu(self._menu3)
        # self._menu.updateRect()
        self._testMenu()

    def setMenuStyle(self, shellmenu):
        self._menustyle = MenuStyle(shellmenu)
        pass

    def getMenuStyle(self):
        return self._menustyle

    def _testMenu(self):
        parten = QWidget(flags=Qt.Dialog)
        icon = QIcon(r"icon.ico")
        self._menu = Menu(parten, "Main")

        # menu1
        menu1 = Menu(self._menu, "ItemTest")
        c = 16
        for i in range(c):
            text = str("%s-item%d" % (menu1.title(), i))
            callbackfunc = lambda checked, a=i, b=menu1.title(): self._test_callback(a, b)
            act = menu1.addMenuItem(text, callbackfunc)

            if i >= c / 2: act.setDisabled(True); act.setText("%s-dis" % act.text())
            if i % 8 >= c / 4: act.setIcon(icon); act.setText("%s-icon" % act.text())
            if i % 4 >= c / 8: act.setCheckable(True); act.setText("%s-ckeckable" % act.text())
            if i % 2 >= c / 16: act.setChecked(True); act.setText("%s-checked" % act.text())
        self._menu.addSubMenu(menu1)

        # menu2
        menu2 = Menu(self._menu, "MenuImageTest")
        for i in range(50):
            text = " "*300
            menu2.addMenuItem(text)
        self._menu.addSubMenu(menu2)
        self._menu.addSeparator()

        # menu3
        menu3 = Menu(self._menu, "LongMenuText")
        for i in range(100):
            text = str("%s-item%d" % (menu3.title(), i))
            callbackfunc = lambda checked, a=i, b=menu3.title(): self._test_callback(a, b)
            menu3.addMenuItem(text, callbackfunc)
        self._menu.addSubMenu(menu3)
        self._menu.addSeparator()

        # menu4
        menu4 = Menu(self._menu, "SubMenuTest")
        m = menu4
        for i in range(10):
            for k in range(10):
                text = str("%s-item%d" % (m.title(), k))
                callbackfunc = lambda checked, a=k, b=m.title(): self._test_callback(a, b)
                m.addMenuItem(text, callbackfunc)
            next = Menu(self._menu, "submenu%d" % i)
            m.addSubMenu(next)
            m = next
        self._menu.addSubMenu(menu4)
        self._menu.addSeparator()

        # menu5
        menu5 = Menu(self._menu, "BigMenuTest")
        for i in range(60):
            text = str("%s-item%d " % (menu5.title(), i)) * 10
            callbackfunc = lambda checked, a=i, b=menu5.title(): self._test_callback(a, b)
            menu5.addMenuItem(text, callbackfunc)
        self._menu.addSubMenu(menu5)
        self._menu.addSeparator()

    def _test_callback(self, index=0, title=''):
        logging.info("menu_callback: click %s %d" % (title, index))


class MenuStyle:
    def __init__(self, shellmenu):
        # image
        if os.path.exists(shellmenu.background_image):
            self.bg_image = QImage(shellmenu.background_image)
        else:
            self.bg_image = kikkahelper.getDefaultImage()
            logging.warning("Menu background image NOT found: %s"%(shellmenu.background_image))

        if os.path.exists(shellmenu.foreground_image):
            self.fg_image = QImage(shellmenu.foreground_image)
        else:
            self.fg_image = kikkahelper.getDefaultImage()
            logging.warning("Menu foreground image NOT found: %s"%(shellmenu.foreground_image))

        if os.path.exists(shellmenu.sidebar_image):
            self.side_image = QImage(shellmenu.sidebar_image)
        else:
            self.side_image = kikkahelper.getDefaultImage()
            logging.warning("Menu sidebar image NOT found: %s"%(shellmenu.sidebar_image))

        # font and color
        if shellmenu.font_family != '':self.font = QFont(shellmenu.font_family, shellmenu.font_size)
        else: self.font = None

        if -1 in shellmenu.background_font_color: self.bg_font_color = None
        else: self.bg_font_color = QColor(shellmenu.background_font_color[0],
                                          shellmenu.background_font_color[1],
                                          shellmenu.background_font_color[2])

        if -1 in shellmenu.foreground_font_color: self.fg_font_color = None
        else: self.fg_font_color = QColor(shellmenu.foreground_font_color[0],
                                          shellmenu.foreground_font_color[1],
                                          shellmenu.foreground_font_color[2])

        if -1 in shellmenu.disable_font_color: self.disable_font_color = None
        else: self.disable_font_color = QColor(shellmenu.disable_font_color[0],
                                               shellmenu.disable_font_color[1],
                                               shellmenu.disable_font_color[2])

        if -1 in shellmenu.separator_color: self.separator_color = None
        else: self.separator_color = QColor(shellmenu.separator_color[0],
                                            shellmenu.separator_color[1],
                                            shellmenu.separator_color[2])

        # others
        self.hidden = shellmenu.hidden
        self.background_alignment = shellmenu.background_alignment
        self.foreground_alignment = shellmenu.foreground_alignment
        self.sidebar_alignment = shellmenu.sidebar_alignment
        pass

    def getPenColor(self, opt):
        if opt.menuItemType == QStyleOptionMenuItem.Separator:
            color = self.separator_color
        elif opt.state & QStyle.State_Selected and opt.state & QStyle.State_Enabled:
            color = self.fg_font_color
        elif not (int(opt.state) & int(QStyle.State_Enabled)):
            color = self.disable_font_color
        else:
            color = self.bg_font_color

        if color is None:
            color = opt.palette.color(QPalette.Text)
        return color


class Menu(QMenu):
    def __init__(self, parent, title=''):
        self._title = "%s(Menu)" % (title)
        QMenu.__init__(self, title, parent)
        self._parent = parent

        self.aRect = {}
        self.bg_image = None
        self.fg_image = None
        self.side_image = None

        self.installEventFilter(self)
        self.setMouseTracking(True)
        self.setStyleSheet("QMenu { menu-scrollable: 1; }")
        self.setSeparatorsCollapsible(False)

    def addMenuItem(self, text, callbackfunc=None, iconfilepath=None):
        act = None
        if iconfilepath is None: act = QAction(text, self._parent)
        elif os.path.exists(iconfilepath): act = QAction(QIcon(iconfilepath), text, self._parent)
        else: logging.info("fail to add menu item"); return

        if callbackfunc is not None: act.triggered.connect(callbackfunc)

        self.addAction(act)
        self.confirmMenuSize(act)
        return act

    def addSubMenu(self, menu):
        act = self.addMenu(menu)
        self.confirmMenuSize(act)

    def confirmMenuSize(self, item):
        s = self.sizeHint()
        w, h = kikkahelper.getScreenResolution()
        if s.height() > h: logging.warning("the Menu_Height out of Screen_Height, too many menu item when add: %s" % item.text())
        if s.width() > w: logging.warning("the Menu_Width out of Screen_Width, too menu item text too long when add: %s" % item.text())

    def eventFilter(self, obj, event):
        # text = ''
        # if event.type() == QEvent.UpdateRequest:text = 'UpdateRequest'
        # elif event.type() == QEvent.Leave:text = 'Leave'
        # elif event.type() == QEvent.Enter:text = 'Enter'
        # elif event.type() == QEvent.ToolTip:text = 'ToolTip'
        # elif event.type() == QEvent.StatusTip:text = 'StatusTip'
        # elif event.type() == QEvent.ZOrderChange:text = 'ZOrderChange'
        # elif event.type() == QEvent.Show:text = 'Show'
        # elif event.type() == QEvent.ShowToParent:text = 'ShowToParent'
        # elif event.type() == QEvent.UpdateLater:text = 'UpdateLater'
        # elif event.type() == QEvent.MouseMove:text = 'MouseMove'
        # elif event.type() == QEvent.Close:text = 'Close'
        # elif event.type() == QEvent.Hide:text = 'Hide'
        # elif event.type() == QEvent.HideToParent:text = 'HideToParent'
        # elif event.type() == QEvent.Timer:text = 'Timer'
        # elif event.type() == QEvent.Paint:text = 'Paint'
        # elif event.type() == QEvent.MouseButtonPress:
        #     text = 'MouseButtonPress(%d %d)'%(event.globalPos().x(), event.globalPos().y())
        # logging.info("%s %d %s"%(self._title, event.type(), text))
        if obj == self:
            if event.type() == QEvent.WindowDeactivate: self.Hide()
            # elif event.type() == QEvent.MouseMove: QApplication.sendEvent(self._parent, event)

        return False

    def setPosition(self, pos):
        pos = QPoint(pos)
        w, h = kikkahelper.getScreenResolution()
        if pos.y() + self.height() > h: pos.setY(h - self.height())
        if pos.y() < 0: pos.setY(0)

        if pos.x() + self.width() > w: pos.setX(w - self.width())
        if pos.x() < 0: pos.setX(0)
        self.move(pos)

    def updateActionRect(self):
        """
        void QMenuPrivate::updateActionRects(const QRect &screen) const
        https://cep.xray.aps.anl.gov/software/qt4-x11-4.8.6-browser/da/d61/class_q_menu_private.html#acf93cda3ebe88b1234dc519c5f1b0f5d
        """

        self.aRect = {}
        style = self.style()
        opt = QStyleOption()
        opt.initFrom(self)
        hmargin = style.pixelMetric(QStyle.PM_MenuHMargin, opt, self)
        vmargin = style.pixelMetric(QStyle.PM_MenuVMargin, opt, self)
        icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
        fw = style.pixelMetric(QStyle.PM_MenuPanelWidth, opt, self)
        deskFw = style.pixelMetric(QStyle.PM_MenuDesktopFrameWidth, opt, self)
        tearoffHeight = style.pixelMetric(QStyle.PM_MenuTearoffHeight, opt, self) if self.isTearOffEnabled() else 0

        dh = self.sizeHint().height()
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
            if self.aRect[i].isNull(): continue
            if y + self.aRect[i].height() > dh - deskFw * 2:
                x += max_column_width + hmargin
                y = base_y

            self.aRect[i].translate(x, y)  # move
            self.aRect[i].setWidth(max_column_width)  # uniform width

            y += self.aRect[i].height()

        s = self.sizeHint()
        self.resize(s)

    def paintEvent(self, event):
        menustyle = KikkaMenu.this().getMenuStyle()
        self.bg_image = menustyle.bg_image
        self.fg_image = menustyle.fg_image
        self.side_image = menustyle.side_image

        # init
        self.updateActionRect()
        p = QPainter(self)

        # draw background
        p.fillRect(QRect(QPoint(), self.size()), self.side_image.pixelColor(0, 0))
        vertical = False
        y = self.height()
        while y > 0:
            x = 0
            while x < self.width():
                yy = y - self.bg_image.height()
                p.drawImage(x, yy, self.side_image.mirrored(False, vertical))
                x += self.side_image.width()
                p.drawImage(x, yy, self.bg_image.mirrored(False, vertical))
                x += self.bg_image.width()
                p.drawImage(x, yy, self.bg_image.mirrored(True, vertical))
                x += self.bg_image.width() + 1
            y -= self.bg_image.height()
            vertical = not vertical

        # draw item
        actioncount = len(self.actions())
        for i in range(actioncount):
            act = self.actions()[i]
            arect = QRect(self.aRect[i])
            if event.rect().intersects(arect) is False:
                continue

            opt = QStyleOptionMenuItem()
            self.initStyleOption(opt, act)
            opt.rect = arect
            if opt.state & QStyle.State_Selected \
            and opt.state & QStyle.State_Enabled:
                # Selected Item, draw foreground image
                irect = QRectF(arect)
                irect.moveLeft(self.side_image.width() + irect.x())
                irect.setWidth(irect.width() - self.side_image.width())

                srect = QRectF(arect)
                srect.moveBottom(self.bg_image.height() - self.height() + srect.bottom())
                srect.setWidth(srect.width() - self.side_image.width())

                vertical = False
                y = self.height()
                while y > 0:
                    x = 0
                    while x < self.width():
                        p.drawImage(irect, self.fg_image.mirrored(False, vertical), srect)
                        irect.moveLeft(x - 1 + self.fg_image.width())
                        p.drawImage(irect, self.fg_image.mirrored(False, vertical), srect)
                        x += self.side_image.width() + self.fg_image.width()*2 + 1
                        irect.moveLeft(x)
                    y -= self.fg_image.height()
                    vertical = not vertical
                #p.drawImage(irect, self.fg_image, srect)

            if opt.menuItemType == QStyleOptionMenuItem.Separator:
                # Separator
                p.setPen(menustyle.getPenColor(opt))
                y = arect.y() + arect.height() / 2
                p.drawLine(self.side_image.width(), y, arect.width(), y)
            else:
                # MenuItem
                self.drawControl(p, opt, arect, act.icon(), menustyle)
                pass



    def drawControl(self, p, opt, arect, icon, menustyle):
        """
        due to overrides the "paintEvent" method, so we must repaint all menu item by self.
        luckly, we have qt source code to reference.

        void drawControl (ControlElement element, const QStyleOption *opt, QPainter *p, const QWidget *w=0) const
        https://cep.xray.aps.anl.gov/software/qt4-x11-4.8.6-browser/df/d91/class_q_style_sheet_style.html#ab92c0e0406eae9a15bc126b67f88c110
        Line 3533: element = CE_MenuItem
        """

        style = self.style()
        p.setPen(menustyle.getPenColor(opt))

        # Line 3566: draw icon and checked sign
        checkable = opt.checkType != QStyleOptionMenuItem.NotCheckable
        checked = opt.checked if checkable else False
        if opt.icon.isNull() is False: # has custom icon
            dis = not (int(opt.state) & int(QStyle.State_Enabled))
            active = int(opt.state) & int(QStyle.State_Selected)
            mode = QIcon.Disabled if dis else QIcon.Normal
            if active != 0 and not dis: mode = QIcon.Active

            fw = style.pixelMetric(QStyle.PM_MenuPanelWidth, opt, self)
            icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
            iconRect = QRectF(arect.x() - fw, arect.y(), self.side_image.width(), arect.height())
            if checked: pixmap = icon.pixmap(QSize(icone, icone), mode, QIcon.On)
            else: pixmap = icon.pixmap(QSize(icone, icone), mode)

            pixw = pixmap.width()
            pixh = pixmap.height()
            pmr = QRectF(0, 0, pixw, pixh)
            pmr.moveCenter(iconRect.center())

            if checked: p.drawRect(QRectF(pmr.x() - 1, pmr.y() - 1, pixw + 2, pixh + 2))
            p.drawPixmap(pmr.topLeft(), pixmap)

        elif checkable and checked: # draw default checked sign
            opt.rect = QRect(0, arect.y(), self.side_image.width(), arect.height())
            opt.palette.setColor(QPalette.Text, menustyle.getPenColor(opt))
            style.drawPrimitive(QStyle.PE_IndicatorMenuCheckMark, opt, p, self)

        # Line 3604: draw emnu text
        font = menustyle.font
        if font is not None: p.setFont(font)
        else: p.setFont(opt.font)

        text_flag = Qt.AlignVCenter | Qt.TextShowMnemonic | Qt.TextDontClip | Qt.TextSingleLine

        tr = QRect(arect)
        s = opt.text
        if '\t' in s:
            ss = s[s.index('\t') + 1:]
            fontwidth = opt.fontMetrics.width(ss)
            tr.moveLeft(opt.rect.right() - fontwidth)
            tr = QStyle.visualRect(opt.direction, opt.rect, tr)
            p.drawText(tr, text_flag, ss)
        tr.moveLeft(self.side_image.width() + arect.x())
        tr = QStyle.visualRect(opt.direction, opt.rect, tr)
        p.drawText(tr, text_flag, s)

        # Line 3622: draw sub menu arrow
        if opt.menuItemType == QStyleOptionMenuItem.SubMenu:
            arrowW = style.pixelMetric(QStyle.PM_IndicatorWidth, opt, self)
            arrowH = style.pixelMetric(QStyle.PM_IndicatorHeight, opt, self)
            arrowRect = QRect(0, 0, arrowW, arrowH)
            arrowRect.moveBottomRight(arect.bottomRight())
            arrow = QStyle.PE_IndicatorArrowLeft if opt.direction == Qt.RightToLeft else QStyle.PE_IndicatorArrowRight

            opt.rect = arrowRect
            opt.palette.setColor(QPalette.ButtonText, menustyle.getPenColor(opt))
            style.drawPrimitive(arrow, opt, p, self)
        pass
