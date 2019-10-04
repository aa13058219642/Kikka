
import logging
import time
import random
from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QActionGroup

import kikka
from shellwindow import ShellWindow
from dialogwindow import DialogWindow
from kikka_const import WindowConst


class Soul:

    def __init__(self, ghost, soulid, surfaceID=0):
        self.ID = soulid
        self._ghost = ghost

        self._balloon = None
        self._menu = None
        self._menustyle = None

        self._shell_window = None
        self._dialog_window = None
        self._size = None

        self._surface = None
        self._animations = {}
        self._clothes = {}
        self._bind = []

        self._draw_offset = []
        self._base_image = None
        self._surface_image = None
        self._soul_image = None
        self._balloon_image_cache = None
        self._center_point = QPoint()
        self._base_rect = QRect()

        self.init()
        self.setSurface(surfaceID)
        self.updateClothesMenu()

    def init(self):
        self._shell_window = ShellWindow(self, self.ID)
        self._dialog_window = DialogWindow(self, self.ID)

        if self.ID == 0:
            self._menu = kikka.menu.createSoulMainMenu(self._ghost)
        else:
            self._menu = kikka.menu.createSoulDefaultMenu(self._ghost)

        if self._balloon is not None:
            self._dialog_window.setBalloon(self._balloon)

        self._size = self._shell_window.size()
        self.resetWindowsPosition(False, self._ghost.getIsLockOnTaskbar())

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
        return self._ghost

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
        shell = self._ghost.getShell()
        setting = shell.setting[self.ID]
        clothesmenu = OrderedDict(sorted(setting.clothesmenu.items()))
        bindgroups = setting.bindgroups
        bindoption = setting.bindoption

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
                    # logging.info("%s %s" % (bindgroup.type, option))
        pass

        for v in clothesmenu.values():
            if v == -1:
                menu.addSeparator()
            elif v in bindgroups.keys():
                bindgroup = bindgroups[v]
                text = "%s - %s" % (bindgroup.type, bindgroup.title)
                act = menu.addMenuItem(text, group=group[bindgroup.type])
                callbackfunc = lambda checked, act=act, bindgroup=bindgroup: self.clickClothesMenuItem(checked, act, bindgroup)
                act.triggered.connect(callbackfunc)
                act.setCheckable(True)
                if bindgroup.type not in self._clothes.keys():
                    self._clothes[bindgroup.type] = -1

                if bindgroup.default is True and len(self._ghost.getShell().getBind()) == 0:
                    self._clothes[bindgroup.type] = bindgroup.aID
                    act.setChecked(True)
                    self.setClothes(bindgroup.aID, True)
            pass
        pass

    def clickClothesMenuItem(self, checked, act, bindgroup):
        shell = self._ghost.getShell()
        setting = shell.setting[self.ID]
        bindgroups = setting.bindgroups
        bindoption = setting.bindoption

        group = act.actionGroup()
        lastcloth = self._clothes[bindgroup.type]
        if lastcloth == bindgroup.aID:
            if (bindgroup.type in bindoption and bindoption[bindgroup.type] != 'mustselect') \
            or bindgroup.type not in bindoption:
                self._clothes[bindgroup.type] = -1
                self.setClothes(bindgroup.aID, False)
                act.setChecked(not act.isChecked())
                self._ghost.saveClothBind()
        else:
            self.setClothes(lastcloth, False)
            self._clothes[bindgroup.type] = bindgroup.aID
            self.setClothes(bindgroup.aID, True)
            self._ghost.saveClothBind()

        self.setSurface(-1)
        logging.info("clickClothesMenuItem: %s %s", act.text(), act.isChecked())
        pass

    def resetAnimation(self, animations):
        self._animations.clear()
        for aid, ani in animations.items():
            self._animations[aid] = Animation(self, self.ID, ani)
            self._animations[aid].updateDrawRect()

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
            logging.warning("animation %d NOT exist!" % aid)

    def animationStop(self, aid):
        if aid in self._animations.keys():
            self._animations[aid].stop()
        else:
            logging.warning("animation %d NOT exist!" % aid)

    def setSurface(self, surfaceID=-1):
        if self._surface is not None and self._surface.ID == surfaceID:
            return

        # -1 for update surface
        if surfaceID == -1:
            surfaceID = self._surface.ID

        shell = self._ghost.getShell()
        if surfaceID in shell.alias.keys():
            surfaceID = random.choice(shell.alias[surfaceID])
        logging.info("setSurface: %d", surfaceID)
        surface = shell.getSurface(surfaceID)
        if surface is None:
            logging.warning("setSurfaces: surfaceID: %d NOT exist" % surfaceID)
            return

        self._surface = surface
        self.resetAnimation(surface.animations)
        self.updateDrawRect()
        self.repaint()
        self._shell_window.setBoxes(shell.getCollisionBoxes(surfaceID), self._draw_offset)
        pass

    def getCurrentSurface(self):
        return self._surface

    def getCurrentSurfaceID(self):
        return self._surface.ID

    def setClothes(self, aid, isEnable=True):
        self._ghost.getShell().setClothes(aid, isEnable)
        self.repaint()

    def getSize(self):
        return QSize(self._size)

    def getDrawOffset(self):
        return QPoint(self._draw_offset)

    def getCenterPoint(self):
        return QPoint(self._center_point)

    def getBaseRect(self):
        return QRect(self._base_rect)

    def resetWindowsPosition(self, usingDefaultPos=True, isLockTaskBar=True, rightOffset=0):
        shell = self._ghost.getShell()

        w, h = kikka.helper.getScreenClientRect()
        if usingDefaultPos is True:
            pos = QPoint(shell.setting[self.ID].position)
            if pos.x() == WindowConst.UNSET.x():
                pos.setX(w - self._size.width() - rightOffset)
        else:
            pos = self._shell_window.pos()

        if isLockTaskBar is True or pos.y() == WindowConst.UNSET.y():
            pos.setY(h - self._size.height())

        self._shell_window.move(pos)
        self._shell_window.saveShellRect()

    # ################################################################

    def update(self, updatetime):
        isNeedUpdate = False
        for aid, ani in self._animations.items():
            if ani.update(updatetime) is True:
                isNeedUpdate = True

        if isNeedUpdate is True:
            self.repaint()
        return isNeedUpdate

    def repaint(self):
        self.repaintBaseImage()
        self.repaintSoulImage()
        self._shell_window.setImage(self._soul_image)
        self._dialog_window.repaint()

    def getShellImage(self, faceID):
        shell_image = self._ghost.getShellImage()
        filename1 = "surface%04d.png" % faceID
        filename2 = "surface%d.png" % faceID
        if filename1 in shell_image:
            return shell_image[filename1]
        if filename2 in shell_image:
            return shell_image[filename2]
        else:
            logging.warning("Image lost: %s or %s"%(filename1, filename2))
            return kikka.helper.getDefaultImage()

    def updateDrawRect(self):
        if self._surface.ID == -1:
            self._draw_offset = self._ghost.getShell().getOffset(self.ID)
            self._size = kikka.const.WindowConst.ShellWindowDefaultSize
            self._center_point = kikka.const.WindowConst.ShellWindowDefaultCenter
            self._base_rect = QRect(self._draw_offset, self._size)
        else:
            shell_image = self._ghost.getShellImage()
            baserect = QRect()
            if len(self._surface.elements) > 0:
                for i, ele in self._surface.elements.items():
                    if ele.filename in shell_image:
                        baserect = baserect.united(QRect(ele.offset, shell_image[ele.filename].size()))
            else:
                img = self.getShellImage(self._surface.ID)
                baserect = QRect(0, 0, img.width(), img.height())

            self._base_rect = QRect(baserect)
            baserect.translate(self._ghost.getShell().getOffset(self.ID))
            rect = QRect(baserect)
            for aid, ani in self._animations.items():
                rect = rect.united(ani.rect)

            self._draw_offset = QPoint(baserect.x() - rect.x(), baserect.y() - rect.y())
            self._size = rect.size()

            if self._surface.basepos != WindowConst.UNSET:
                self._center_point = self._surface.basepos
            else:
                self._center_point = QPoint(self._size.width() / 2, self._size.height())
        pass

    def repaintBaseImage(self):
        shell_image = self._ghost.getShellImage()

        self._base_image = QImage(self._size, QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(self._base_image)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self._base_image.rect(), Qt.transparent)
        painter.end()
        del painter
        if len(self._surface.elements) > 0:
            for i, ele in self._surface.elements.items():
                if ele.filename in shell_image:
                    offset = self._draw_offset + ele.offset
                    kikka.helper.drawImage(self._base_image, shell_image[ele.filename], offset.x(), offset.y(), ele.PaintType)
        else:
            img = self.getShellImage(self._surface.ID)
            painter = QPainter(self._base_image)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawImage(self._draw_offset, img)
            painter.end()

        # self._base_image.save("_base_image.png")
        pass

    def repaintSoulImage(self):
        self._soul_image = QImage(self._base_image)
        for aid, ani in self._animations.items():
            ani.draw(self._soul_image)
        pass


class Animation:
    def __init__(self, soul, winid, animation_data):
        self._soul = soul
        self._ghost = soul.getGhost()
        self._winid = winid
        self.ID = animation_data.ID
        self.data = animation_data
        self.patterns = animation_data.patterns
        self.interval = animation_data.interval
        self.intervalValue = animation_data.intervalValue
        self.exclusive = animation_data.exclusive

        self.isRunning = False
        self.isFinish = True
        self._updatetime = 0
        self._curPattern = -1
        self._lasttime = 0

        self._image = None
        self._drawOffset = QPoint()
        self._drawType = None
        self.rect = QRect()

        if self.interval == 'runonce':
            self.start()

    def updateDrawRect(self):
        self.rect = QRect()
        for pid, p in self.patterns.items():
            if p.isControlPattern() is False and p.surfaceID != -1:
                img = self._soul.getShellImage(p.surfaceID)
                self.rect = self.rect.united(QRect(p.offset, img.size()))
        pass

    def start(self):
        if self.isRunning is False or self.isFinish is True:
            logging.debug("Animation %d start" % self.ID)

            self.isRunning = True
            self.isFinish = False
            self._updatetime = time.clock()
            self._curPattern = -1

    def stop(self):
        self.isRunning = False
        self.isFinish = True
        self._curPattern = -1
        self._image = None

    def randomStart(self):
        if self.isFinish is False:
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
            isNeedStart = True if random.random() < 0.0003 * timer_interval else False

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
            self._soul.animationStart(r)
            pattern.bindAnimation = r
        elif pattern.methodType in ['alternativestop', 'stop']:
            for aid in self.patterns[0].aid:
                self._soul.animationStop(aid)
                pattern.bindAnimation = -1
        else:
            self._image = self._soul.getShellImage(pattern.surfaceID)
            self._drawOffset = pattern.offset
            self._drawType = pattern.methodType
        pass

    def isAllBindAnimationFinish(self):
        hasControlPattern = False
        AllStop = True
        animations = self._soul.getAnimation()
        for pid, pattern in self.patterns.items():
            if pattern.isControlPattern() and pattern.bindAnimation != -1:
                hasControlPattern = True
                if animations[pattern.bindAnimation].isFinish is False:
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

        self._updatetime += updatetime
        while self._curPattern + 1 < len(self.patterns) \
        and self._updatetime > self.patterns[self._curPattern + 1].time:
            isNeedUpdate = True
            self._curPattern += 1
            pattern = self.patterns[self._curPattern]

            if pattern.surfaceID == -1:
                self._updatetime = 0
                self.stop()
                break

            self._updatetime -= pattern.time
            self.doPattern(pattern)

        if self._curPattern + 1 >= len(self.patterns):
            self.isFinish = True

        if self.isAllBindAnimationFinish() is True:
            self._updatetime = 0
            self.stop()

        return isNeedUpdate

    def draw(self, destImage):
        if self.ID in self._soul.getGhost().getShell().getBind():
            for p in self.patterns.values():
                self.doPattern(p)
                offset = self._soul.getDrawOffset() + self._drawOffset
                kikka.helper.drawImage(destImage, self._image, offset.x(), offset.y(), self._drawType)
        else:
            offset = self._soul.getDrawOffset() + self._drawOffset
            kikka.helper.drawImage(destImage, self._image, offset.x(), offset.y(), self._drawType)

        return destImage






















