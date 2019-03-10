
import logging
import os
import time
import random
from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QRectF
from PyQt5.QtGui import QImage, QPainter, QColor, QPixmap
from PyQt5.QtWidgets import QActionGroup

import kikka
from shellwindow import ShellWindow
from dialogwindow import Dialog
from kikka_menu import MenuStyle, Menu


class Soul:


    def __init__(self, ghost, id, surfaceID=0):
        self._parent = ghost
        self.ID = id

        self._shell = None
        self._balloon = None
        self._menu = None
        self._menustyle = None

        self._shell_window = None
        self._dialog_window = None

        self._surface = None
        self._animations = {}
        self._clothes = {}
        self._bind = []

        #self._shell_image = {}
        self._base_shell_image = None
        self._current_shell_image = None
        self._balloon_image_cache = None

        self.init()
        self.setSurface(surfaceID)
        self.updateClothesMenu()

    def init(self):
        self._shell_window = ShellWindow(self, self.ID)
        self._dialog_window = Dialog(self, self.ID)

        self._menu = kikka.menu.createSystemMenu(self._parent)

        if self._balloon is not None:
            self._dialog_window.setBalloon(self._balloon)

    def show(self):
        self._shell_window.show()

    def hide(self):
        self._shell_window.hide()
        self._dialog_window.hide()

    def showMenu(self, pos):
        if self._menu is not None:
            self._menu.setPosition(pos)
            self._menu.show()
        pass

    def getGhost(self):
        return self._parent

    def getShellWindow(self):
        return self._shell_window

    def getDialog(self):
        return self._dialog_window

    def setBalloon(self, balloon):
        self._dialog_window.setBalloon(balloon)
        self._dialog_window.repaint()

    def getBalloon(self):
        return self._balloon

    def setMenu(self, Menu):
        self._menu = Menu

    def getMenu(self):
        return self._menu

    def updateClothesMenu(self):
        shell = self._parent.getShell()
        clothesmenu = OrderedDict(sorted(shell.setting.clothesmenu.items()))
        bindgroups = shell.setting.bindgroups
        bindoption = shell.setting.bindoption

        menu = None
        for act in self._menu.actions():
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
        pass

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

                if bindgroup.default is True and len(self._bind) == 0:
                    self._clothes[bindgroup.type] = bindgroup.aID
                    act.setChecked(True)
                    self.setClothes(bindgroup.aID, True)
        logging.info("bind: %s", shell.bind)
        pass

    def clickClothesMenuItem(self, checked, act, bindgroup):
        shell = self._parent.getShell()
        bindgroups = shell.setting.bindgroups
        bindoption = shell.setting.bindoption

        group = act.actionGroup()
        lastcloth = self._clothes[bindgroup.type]
        if lastcloth == bindgroup.aID:
            if (bindgroup.type in bindoption and bindoption[bindgroup.type] != 'mustselect') \
            or bindgroup.type not in bindoption:
                self._clothes[bindgroup.type] = -1
                self.setClothes(bindgroup.aID, False)
                act.setChecked(not act.isChecked())
        else:
            self.setClothes(lastcloth, False)
            self._clothes[bindgroup.type] = bindgroup.aID
            self.setClothes(bindgroup.aID, True)

        #self.repaint()
        self.setSurface(-1)
        logging.info("clickClothesMenuItem: %s %s", act.text(), act.isChecked())
        pass

    def getAnimation(self):
        return self._animations

    def getRunningAnimation(self):
        runningAni = []
        for aid, ani in self._animations.items():
            if ani.isRunning is True:
                runningAni.append(aid)
        return runningAni

    def animationStart(self, aid):
        if aid in self._animations.keys():
            self._animations[aid].start()
        else:
            logging.warning("animation %d NOT exist!"%aid)

    def animationStop(self, aid):
        if aid in self._animations.keys():
            self._animations[aid].stop()
        else:
            logging.warning("animation %d NOT exist!" % aid)

    def addBind(self, aid):
        if aid not in self._bind:
            self._bind.append(aid)
            self._bind.sort()
            #self.repaintBaseSurfaceImage()

    def getBind(self):
        return self._bind

    def setSurface(self, surfaceID=-1):
        if self._surface is not None and self._surface.ID == surfaceID:
            return

        # -1 for update surface
        if surfaceID == -1:
            surfaceID = self._surface.ID

        logging.info("setSurface %d", surfaceID)

        shell = self._parent.getShell()
        surface = shell.getSurface(surfaceID)
        if surface is None:
            logging.warning("setSurfaces: surfaceID: %d NOT exist" % surfaceID)
            return

        self._surface = surface
        self.repaintBaseSurfaceImage()

        self._animations.clear()
        for aid, ani in surface.animations.items():
            self._animations[aid] = Animation(self, self.ID, ani)

        # start bind cloth
        for aid in self._bind:
            if aid in self._animations.keys():
                self._animations[aid].start()

        img = self.getShellImage()
        self._shell_window.setImage(img)
        self._shell_window.setBoxes(shell.getCollisionBoxes(surfaceID), shell.getOffset())
        pass

    def getCurrentSurface(self):
        return self._surface

    def getCurrentSurfaceID(self):
        return self._surface.ID

    def setClothes(self, aid, isEnable=True):
        self.repaintBaseSurfaceImage()
        if isEnable is True and aid not in self._bind:
            self.addBind(aid)
            self.animationStart(aid)
        elif aid in self._bind:
            self._bind.remove(aid)
            self.animationStop(aid)

    # ################################################################

    def update(self, updatetime):
        isNeedUpdate = False

        for aid, ani in self._animations.items():
            if ani.update(updatetime) is True:
                isNeedUpdate = True

        return isNeedUpdate

    def repaint(self):
        #self.repaintBaseSurfaceImage()
        self._shell_window.setImage(self.getShellImage())
        self._dialog_window.repaint()

    def drawImage(self, image, faceid, x, y, drawtype):
        if faceid == -1:
            return

        image_name = "surface%04d.png" % faceid
        shell_image = self._parent.getShellImage()
        if image_name in shell_image:
            face = shell_image[image_name]
            offset = self._parent.getShell().setting.offset
            painter = QPainter(image)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawImage(offset + QPoint(x, y), face)
            painter.end()
        pass

    def repaintBaseSurfaceImage(self):
        shell = self._parent.getShell()
        shell_image = self._parent.getShellImage()

        image_cache = QImage(kikka.const.ShellWidth, kikka.const.ShellHeight, QImage.Format_ARGB32)
        painter = QPainter(image_cache)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(image_cache.rect(), Qt.transparent)

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        if len(self._surface.elements) > 0:
            for i, ele in self._surface.elements.items():
                fn = ele.filename
                if fn in shell_image:
                    painter.drawImage(shell.setting.offset + ele.offset, shell_image[fn])
        else:
            fn = "surface%04d.png" % self._surface.ID
            if fn in shell_image:
                painter.drawImage(shell.setting.offset, shell_image[fn])

        painter.end()
        # self._base_image.save("_base_image.png")
        self._base_shell_image = image_cache
        self._current_shell_image = QImage(image_cache)

    def getShellImage(self):
        image = QImage(self._base_shell_image)
        painter = QPainter(image)
        for aid, ani in self._animations.items():
            img = ani.getImage()
            if img is not None:
                #img.save("%d.png"%aid)
                #painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                painter.drawImage(QPoint(0, 0), img)

        painter.end()
        return image


class Animation:
    def __init__(self, soul, winid, animation_data):
        self._parent = soul
        self._winid = winid
        self.ID = animation_data.ID
        self.data = animation_data
        self.patterns = animation_data.patterns
        self.interval = animation_data.interval
        self.intervalValue = animation_data.intervalValue
        self.exclusive = animation_data.exclusive

        self.isRunning = False
        self.updatetime = 0
        self.curPattern = -1
        self._lasttime = 0
        self._image = None

        if self.interval == 'runonce':
            self.start()

    def start(self):
        if self.isRunning is False:
            logging.debug("Animation %d start"%(self.ID))

            self.isRunning = True
            self.updatetime = time.clock()
            self.curPattern = -1

            self._image = QImage(kikka.const.ShellWidth, kikka.const.ShellHeight, QImage.Format_ARGB32)
            painter = QPainter(self._image)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.fillRect(self._image.rect(), Qt.transparent)
            painter.end()

    def stop(self):
        self.isRunning = False
        self.curPattern = -1
        self._image = None

    def randomStart(self):
        if self.isRunning is True:
            return False

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

        return isNeedStart

    def doPattern(self, pattern):
        logging.debug("aid:%d %s doPattern %d %s", self.ID, self.interval, pattern.ID, pattern.methodType)

        if pattern.methodType in ['alternativestart', 'start', 'insert']:
            r = random.choice(self.patterns[0].aid)
            self._parent.animationStart(r)
            pattern.bindAnimation = r
        elif pattern.methodType in ['alternativestop', 'stop']:
            for aid in self.patterns[0].aid:
                self._parent.animationStop(aid)
                pattern.bindAnimation = -1
        else:
            self._parent.drawImage(self._image, pattern.surfaceID, pattern.offset[0], pattern.offset[1], pattern.methodType)
        pass

    def isAllBindAnimationStop(self):
        hasControlPattern = False
        AllStop = True
        animations = self._parent.getAnimation()
        for pid, pattern in self.patterns.items():
            if pattern.isControlPattern() and pattern.bindAnimation != -1:
                hasControlPattern = True
                if animations[pattern.bindAnimation].isRunning is True:
                    AllStop = False
                    break
                else:
                    pattern.bindAnimation = -1

        return True if hasControlPattern is True and AllStop is True else False

    def update(self, updatetime):
        isNeedUpdate = False
        if self.randomStart() is True:
            self.start()
            isNeedUpdate = True

        if self.isRunning is False:
            return isNeedUpdate

        self.updatetime += updatetime
        while self.curPattern + 1 < len(self.patterns) \
        and self.updatetime > self.patterns[self.curPattern + 1].time:
            isNeedUpdate = True
            self.curPattern += 1
            pattern = self.patterns[self.curPattern]

            if pattern.surfaceID == -1:
                self.updatetime = 0
                self.stop()
                break

            self.updatetime -= pattern.time
            self.doPattern(pattern)


        if self.isAllBindAnimationStop() is True:
            self.updatetime = 0
            self.stop()

        return isNeedUpdate

    def getImage(self):
        img = self._image if self.isRunning is True else None
        return img
























