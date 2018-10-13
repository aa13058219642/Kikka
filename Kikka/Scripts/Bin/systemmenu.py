
import logging
import os
import sys

from PyQt5.QtCore import QRect, QSize, Qt, QRectF, QPoint
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QMenu, QStyle, QStyleOptionMenuItem, QStyleOption, QApplication
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QImage, QPainter, QFontMetrics, QFont, QPalette, QColor, QPixmap

import Bin.kikka

class SystemMenu(QMenu):
    def __init__(self, parent):
        QMenu.__init__(self)
        self._parent = parent
        
        self.bg = QImage(os.path.join(sys.path[0],r"..\Resources\Shell\_Default_Kikka2\background.png"))
        self.fg = QImage(os.path.join(sys.path[0],r"..\Resources\Shell\_Default_Kikka2\foreground.png"))
        self.side = QImage(os.path.join(sys.path[0],r"..\Resources\Shell\_Default_Kikka2\sidebar.png"))

        self.setFixedHeight(700)

        self.sheet = """
        /*Qmenu Style Sheets*/
        QMenu {

            background-image: url(D:/Projects/Kikka/Kikka/Resources/Shell/Bunny/foreground.png);
            height: 700px
        }
  
        QMenu::item {
        background-image: url(D:/Projects/Kikka/Kikka/Resources/Shell/Bunny/background.png);
            /* sets background of menu item. set this to something non-transparent
                if you want menu color and menu item color to be different 
            background-image: url(D:/Projects/Kikka/Kikka/Resources/Shell/Bunny/background.png);

            */
        }
  
        QMenu::item:selected { 
        /* 
            background-image: url(D:/Projects/Kikka/Kikka/Resources/Shell/Bunny/background.png);
            background-color: green;
            background-color: #FFFFFF;
            border-color: #FF0000;
            
            background: rgba(100, 100, 100, 150);
            */
        }
        """

        self.setStyleSheet("QMenu { menu-scrollable: 1; }")
        #of = scroll.scrollOffset
        self.createAction()

        pri = 2

        

    def createAction(self):
        #icon = QIcon(r"D:\Projects\_Kikka\Kikka\Scripts\img.png")
        icon = QIcon(r"D:\Projects\_Kikka\Kikka\icon.ico")
        self.addAction(QAction(icon, "Exitttttttttttttttttttttttttttttt", self._parent, triggered=self.onExit))
        for i in range(10):
            text = str("exit%d"%i)
            self.addAction(QAction(icon, text, self._parent, triggered=self.onExit))

        self.actions()[0].setDisabled(True)

        self.actions()[1].setIcon(QIcon())
        self.actions()[1].setCheckable(True)
        self.actions()[1].setChecked(True)

        self.actions()[2].setCheckable(True)

        #self.setStyleSheet(self.sheet)

    def addItem(self, text, callbackfunc, iconfile=None):
        if iconfile != None and os.path.exists(iconfile):
            icon = QIcon(iconfile)
            self.addAction(QAction(icon, text, self._parent, triggered=callbackfunc))
        else:
            self.addAction(QAction(text, self._parent, triggered=callbackfunc))
        pass



    def onExit(self):
        logging.info("SystemMenu-onExit")
        Bin.kikka.KikkaApp.get_instance().exitApp()
        #sys.exit(0)
        pass

    def printRect(self, rect, text=''):
        s = str("rect(%d, %d, %d, %d)"%(rect.x(), rect.y(), rect.width(), rect.height()))
        logging.info("%s %s", text, s)
        return s

    def _updateActionRect(self):
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

        #dh = QApplication.desktop().screenGeometry(self).height()
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
        previousWasSeparator = True # this is true to allow removing the leading separators
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
                    act.setText(s[t+1:])
                    tabWidth = max(int(tabWidth), qfm.width(s[t+1:]))
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

                if y + sz.height() + vmargin > dh - deskFw *2:
                    ncols +=1
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
            if(self.aRect[i].isNull()):
                continue
            if y+self.aRect[i].height() > dh - deskFw*2:
                x += max_column_width + hmargin
                y = base_y

            self.aRect[i].translate(x, y) # move
            self.aRect[i].setWidth(max_column_width) # uniform width

            y += self.aRect[i].height()

    def paintEvent(self, e):
        """
        https://cep.xray.aps.anl.gov/software/qt4-x11-4.8.6-browser/d8/d24/class_q_menu.html#a8863816ad5113a5e8b21d01e85939d76
        """
        p = QPainter(self)
        leftW = self.side.width()
        p.fillRect(0,0,self.width(),self.height(),Qt.green)
        p.drawImage(0, self.height() - self.side.height(), self.side)
        p.drawImage(leftW, self.height() - self.bg.height(), self.bg)

        self._updateActionRect()
        style = self.style()
        actioncount = len(self.actions())

        dh = self.height()
        for i in range(actioncount):
            act = self.actions()[i]
            arect = QRect(self.aRect[i])
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
                #p.setBrush(opt.palette.brush(QPalette.Foreground))
                if i >= 26:
                    x = 1

                irect = QRectF(arect)
                irect.moveLeft(leftW + irect.x())
                irect.setWidth(irect.width() - leftW)

                srect = QRectF(arect)
                srect.moveBottom(self.bg.height() - self.height() + srect.bottom())
                srect.setWidth(srect.width() - leftW)
                p.drawImage(irect, self.fg, srect)

                p.setPen(Qt.white)
                tr = QRect(arect)
                p.setFont(opt.font)
                text_flag = Qt.AlignVCenter | Qt.TextShowMnemonic | Qt.TextDontClip | Qt.TextSingleLine
                s = opt.text
                if '\t' in s:
                    ss = s[s.index('\t')+1:]
                    fontwidth = opt.fontMetrics.width(ss)
                    tr.moveLeft(opt.rect.right() - fontwidth)
                    tr = QStyle.visualRect(opt.direction, opt.rect, tr)
                    p.drawText(tr, text_flag, ss)
                tr.moveLeft(leftW + arect.x())
                tr = QStyle.visualRect(opt.direction, opt.rect, tr)
                p.drawText(tr, text_flag, self.printRect(tr, s))
                

                # https://cep.xray.aps.anl.gov/software/qt4-x11-4.8.6-browser/df/d91/class_q_style_sheet_style.html#ab92c0e0406eae9a15bc126b67f88c110
                if opt.icon.isNull() is False:
                    mode = QIcon.Disabled if dis else QIcon.Normal
                    if active != 0 and not dis: mode = QIcon.Active

                    icon = act.icon()
                    #pixmap = QPixmap()
                    icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
                    #iconRule = QRenderRule()
                    iconRect = QRectF(arect.x() - fw, arect.y(), leftW, arect.height())

                    if checked: 
                        pixmap = act.icon().pixmap(QSize(icone, icone), mode, QIcon.On)
                    else:    
                        pixmap = act.icon().pixmap(QSize(icone, icone), mode)   

                    pixw = pixmap.width()
                    pixh = pixmap.height()
                    pmr = QRectF(0, 0, pixw, pixh)
                    pmr.moveCenter(iconRect.center())
                    if checked:
                        p.setPen(Qt.red)
                        p.setBrush(Qt.transparent)
                        p.drawRect(QRectF(pmr.x()-1, pmr.y()-1, pixw+2, pixh+2))
                    p.drawPixmap(pmr.topLeft(), pixmap)
                elif checkable:
                    iconRect = QRect(0, arect.y(), leftW, arect.height())
                    if checked:
                        pe = QStyle.PE_IndicatorMenuCheckMark
                        opt.rect = iconRect
                        style.drawPrimitive(pe,opt,p,self)


            elif opt.menuItemType == QStyleOptionMenuItem.Separator:
                # 分隔线
                p.setPen(Qt.black)
                p.drawLine(leftW, arect.y(), arect.width(), arect.y())
            elif opt.menuItemType == QStyleOptionMenuItem.SubMenu:
                # 子菜单
                pass
            else:


                # 其他菜单项
                p.setPen(opt.palette.color(QPalette.Text))
                tr = QRect(arect)
                p.setFont(opt.font)
                text_flag = Qt.AlignVCenter | Qt.TextShowMnemonic | Qt.TextDontClip | Qt.TextSingleLine
                s = opt.text
                if '\t' in s:
                    ss = s[s.index('\t')+1:]
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

                    icon = act.icon()
                    #pixmap = QPixmap()
                    icone = style.pixelMetric(QStyle.PM_SmallIconSize, opt, self)
                    #iconRule = QRenderRule()
                    iconRect = QRectF(arect.x() - fw, arect.y(), leftW, arect.height())

                    if checked: 
                        pixmap = act.icon().pixmap(QSize(icone, icone), mode, QIcon.On)
                    else:    
                        pixmap = act.icon().pixmap(QSize(icone, icone), mode)   

                    pixw = pixmap.width()
                    pixh = pixmap.height()
                    pmr = QRectF(0, 0, pixw, pixh)
                    pmr.moveCenter(iconRect.center())
                    if checked:
                        p.setPen(Qt.red)
                        p.drawRect(QRectF(pmr.x()-1, pmr.y()-1, pixw+2, pixh+2))
                    p.drawPixmap(pmr.topLeft(), pixmap)
                elif checkable:
                    iconRect = QRect(0, arect.y(), leftW, arect.height())
                    if checked:
                        pe = QStyle.PE_IndicatorMenuCheckMark
                        opt.rect = iconRect
                        style.drawPrimitive(pe,opt,p,self)

        pass