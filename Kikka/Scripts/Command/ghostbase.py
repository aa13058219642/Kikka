# coding=utf-8
import logging
import os
import time
import random
from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QRectF
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap

import kikka
from PyQt5.QtWidgets import QActionGroup
from shellwindow import ShellWindow
from dialogwindow import Dialog
from kikka_menu import MenuStyle, Menu


class GhostBase:
    def __init__(self, gid=-1, name=''):
        self.gid = gid if gid != -1 else kikka.core.newGhostID()
        self.name = name
        self.shell = None
        self.balloon = None
        self.eventlist = {}
        self.animation_list = {}

        self._shellwindows = {}
        self._dialogs = {}
        self._surfaces = {}
        self._surface_base_image = {}
        self._surface_image = {}
        self._balloon_image_cache = None
        self._shell_image = {}
        self._balloon_image = {}
        self._menus = {}
        self._menustyle = None
        self._clothes = {}

    def show(self):
        for w in self._shellwindows.values():
            w.show()

    def hide(self):
        for w in self._shellwindows.values():
            w.hide()
        for d in self._dialogs.values():
            d.hide()

    def showMenu(self, winid, pos):
        if 0 <= winid < len(self._menus) and self._menus[winid] is not None:
            self._menus[winid].setPosition(pos)
            self._menus[winid].show()
        pass

    def addWindow(self, winid, surfaceID=0):
        window = ShellWindow(self, winid)
        dialog = Dialog(self, winid)

        self._shellwindows[winid] = window
        self._dialogs[winid] = dialog
        self._surface_base_image[winid] = None
        self._surfaces[winid] = None

        if len(self._menus) == 0:
            self._menus[winid] = kikka.menu.createSystemMenu(self)

        self.setSurface(winid, surfaceID)
        if self.balloon is not None:
            dialog.setBalloon(self.balloon)

        self.updateClothesMenu(winid)

        return window

    def getShellWindow(self, winid):
        if 0 <= winid < len(self._shellwindows):
            return self._shellwindows[winid]
        else:
            return None

    def getDialog(self, winid):
        if 0 <= winid < len(self._dialogs):
            return self._dialogs[winid]
        else:
            return None

    def changeShell(self, shellID):
        self.hide()
        self.setShell(shellID)
        self.show()

    def setShell(self, shellID):
        if self.shell is not None and self.shell.id == shellID:
            return

        self.shell = kikka.shell.getShell(shellID)
        self.shell.load()
        self._menustyle = MenuStyle(self.shell.shellmenustyle)

        self._shell_image = {}
        for filename in self.shell.pnglist:
            p = os.path.join(self.shell.shellpath, filename)
            if p == self.shell.shellmenustyle.background_image \
                    or p == self.shell.shellmenustyle.foreground_image \
                    or p == self.shell.shellmenustyle.sidebar_image:
                continue
            self._shell_image[filename] = kikka.helper.getImage(p)

        for winid in self._shellwindows.keys():
            self.setSurface(winid)
            self.updateClothesMenu(winid)


    def getShell(self):
        return self.shell

    def setBalloon(self, balloowinid):
        self.balloon = kikka.balloon.getBalloon(balloowinid)
        self.balloon.load()

        for parent, dirnames, filenames in os.walk(self.balloon.balloonpath):
            for filename in filenames:
                if filename[len(filename) - 4:] == '.png':
                    p = os.path.join(self.balloon.balloonpath, filename)
                    self._balloon_image[filename] = kikka.helper.getImage(p)
        self._balloon_image_cache = self._balloon_image['background.png']

        for i in range(len(self._dialogs)):
            self._dialogs[i].setBalloon(self.balloon)
            self._dialogs[i].repaint()

    def getBalloon(self):
        return self.balloon

    def setMenu(self, winid, Menu):
        self._menus[winid] = Menu

    def getMenu(self, winid=0) -> Menu:
        if winid in self._menus:
            return self._menus[winid]
        else:
            return None

    # ###################################################################################

    def setSurface(self, wiwinid, surfaceID=-1):
        try:
            if self._surfaces[wiwinid] is not None and self._surfaces[wiwinid].ID == surfaceID:
                return

            if surfaceID == -1:
                surfaceID = self._surfaces[wiwinid].ID

            surface = self.shell.getSurface(surfaceID)
            if surface is None:
                return

            self._surfaces[wiwinid] = surface
            self.animation_list.clear()
            for aid, ani in surface.animations.items():
                self.animation_list[aid] = Animation(aid, self, ani)

            self.makeImageCache(wiwinid, surfaceID)

            # start 'runonce' and 'always' animation
            #for aid, ani in surface.animations.items():
            for aid, ani in self.animation_list.items():
                if ani.interval in ['runonce', 'always']:
                    ani.start()
                else:
                    ani.stop()

            # start bind close
            for aid in self.shell.bind:
                if aid in self.animation_list:
                    self.animation_list[aid].start()


            img = self.getShellImage(wiwinid)
            self._shellwindows[wiwinid].setImage(img)
            self._shellwindows[wiwinid].setBoxes(self.shell.getCollisionBoxes(surfaceID), self.shell.getOffset())
        except ValueError:
            logging.warning("Gohst.setSurfaces: surfaceID: %d NOT exist" % surfaceID)
        pass

    def makeImageCache(self, winid, surfaceID):
        surface = self.shell.getSurface(surfaceID)
        image_cache = QImage(500, 500, QImage.Format_ARGB32)
        painter = QPainter(image_cache)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(image_cache.rect(), Qt.transparent)

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        if len(surface.elements) > 0:
            for i, ele in surface.elements.items():
                fn = ele.filename
                if fn in self._shell_image:
                    painter.drawImage(self.shell.setting.offset + ele.offset, self._shell_image[fn])
        else:
            fn = "surface%04d.png" % surface.ID
            if fn in self._shell_image:
                painter.drawImage(self.shell.setting.offset, self._shell_image[fn])

        for aid, ani in self.animation_list.items():
            patterns = ani.getCurSurfaceData()
            for pattern in patterns:
                fid = pattern[0]
                x = pattern[1]
                y = pattern[2]
                drawtype = pattern[3]

                if ani.interval in ['bind', 'add']:
                    image_name = "surface%04d.png" % fid
                    if image_name in self._shell_image:
                        face = self._shell_image[image_name]
                        painter.drawImage(self.shell.setting.offset + QPoint(x, y), face)

        painter.end()
        # self._base_image.save("_base_image.png")
        self._surface_base_image[winid] = image_cache

    def getShellBaseImage(self, winid):
        return self._surface_base_image[winid]

    def getShellImage(self, winid):
        img = QImage(self._surface_base_image[winid])
        painter = QPainter(img)

        # draw surface and animations
        surface = self._surfaces[winid]
        runningAni = []
        for aid, ani in self.animation_list.items():
            patterns = ani.getCurSurfaceData()
            if len(patterns) > 0 and aid not in runningAni:
                runningAni.append(aid)

            for pattern in patterns:
                fid = pattern[0]
                x = pattern[1]
                y = pattern[2]
                drawtype = pattern[3]
                logging.info("aid=%d pid=%d faceid=%d xy=(%d, %d)" % (aid, ani.curPattern, fid, x, y))

                self.drawImage(img, fid, x, y, drawtype)
                #
                # image_name = "surface%04d.png" % fid
                # if image_name in self._shell_image:
                #     face = self._shell_image[image_name]
                #     painter.drawImage(self.shell.setting.offset + QPoint(x, y), face)

        # debug draw
        if kikka.shell.isDebug is True:
            painter.fillRect(QRect(0, 0, 256, 128), QColor(0, 0, 0, 64))
            painter.setPen(Qt.green)
            painter.drawRect(QRect(0, 0, img.width() - 1, img.height() - 1))
            painter.drawText(3, 12, "MainWindow")
            painter.drawText(3, 24, "Ghost: %d" % self.gid)
            painter.drawText(3, 36, "Name: %s" % self.name)
            painter.drawText(3, 48, "winid: %d" % winid)
            painter.drawText(3, 60, "surface: %d" % surface.ID)
            painter.drawText(3, 72, "bind: %s" % self.shell.bind)
            painter.drawText(3, 84, "animations: %s" % runningAni)

            for cid, col in surface.CollisionBoxes.items():
                painter.setPen(Qt.red)
                rect = QRect(col.Point1, col.Point2)
                rect.moveTopLeft(col.Point1 + self.shell.setting.offset)
                painter.drawRect(rect)
                painter.fillRect(rect, QColor(255, 255, 255, 64))
                painter.setPen(Qt.black)
                painter.drawText(rect, Qt.AlignCenter, col.tag)

        return img

    def drawImage(self, image, faceid, x, y, drawtype):
        image_name = "surface%04d.png" % faceid
        if image_name in self._shell_image:
            face = self._shell_image[image_name]

            painter = QPainter(image)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawImage(self.shell.setting.offset + QPoint(x, y), face)
            painter.end()
        pass

    def getBalloonImage(self, size: QSize, flip=False, winid=-1):
        drect = []
        # calculate destination rect
        if len(self.balloon.clipW) == 3:
            dw = [self.balloon.clipW[0],
                  size.width() - self.balloon.clipW[0] - self.balloon.clipW[2],
                  self.balloon.clipW[2]]
        elif len(self.balloon.clipW) == 5:
            sw = size.width() - self.balloon.clipW[0] - self.balloon.clipW[2] - self.balloon.clipW[4]
            dw = [self.balloon.clipW[0],
                  sw // 2,
                  self.balloon.clipW[2],
                  sw - sw // 2,
                  self.balloon.clipW[4]]
        else:
            sw = size.width() // 3
            dw = [sw, size.width() - sw*2, sw]

        if len(self.balloon.clipH) == 3:
            dh = [self.balloon.clipH[0],
                  size.height() - self.balloon.clipH[0] - self.balloon.clipH[2],
                  self.balloon.clipH[2]]
        elif len(self.balloon.clipH) == 5:
            sh = size.height() - self.balloon.clipH[0] - self.balloon.clipH[2] - self.balloon.clipH[4]
            dh = [self.balloon.clipH[0],
                  sh // 2,
                  self.balloon.clipH[2],
                  sh - sh // 2,
                  self.balloon.clipH[4]]
        else:
            sh = size.height() // 3
            dh = [sh, size.height() - sh*2, sh]

        for y in range(len(self.balloon.clipH)):
            dr = []
            for x in range(len(self.balloon.clipW)):
                pt = QPoint(0, 0)
                if x > 0: pt.setX(dr[x-1].x() + dw[x-1])
                if y > 0: pt.setY(drect[y-1][0].y() + dh[y-1])
                sz = QSize(dw[x], dh[y])
                dr.append(QRect(pt, sz))
                pass
            drect.append(dr)
        pass  # exit for

        # paint balloon image
        img = QImage(size, QImage.Format_ARGB32)
        pixmap = QPixmap().fromImage(self._balloon_image_cache, Qt.AutoColor)
        painter = QPainter(img)
        painter.setCompositionMode(QPainter.CompositionMode_Source)

        for y in range(len(self.balloon.clipH)):
            for x in range(len(self.balloon.clipW)):
                painter.drawPixmap(drect[y][x], pixmap, self.balloon.bgRect[y][x])
        painter.end()

        # flip or not
        if self.balloon.flipBackground is True and flip is True:
            img = img.mirrored(True, False)
            if self.balloon.noFlipCenter is True and len(self.balloon.clipW) == 5 and len(self.balloon.clipH) == 5:
                painter = QPainter(img)
                painter.setCompositionMode(QPainter.CompositionMode_Source)
                painter.drawPixmap(drect[2][2], pixmap, self.balloon.bgRect[2][2])
                painter.end()

        # debug draw
        if kikka.shell.isDebug is True:
            painter = QPainter(img)
            painter.fillRect(QRect(0, 0, 200, 64), QColor(0, 0, 0, 64))
            painter.setPen(Qt.red)
            for y in range(len(self.balloon.clipH)):
                for x in range(len(self.balloon.clipW)):
                    if x in (0, 2, 4) and y in (0, 2, 4):
                        continue
                    rectf = QRect(drect[y][x])
                    text = "(%d, %d)\n%d x %d" % (rectf.x(), rectf.y(), rectf.width(), rectf.height())
                    painter.drawText(rectf, Qt.AlignCenter, text)
                if y > 0:
                    painter.drawLine(drect[y][0].x(), drect[y][0].y(), drect[y][0].x() + img.width(), drect[y][0].y())

            for x in range(1, len(self.balloon.clipW)):
                painter.drawLine(drect[0][x].x(), drect[0][x].y(), drect[0][x].x(), drect[0][x].y() + img.height())

            painter.setPen(Qt.green)
            painter.drawRect(QRect(0, 0, img.width() - 1, img.height() - 1))
            painter.drawText(3, 12, "DialogWindow")
            painter.drawText(3, 24, "Ghost: %d" % self.gid)
            painter.drawText(3, 36, "Name: %s" % self.name)
            painter.drawText(3, 48, "winid: %d" % winid)
        return img

    def getMenuStyle(self):
        return self._menustyle

    def update(self, updatetime):
        isNeedUpdate = False

        # for winid, w in self._shellwindows.items():
        #     for aid, ani in self._surfaces[winid].animations.items():
        #         if ani.update(updatetime) is True:
        #             w.setImage(self.getShellImage(winid))
        #             isNeedUpdate = True

        for aid, ani in self.animation_list.items():
            if ani.update(updatetime) is True:
                isNeedUpdate = True

        return isNeedUpdate

    def repaint(self):
        for w in self._shellwindows.values():
            w.setImage(self.getShellImage(w.winid))
            w.repaint()
        for d in self._dialogs.values():
            d.repaint()

    # #####################################################################################

    def memoryRead(self, key, default, winid=0):
        key = '%s_%d_%d' % (key, self.gid, winid)
        if kikka.core.isDebug:
            value = kikka.memory.read(key, default)
        else:
            value = kikka.memory.readDeepMemory(key, default)
        return value

    def menoryWrite(self, key, value, winid=0):
        key = '%s_%d_%d' % (key, self.gid, winid)
        if kikka.core.isDebug:
            kikka.memory.write(key, value)
        else:
            kikka.memory.writeDeepMemory(key, value)
        pass

    def event_selector(self, event, tag, **kwargs):
        if 'gid' not in kwargs: kwargs['gid'] = self.gid

        e = self.getEventList()
        if event in e and tag in e[event]:
            e[event][tag](**kwargs)

    def getEventList(self):
        return self.eventlist

    def updateClothesMenu(self, winid):
        if winid not in self._menus:
            return

        clothesmenu = OrderedDict(sorted(self.shell.setting.clothesmenu.items()))
        bindgroups = self.shell.setting.bindgroups
        bindoption = self.shell.setting.bindoption

        menu = None
        for act in self._menus[winid].actions():
            if act.text() == 'Clothes':
                menu = act.menu()
                break

        if menu is None:
            return

        menu.clear()
        self._clothes.clear()
        if len(clothesmenu) == 0:
            menu.setEnabled(False)
            return

        menu.setEnabled(True)

        group = {}
        for bindgroup in bindgroups.values():
            if bindgroup.type not in group:
                group[bindgroup.type] = QActionGroup(menu.parent())
                if bindgroup.type in bindoption:
                    option = bindoption[bindgroup.type]
                    if option == 'multiple':
                        group[bindgroup.type].setExclusive(False)
                    logging.info("%s %s" % (bindgroup.type, option))

        #group1 = QActionGroup(parten)
        for v in clothesmenu.values():
            if v == -1:
                menu.addSeparator()
            elif v in bindgroups.keys():
                bindgroup = bindgroups[v]
                text = "%s - %s"%(bindgroup.type, bindgroup.title)
                act = menu.addMenuItem(text, group=group[bindgroup.type])
                callbackfunc = lambda checked, act=act, bindgroup=bindgroup: self.clickClothesMenuItem(checked, act, bindgroup)
                act.triggered.connect(callbackfunc)
                act.setCheckable(True)
                if bindgroup.type not in self._clothes.keys():
                    self._clothes[bindgroup.type] = -1

                if bindgroup.default is True and len(self.shell.bind) == 0:
                    self._clothes[bindgroup.type] = bindgroup.aID
                    act.setChecked(True)
                    #self.shell.runAnimation(bindgroup.aID)
                    self.shell.setClothes(bindgroup.aID, True)
        logging.info("bind: %s", self.shell.bind)
        pass

    def clickClothesMenuItem(self, checked, act, bindgroup):
        bindgroups = self.shell.setting.bindgroups
        bindoption = self.shell.setting.bindoption

        group = act.actionGroup()
        lastcloth = self._clothes[bindgroup.type]
        if lastcloth == bindgroup.aID:
            if (bindgroup.type in bindoption and bindoption[bindgroup.type] != 'mustselect') \
            or bindgroup.type not in bindoption:
                self._clothes[bindgroup.type] = -1
                self.shell.setClothes(bindgroup.aID, False)
                act.setChecked(not act.isChecked())
        else:
            self.shell.setClothes(lastcloth, False)
            self._clothes[bindgroup.type] = bindgroup.aID
            self.shell.setClothes(bindgroup.aID, True)

        self.repaint()
        logging.info("clickClothesMenuItem: %s %s", act.text(), act.isChecked())
        pass


class Animation:
    def __init__(self, ghost, wiwinid, animation_data):
        self._ghost = ghost
        self.ID = wiwinid
        self.data = animation_data
        self.patterns = animation_data.patterns
        self.interval = animation_data.interval
        self.intervalValue = animation_data.intervalValue
        self.exclusive = animation_data.exclusive

        self.isRuning = False
        self.updatetime = 0
        self.curPattern = -1
        self._lasttime = 0

    def start(self):
        if self.isRuning is False:
            self.isRuning = True
            self.updatetime = time.clock()
            self.curPattern = -1

    def stop(self):
        self.isRuning = False
        self.curPattern = -1

    def randomStart(self):
        isNeedStart = False
        timer_interval = kikka.core.getTimerInterval()
        if self.interval == 'never' \
                or self.interval == 'talk' \
                or self.interval == 'bind' \
                or self.interval == 'yen-e' \
                or self.interval == 'runonce':
            isNeedStart = False

        elif self.interval == 'sometimes':
            # 30% per second
            r = random.random()
            isNeedStart = True if r < 0.0003 * timer_interval else False

        elif self.interval == 'rarely':
            # 10% per second
            isNeedStart = True if random.random() < 0.0001 * timer_interval else False

        elif self.interval == 'random':
            # n% per second
            isNeedStart = True if random.random() < self.intervalValue / 100000 * timer_interval else False

        elif self.interval == 'periodic':
            now = time.clock()
            if now - self._lasttime >= self.intervalValue:
                self._lasttime = now
                isNeedStart = True
            else:
                isNeedStart = False

        elif self.interval == 'always':
            isNeedStart = True

        # start animation
        if isNeedStart is True:
            for pid, pattern in self.patterns.items():
                self.doPattern(pattern)
            self.start()

        return isNeedStart

    def doPattern(self, pattern):
        if pattern.methodType in ['alternativestart', 'start', 'insert']:
            r = random.choice(self.patterns[0].aid)
            if r in self._ghost.animation_list.keys():
                self._ghost.animation_list[r].start()
                pattern.bindAnimation = r

        elif pattern.methodType in ['alternativestop', 'stop']:
            for aid in self.patterns[0].aid:
                if aid in self._ghost.animation_list.keys():
                    self._ghost.animation_list[aid].stop()
                    pattern.bindAnimation = -1
        elif pattern.methodType == 'bind':
            self._ghost.animation_list.bind.append((pattern.surfaceID, pattern.offset[0], pattern.offset[1], pattern.methodType))
            self._ghost.drawImage(self._ghost.getShellBaseImage())

        else:
            self._ghost.repaint()
        pass

    def update(self, updatetime):
        isNeedUpdate = False
        if self.isRuning is False and self.randomStart() is True:
            isNeedUpdate = True
            return isNeedUpdate

        # updating pattern
        if self.isRuning is True:
            self.updatetime += updatetime
            if self.curPattern < len(self.patterns) - 1 \
            and self.updatetime > self.patterns[self.curPattern + 1].time:
                isNeedUpdate = True
                self.curPattern += 1
                self.updatetime -= self.patterns[self.curPattern].time

                # skip time==0 pattern
                while self.curPattern < len(self.patterns) and self.patterns[self.curPattern].time == 0:
                    #self._animationControl(self.patterns[self.curPattern])
                    self.doPattern(self.patterns[self.curPattern])
                    self.curPattern += 1
        pass  # end if

        # if run to last Pattern, stop animation
        if self.curPattern >= len(self.patterns) - 1:
            self.curPattern = len(self.patterns) - 1

            # Control Pattern stop
            if self.patterns[self.curPattern].isControlPattern() is True:
                hasBindAnimationIsRuning = False
                for pid, pattern in self.patterns.items():
                    if pattern.bindAnimation != -1 \
                    and self._ghost.animation_list[pattern.bindAnimation].isRuning is True:
                        hasBindAnimationIsRuning = True
                    else:
                        pattern.bindAnimation = -1

                if hasBindAnimationIsRuning is False and self.curPattern == len(self.patterns) - 1:
                    self.stop()
                    self.updatetime = 0
                    isNeedUpdate = True

            # stop when face id = -1
            if self.curPattern in self.patterns and self.patterns[self.curPattern].surfaceID == -1:
                self.stop()
                self.updatetime = 0
                isNeedUpdate = True

            if self.data.interval == 'always':
                self.start()
        return isNeedUpdate

    def getCurSurfaceData(self):
        result = []
        if self.curPattern in self.patterns and self.patterns[self.curPattern] != -1:
            pattern = self.patterns[self.curPattern]
            result.append((pattern.surfaceID, pattern.offset[0], pattern.offset[1], pattern.methodType))
            # for i in range(self.curPattern + 1):
            #     pattern = self.patterns[i]
            #     if pattern.isControlPattern() is False:
            #         result.append((pattern.surfaceID, pattern.offset[0], pattern.offset[1], pattern.methodType))
        return result

