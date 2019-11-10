# coding=utf-8
import logging
import os

from PyQt5.QtCore import QRect, QSize, Qt, QRectF, QPoint, QEvent
from PyQt5.QtWidgets import QMenu, QStyle, QStyleOptionMenuItem, QStyleOption, QWidget, QApplication, QActionGroup
from PyQt5.QtWidgets import QAction, QToolTip
from PyQt5.QtGui import QIcon, QImage, QPainter, QFont, QPalette, QColor, QKeySequence

import kikka


class KikkaMenu:
    _instance = None
    isDebug = False

    def __init__(self, **kwargs):
        raise SyntaxError('The class is Singletion, please use KikkaMenu.this() or kikka.menu')

    @staticmethod
    def this():
        if KikkaMenu._instance is None:
            KikkaMenu._instance = object.__new__(KikkaMenu)
            KikkaMenu._instance._init()
        return KikkaMenu._instance

    def _init(self):
        pass

    @staticmethod
    def getMenu(ghost_id, soul_id):
        ghost = kikka.core.getGhost(ghost_id)
        if ghost is not None:
            return ghost.getSoul(soul_id).getMenu()
        else:
            logging.warning('menu lost')
            return None

    @staticmethod
    def setAppMenu(menu):
        QApplication.instance().trayIcon.setContextMenu(None)
        QApplication.instance().trayIcon.setContextMenu(menu)

    @staticmethod
    def createSoulMainMenu(ghost):
        import kikka

        parent = QWidget(flags=Qt.Dialog)
        mainmenu = Menu(parent, ghost.ID, "Main")

        # shell list
        menu = Menu(mainmenu, ghost.ID, "Shells")
        group1 = QActionGroup(parent)
        for i in range(kikka.shell.getShellCount()):
            shell = kikka.shell.getShellByIndex(i)
            callbackfunc = lambda checked, name=shell.name: ghost.changeShell(name)
            act = menu.addMenuItem(shell.unicode_name, callbackfunc, None, group1)
            act.setData(shell.name)
            act.setCheckable(True)
            act.setToolTip(shell.description)
        menu.setToolTipsVisible(True)
        mainmenu.addSubMenu(menu)

        # clothes list
        menu = Menu(mainmenu, ghost.ID, "Clothes")
        menu.setEnabled(False)
        mainmenu.addSubMenu(menu)

        # balloon list
        menu = Menu(mainmenu, ghost.ID, "Balloons")
        group2 = QActionGroup(parent)
        for i in range(kikka.balloon.getBalloonCount()):
            balloon = kikka.balloon.getBalloonByIndex(i)
            callbackfunc = lambda checked, name=balloon.name: ghost.setBalloon(name)
            act = menu.addMenuItem(balloon.unicode_name, callbackfunc, None, group2)
            act.setCheckable(True)
        mainmenu.addSubMenu(menu)

        optionmenu = KikkaMenu.createOptionMenu(parent, ghost)
        mainmenu.addSubMenu(optionmenu)

        # debug option
        if kikka.core.isDebug is True:

            def callbackfunction1():
                kikka.core.isDebug = not kikka.core.isDebug
                kikka.core.repaintAllGhost()

            def callbackfunction2():
                kikka.shell.isDebug = not kikka.shell.isDebug
                kikka.core.repaintAllGhost()

            menu = Menu(mainmenu, ghost.ID, "Debug")

            act = menu.addMenuItem("Show ghost data", callbackfunction1)
            act.setCheckable(True)
            act.setChecked(kikka.core.isDebug is True)

            act = menu.addMenuItem("Show shell frame", callbackfunction2)
            act.setCheckable(True)
            act.setChecked(kikka.shell.isDebug is True)

            menu.addSubMenu(Menu(menu, ghost.ID, "TestSurface"))
            menu.addSubMenu(KikkaMenu.createTestMenu(menu))

            mainmenu.addSeparator()
            mainmenu.addSubMenu(menu)
        pass

        from kikka_app import KikkaApp
        callbackfunc = lambda: KikkaApp.this().exitApp()
        mainmenu.addSeparator()
        mainmenu.addMenuItem("Exit", callbackfunc)
        return mainmenu

    @staticmethod
    def createSoulDefaultMenu(ghost):
        import kikka

        parent = QWidget(flags=Qt.Dialog)
        mainmenu = Menu(parent, ghost.ID, "Main")

        # shell list
        menu = Menu(mainmenu, ghost.ID, "Shells")
        group1 = QActionGroup(parent)
        for i in range(kikka.shell.getShellCount()):
            shell = kikka.shell.getShellByIndex(i)
            callbackfunc = lambda checked, name=shell.name: ghost.changeShell(name)
            act = menu.addMenuItem(shell.unicode_name, callbackfunc, None, group1)
            act.setData(shell.name)
            act.setCheckable(True)
        mainmenu.addSubMenu(menu)

        # clothes list
        menu = Menu(mainmenu, ghost.ID, "Clothes")
        menu.setEnabled(False)
        mainmenu.addSubMenu(menu)

        from kikka_app import KikkaApp
        callbackfunc = lambda: KikkaApp.this().exitApp()
        mainmenu.addMenuItem("Exit", callbackfunc)

        return mainmenu

    @staticmethod
    def createOptionMenu(parent, ghost):
        optionmenu = Menu(parent, ghost.ID, "Option")

        callbackfunc1 = lambda checked: ghost.resetWindowsPosition(True, False)
        optionmenu.addMenuItem("Reset Shell Position", callbackfunc1)

        callbackfunc2 = lambda checked, g=ghost: g.setIsLockOnTaskbar(checked)
        act = optionmenu.addMenuItem("Lock on taskbar", callbackfunc2)
        act.setCheckable(True)
        act.setChecked(ghost.getIsLockOnTaskbar())

        return optionmenu

    # ###########################################################################
    @staticmethod
    def createTestMenu(parent=None):
        # test callback function
        def _test_callback(index=0, title=''):
            logging.info("MainMenu_callback: click [%d] %s" % (index, title))

        def _test_Exit(testmenu):
            from kikka_app import KikkaApp
            callbackfunc = lambda: KikkaApp.this().exitApp()
            testmenu.addMenuItem("Exit", callbackfunc)

        def _test_MenuItemState(testmenu):
            menu = Menu(testmenu, 0, "MenuItem State")
            c = 16
            for i in range(c):
                text = str("%s-item%d" % (menu.title(), i))
                callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
                act = menu.addMenuItem(text, callbackfunc)

                if i >= c / 2:
                    act.setDisabled(True)
                    act.setText("%s-disable" % act.text())
                if i % 8 >= c / 4:
                    act.setIcon(icon)
                    act.setText("%s-icon" % act.text())
                if i % 4 >= c / 8:
                    act.setCheckable(True)
                    act.setText("%s-ckeckable" % act.text())
                if i % 2 >= c / 16:
                    act.setChecked(True)
                    act.setText("%s-checked" % act.text())
            testmenu.addSubMenu(menu)

        def _test_Shortcut(testmenu):
            menu = Menu(testmenu, 0, "Shortcut")

            c = 4
            for i in range(c):
                text = str("%s-item" % (str(chr(ord('A') + i))))
                callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
                act = menu.addMenuItem(text, callbackfunc)

                if i == 0:
                    act.setShortcut(QKeySequence("Ctrl+T"))
                    act.setShortcutContext(Qt.ApplicationShortcut)
                    act.setShortcutVisibleInContextMenu(True)
            testmenu.addSubMenu(menu)
            pass

        def _test_StatusTip(testmenu):
            pass

        def _test_Separator(testmenu):
            menu = Menu(testmenu, 0, "Separator")
            menu.addSeparator()
            c = 5
            for i in range(c):
                text = str("%s-item%d" % (menu.title(), i))
                callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
                menu.addMenuItem(text, callbackfunc)
                for j in range(i + 2): menu.addSeparator()
            testmenu.addSubMenu(menu)

        def _test_MultipleItem(testmenu):
            menu = Menu(testmenu, 0, "Multiple item")
            for i in range(100):
                text = str("%s-item%d" % (menu.title(), i))
                callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
                menu.addMenuItem(text, callbackfunc)
            testmenu.addSubMenu(menu)

        def _test_LongTextItem(testmenu):
            menu = Menu(testmenu, 0, "Long text item")
            for i in range(5):
                text = str("%s-item%d " % (menu.title(), i)) * 20
                callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
                menu.addMenuItem(text, callbackfunc)
            testmenu.addSubMenu(menu)

        def _test_LargeMenu(testmenu):
            menu = Menu(testmenu, 0, "Large menu")
            for i in range(60):
                text = str("%s-item%d " % (menu.title(), i)) * 10
                callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
                menu.addMenuItem(text, callbackfunc)
                if i % 5 == 0: menu.addSeparator()
            testmenu.addSubMenu(menu)

        def _test_LimitTest(testmenu):
            menu = Menu(testmenu, 0, "LimitTest")
            _test_LargeMenu(menu)
            _test_MultipleItem(menu)
            _test_LongTextItem(menu)
            testmenu.addSubMenu(menu)

        def _test_Submenu(testmenu):
            menu = Menu(testmenu, 0, "Submenu")
            testmenu.addSubMenu(menu)

            submenu = Menu(menu, 0, "submenu1")
            menu.addSubMenu(submenu)
            m = submenu
            for i in range(8):
                next = Menu(testmenu, 0, "submenu%d" % (i + 2))
                m.addSubMenu(next)
                m = next

            submenu = Menu(menu, 0, "submenu2")
            menu.addSubMenu(submenu)
            m = submenu
            for i in range(8):
                for j in range(10):
                    text = str("%s-item%d" % (m.title(), j))
                    callbackfunc = lambda checked, a=j, b=text: _test_callback(a, b)
                    m.addMenuItem(text, callbackfunc)
                next = Menu(testmenu, 0, "submenu%d" % (i + 2))
                m.addSubMenu(next)
                m = next

            submenu = Menu(testmenu, 0, "SubMenu State")
            c = 16
            for i in range(c):
                text = str("%s-%d" % (submenu.title(), i))
                m = Menu(submenu, 0, text)
                act = submenu.addSubMenu(m)
                callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
                act.triggered.connect(callbackfunc)
                if i >= c / 2:
                    act.setDisabled(True)
                    act.setText("%s-disable" % act.text())
                if i % 8 >= c / 4:
                    act.setIcon(icon)
                    act.setText("%s-icon" % act.text())
                if i % 4 >= c / 8:
                    act.setCheckable(True)
                    act.setText("%s-ckeckable" % act.text())
                if i % 2 >= c / 16:
                    act.setChecked(True)
                    act.setText("%s-checked" % act.text())
                submenu.addSubMenu(m)
            menu.addSubMenu(submenu)

        def _test_ImageTest(testmenu):
            imagetestmenu = Menu(testmenu, 0, "ImageTest")
            testmenu.addSubMenu(imagetestmenu)

            menu = Menu(imagetestmenu, 0, "MenuImage-normal")
            for i in range(32):
                text = " " * 54
                menu.addMenuItem(text)
            imagetestmenu.addSubMenu(menu)

            menu = Menu(imagetestmenu, 0, "MenuImage-bit")
            menu.addMenuItem('')
            imagetestmenu.addSubMenu(menu)

            menu = Menu(imagetestmenu, 0, "MenuImage-small")
            for i in range(10):
                text = " " * 30
                menu.addMenuItem(text)
            imagetestmenu.addSubMenu(menu)

            menu = Menu(imagetestmenu, 0, "MenuImage-long")
            for i in range(64):
                text = " " * 54
                menu.addMenuItem(text)
            imagetestmenu.addSubMenu(menu)

            menu = Menu(imagetestmenu, 0, "MenuImage-long2")
            for i in range(32):
                text = " " * 30
                menu.addMenuItem(text)
            imagetestmenu.addSubMenu(menu)

            menu = Menu(imagetestmenu, 0, "MenuImage-large")
            for i in range(64):
                text = " " * 300
                menu.addMenuItem(text)
            imagetestmenu.addSubMenu(menu)

            menu = Menu(imagetestmenu, 0, "MenuImage-verylarge")
            for i in range(100):
                text = " " * 600
                menu.addMenuItem(text)
            imagetestmenu.addSubMenu(menu)

        if parent is None:
            parent = QWidget(flags=Qt.Dialog)
        icon = QIcon(r"icon.ico")
        menu_test = Menu(parent, 0, "TestMenu")

        _test_Exit(menu_test)
        menu_test.addSeparator()
        _test_MenuItemState(menu_test)
        _test_Shortcut(menu_test)
        _test_StatusTip(menu_test)
        _test_Separator(menu_test)
        _test_LimitTest(menu_test)
        _test_Submenu(menu_test)
        menu_test.addSeparator()
        _test_ImageTest(menu_test)
        menu_test.addSeparator()
        _test_Exit(menu_test)

        return menu_test

    @staticmethod
    def updateTestSurface(menu, ghost, curSurface=-1):
        if kikka.core.isDebug is False or menu is None:
            return

        debugmenu = None
        for act in menu.actions():
            if act.text() == 'Debug':
                debugmenu = act.menu()
                break

        if debugmenu is None:
            return

        sufacemenu = None
        for act in debugmenu.actions():
            if act.text() == 'TestSurface':
                sufacemenu = act.menu()
                break

        if sufacemenu is None:
            return

        sufacemenu.clear()
        surfacelist = ghost.getShell().getSurfaceNameList()
        group = QActionGroup(sufacemenu.parent())
        for surfaceID, item in surfacelist.items():
            callbackfunc = lambda checked, faceID=surfaceID: ghost.getSoul(0).setSurface(faceID)
            name = "%3d - %s(%s)" % (surfaceID, item[0], item[1])
            act = sufacemenu.addMenuItem(name, callbackfunc, None, group)
            act.setCheckable(True)
            if surfaceID == curSurface:
                act.setChecked(True)
        pass


class MenuStyle:
    def __init__(self, shellmenu):
        # image
        if os.path.exists(shellmenu.background_image):
            self.bg_image = QImage(shellmenu.background_image)
        else:
            self.bg_image = kikka.helper.getDefaultImage()
            logging.warning("Menu background image NOT found: %s" % shellmenu.background_image)

        if os.path.exists(shellmenu.foreground_image):
            self.fg_image = QImage(shellmenu.foreground_image)
        else:
            self.fg_image = kikka.helper.getDefaultImage()
            logging.warning("Menu foreground image NOT found: %s" % shellmenu.foreground_image)

        if os.path.exists(shellmenu.sidebar_image):
            self.side_image = QImage(shellmenu.sidebar_image)
        else:
            self.side_image = kikka.helper.getDefaultImage()
            logging.warning("Menu sidebar image NOT found: %s" % shellmenu.sidebar_image)

        # font and color
        if shellmenu.font_family != '':
            self.font = QFont(shellmenu.font_family, shellmenu.font_size)
        else:
            self.font = None

        if -1 in shellmenu.background_font_color:
            self.bg_font_color = None
        else:
            self.bg_font_color = QColor(shellmenu.background_font_color[0],
                                        shellmenu.background_font_color[1],
                                        shellmenu.background_font_color[2])

        if -1 in shellmenu.foreground_font_color:
            self.fg_font_color = None
        else:
            self.fg_font_color = QColor(shellmenu.foreground_font_color[0],
                                        shellmenu.foreground_font_color[1],
                                        shellmenu.foreground_font_color[2])

        if -1 in shellmenu.disable_font_color:
            self.disable_font_color = None
        else:
            self.disable_font_color = QColor(shellmenu.disable_font_color[0],
                                             shellmenu.disable_font_color[1],
                                             shellmenu.disable_font_color[2])

        if -1 in shellmenu.separator_color:
            self.separator_color = None
        else:
            self.separator_color = QColor(shellmenu.separator_color[0],
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
    def __init__(self, parent, gid, title=''):
        QMenu.__init__(self, title, parent)

        self.gid = gid
        self._parent = parent
        self._aRect = {}
        self._bg_image = None
        self._fg_image = None
        self._side_image = None

        self.installEventFilter(self)
        self.setMouseTracking(True)
        self.setStyleSheet("QMenu { menu-scrollable: 1; }")
        self.setSeparatorsCollapsible(False)

    def addMenuItem(self, text, callbackfunc=None, iconfilepath=None, group=None):
        if iconfilepath is None:
            act = QAction(text, self._parent)
        elif os.path.exists(iconfilepath):
            act = QAction(QIcon(iconfilepath), text, self._parent)
        else:
            logging.info("fail to add menu item")
            return

        if callbackfunc is not None:
            act.triggered.connect(callbackfunc)

        if group is None:
            self.addAction(act)
        else:
            self.addAction(group.addAction(act))

        self.confirmMenuSize(act)
        return act

    def addSubMenu(self, menu):
        act = self.addMenu(menu)
        self.confirmMenuSize(act, menu.title())
        return act

    def getSubMenu(self, menuName):
        for i in range(len(self.actions())):
            act = self.actions()[i]
            if act.text() == menuName:
                return act.menu()
        return None

    def getAction(self, actionName):
        for i in range(len(self.actions())):
            act = self.actions()[i]
            if act.text() == actionName:
                return act
        return None

    def getActionByData(self, data):
        for i in range(len(self.actions())):
            act = self.actions()[i]
            if act.data() == data:
                return act
        return None

    def checkAction(self, actionName, isChecked):
        for i in range(len(self.actions())):
            act = self.actions()[i]
            if act.text() != actionName:
                continue

            act.setChecked(isChecked)
        pass

    def confirmMenuSize(self, item, text=''):
        s = self.sizeHint()
        w, h = kikka.helper.getScreenResolution()

        if text == '': text = item.text()
        if KikkaMenu.isDebug and s.height() > h:
            logging.warning("the Menu_Height out of Screen_Height, too many menu item when add: %s" % text)
        if KikkaMenu.isDebug and s.width() > w:
            logging.warning("the Menu_Width out of Screen_Width, too menu item text too long when add: %s" % text)

    def setPosition(self, pos):
        w, h = kikka.helper.getScreenResolution()
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
        self._aRect = {}
        topmargin = 0
        leftmargin = 0
        rightmargin = 0

        # qmenu.cpp Line 259:
        # init
        max_column_width = 0
        dh = self.height()
        y = 0
        style = self.style()
        opt = QStyleOption()
        opt.initFrom(self)
        hmargin = style.pixelMetric(QStyle.PM_MenuHMargin, opt, self)
        vmargin = style.pixelMetric(QStyle.PM_MenuVMargin, opt, self)
        icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
        fw = style.pixelMetric(QStyle.PM_MenuPanelWidth, opt, self)
        deskFw = style.pixelMetric(QStyle.PM_MenuDesktopFrameWidth, opt, self)
        tearoffHeight = style.pixelMetric(QStyle.PM_MenuTearoffHeight, opt, self) if self.isTearOffEnabled() else 0

        # for compatibility now - will have to refactor this away
        tabWidth = 0
        maxIconWidth = 0
        hasCheckableItems = False
        # ncols = 1
        # sloppyAction = 0

        for i in range(len(self.actions())):
            act = self.actions()[i]
            if act.isSeparator() or act.isVisible() is False:
                continue
            # ..and some members
            hasCheckableItems |= act.isCheckable()
            ic = act.icon()
            if ic.isNull() is False:
                maxIconWidth = max(maxIconWidth, icone + 4)

        # qmenu.cpp Line 291:
        # calculate size
        qfm = self.fontMetrics()
        previousWasSeparator = True  # this is true to allow removing the leading separators
        for i in range(len(self.actions())):
            act = self.actions()[i]

            if act.isVisible() is False \
            or (self.separatorsCollapsible() and previousWasSeparator and act.isSeparator()):
                # we continue, this action will get an empty QRect
                self._aRect[i] = QRect()
                continue

            previousWasSeparator = act.isSeparator()

            # let the style modify the above size..
            opt = QStyleOptionMenuItem()
            self.initStyleOption(opt, act)
            fm = opt.fontMetrics

            sz = QSize()
            # sz = self.sizeHint().expandedTo(self.minimumSize()).expandedTo(self.minimumSizeHint()).boundedTo(self.maximumSize())
            # calc what I think the size is..
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
                        tabWidth = max(int(tabWidth), qfm.width(seq.toString()))

                sz.setWidth(fm.boundingRect(QRect(), Qt.TextSingleLine | Qt.TextShowMnemonic, s).width())
                sz.setHeight(fm.height())

                if not act.icon().isNull():
                    is_sz = QSize(icone, icone)
                    if is_sz.height() > sz.height():
                        sz.setHeight(is_sz.height())

            sz = style.sizeFromContents(QStyle.CT_MenuItem, opt, sz, self)

            if sz.isEmpty() is False:
                max_column_width = max(max_column_width, sz.width())
                # wrapping
                if y + sz.height() + vmargin > dh - deskFw * 2:
                    # ncols += 1
                    y = vmargin
                y += sz.height()
                # update the item
                self._aRect[i] = QRect(0, 0, sz.width(), sz.height())
        pass  # exit for

        max_column_width += tabWidth  # finally add in the tab width
        sfcMargin = style.sizeFromContents(QStyle.CT_Menu, opt, QApplication.globalStrut(),
                                           self).width() - QApplication.globalStrut().width()
        min_column_width = self.minimumWidth() - (sfcMargin + leftmargin + rightmargin + 2 * (fw + hmargin))
        max_column_width = max(min_column_width, max_column_width)

        # qmenu.cpp Line 259:
        # calculate position
        base_y = vmargin + fw + topmargin + tearoffHeight
        x = hmargin + fw + leftmargin
        y = base_y

        for i in range(len(self.actions())):
            if self._aRect[i].isNull():
                continue
            if y + self._aRect[i].height() > dh - deskFw * 2:
                x += max_column_width + hmargin
                y = base_y

            self._aRect[i].translate(x, y)  # move
            self._aRect[i].setWidth(max_column_width)  # uniform width
            y += self._aRect[i].height()

        # update menu size
        s = self.sizeHint()
        self.resize(s)

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
        if opt.icon.isNull() is False:  # has custom icon
            dis = not (int(opt.state) & int(QStyle.State_Enabled))
            active = int(opt.state) & int(QStyle.State_Selected)
            mode = QIcon.Disabled if dis else QIcon.Normal
            if active != 0 and not dis: mode = QIcon.Active

            fw = style.pixelMetric(QStyle.PM_MenuPanelWidth, opt, self)
            icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
            iconRect = QRectF(arect.x() - fw, arect.y(), self._side_image.width(), arect.height())
            if checked:
                pixmap = icon.pixmap(QSize(icone, icone), mode, QIcon.On)
            else:
                pixmap = icon.pixmap(QSize(icone, icone), mode)

            pixw = pixmap.width()
            pixh = pixmap.height()
            pmr = QRectF(0, 0, pixw, pixh)
            pmr.moveCenter(iconRect.center())

            if checked: p.drawRect(QRectF(pmr.x() - 1, pmr.y() - 1, pixw + 2, pixh + 2))
            p.drawPixmap(pmr.topLeft(), pixmap)

        elif checkable and checked:  # draw default checked sign
            opt.rect = QRect(0, arect.y(), self._side_image.width(), arect.height())
            opt.palette.setColor(QPalette.Text, menustyle.getPenColor(opt))
            style.drawPrimitive(QStyle.PE_IndicatorMenuCheckMark, opt, p, self)

        # Line 3604: draw emnu text
        font = menustyle.font
        if font is not None:
            p.setFont(font)
        else:
            p.setFont(opt.font)
        text_flag = Qt.AlignVCenter | Qt.TextShowMnemonic | Qt.TextDontClip | Qt.TextSingleLine

        tr = QRect(arect)
        s = opt.text
        if '\t' in s:
            ss = s[s.index('\t') + 1:]
            fontwidth = opt.fontMetrics.width(ss)
            tr.moveLeft(opt.rect.right() - fontwidth)
            tr = QStyle.visualRect(opt.direction, opt.rect, tr)
            p.drawText(tr, text_flag, ss)
        tr.moveLeft(self._side_image.width() + arect.x())
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

    def paintEvent(self, event):
        # init
        menustyle = kikka.core.getGhost(self.gid).getMenuStyle()
        self._bg_image = menustyle.bg_image
        self._fg_image = menustyle.fg_image
        self._side_image = menustyle.side_image
        self.updateActionRect()
        p = QPainter(self)

        # draw background
        p.fillRect(QRect(QPoint(), self.size()), self._side_image.pixelColor(0, 0))
        vertical = False
        y = self.height()
        while y > 0:
            yy = y - self._bg_image.height()
            p.drawImage(0, yy, self._side_image.mirrored(False, vertical))
            x = self._side_image.width()
            while x < self.width():
                p.drawImage(x, yy, self._bg_image.mirrored(False, vertical))
                x += self._bg_image.width()
                p.drawImage(x, yy, self._bg_image.mirrored(True, vertical))
                x += self._bg_image.width() + 1
            y -= self._bg_image.height()
            vertical = not vertical

        # draw item
        actioncount = len(self.actions())
        for i in range(actioncount):
            act = self.actions()[i]
            arect = QRect(self._aRect[i])
            if event.rect().intersects(arect) is False:
                continue

            opt = QStyleOptionMenuItem()
            self.initStyleOption(opt, act)
            opt.rect = arect
            if opt.state & QStyle.State_Selected \
                    and opt.state & QStyle.State_Enabled:
                # Selected Item, draw foreground image
                p.setClipping(True)
                p.setClipRect(arect.x() + self._side_image.width(), arect.y(), self.width() - self._side_image.width(),
                              arect.height())

                p.fillRect(QRect(QPoint(), self.size()), self._fg_image.pixelColor(0, 0))
                vertical = False
                y = self.height()
                while y > 0:
                    x = self._side_image.width()
                    while x < self.width():
                        yy = y - self._fg_image.height()
                        p.drawImage(x, yy, self._fg_image.mirrored(False, vertical))
                        x += self._fg_image.width()
                        p.drawImage(x, yy, self._fg_image.mirrored(True, vertical))
                        x += self._fg_image.width() + 1
                    y -= self._fg_image.height()
                    vertical = not vertical
                p.setClipping(False)

            if opt.menuItemType == QStyleOptionMenuItem.Separator:
                # Separator
                p.setPen(menustyle.getPenColor(opt))
                y = int(arect.y() + arect.height() / 2)
                p.drawLine(self._side_image.width(), y, arect.width(), y)
            else:
                # MenuItem
                self.drawControl(p, opt, arect, act.icon(), menustyle)
        pass  # exit for

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
        # logging.info("%s %d %s"%(self.title(), event.type(), text))
        if obj == self:
            if event.type() == QEvent.WindowDeactivate:
                self.Hide()
            elif event.type() == QEvent.ToolTip:
                act = self.activeAction()
                if act != 0 and act.toolTip() != act.text():
                    QToolTip.showText(event.globalPos(), act.toolTip())
                else:
                    QToolTip.hideText()
        return False
