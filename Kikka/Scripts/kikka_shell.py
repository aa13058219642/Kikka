# coding=utf-8
import os
import re
import logging
import random
import time
from enum import Enum

from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QImage, QPainter, QColor

import kikkahelper
import kikka


class KikkaShell:
    _instance = None

    def __init__(self, **kwargs):
        raise SyntaxError('The class is Singletion, please use ShellManager.this() or kikka.shell_manager')

    @staticmethod
    def this():
        if KikkaShell._instance is None:
            KikkaShell._instance = object.__new__(KikkaShell)
            KikkaShell._instance._init()
        return KikkaShell._instance

    def _init(self):
        self.shells = []
        self.isNeedUpdate = True
        self.shelldir = ''
        self.curShell = 0

    def loadShell(self, shellpath):
        shell = Shell(shellpath)
        if shell.isInitialized is False:
            return

        isExist = False
        for s in self.shells:
            if shell.id == s.id and shell.name == s.name:
                isExist = True
                break

        if not isExist:
            logging.info("scan shell: %s", shell.name)
            self.shells.append(shell)
        pass

    def loadAllShell(self, shelldir):
        self.shelldir = shelldir

        for parent, dirnames, filenames in os.walk(shelldir):
            for dirname in dirnames:
                shellpath = os.path.join(parent, dirname)
                self.loadShell(shellpath)

        logging.info("shell count: %d", len(self.shells))
        self.setCurShell(int(kikka.memory.getInteger('CurShell', 0)))

    def getCurShell(self):

        return self.shells[self.curShell]

    def update(self, updatetime):
        shell = self.getCurShell()
        return shell.update(updatetime)

    def getCurImage(self, isDebug=False):
        shell = self.getCurShell()
        return shell.getCurImage(isDebug)

    def getCollisionBoxes(self):
        shell = self.getCurShell()
        return shell.getCollisionBoxes()

    def setCurShell(self, index):
        if 0 <= index < len(self.shells):
            self.curShell = index
            kikka.menu.setMenuStyle(self.getCurShell().getShellMenuStyle())
            kikka.memory.set('CurShell', index, True)
        else:
            logging.warning("setCurShell: index NOT in shells list")


class Shell:
    def __init__(self, shellpath):
        self.name = ''
        self.id = ''
        self.type = ''
        self.author = AuthorInfo()

        self.shellmenustyle = ShellMenuStyle()
        self.setting = ShellSetting()

        self._pngs = {}
        self.shellpath = shellpath  # root path of this shell
        self.surfaces = {}
        self.isInitialized = False
        self.isLoaded = False
        self._updatetime = 0
        self._CurfaceID = 0

        # path check
        if os.path.exists(shellpath):
            descript_path = os.path.join(self.shellpath, 'descript.txt')
            if not os.path.exists(descript_path): return
            descript_map = self._open_descript(descript_path)
            self._load_descript(descript_map)
            self._loadPNGindex()
            self.isInitialized = True

        pass

    def clearShell(self):
        self._pngs = {}
        self.surfaces = {}
        self.isLoaded = False

    def loadShell(self):
        if self.isLoaded is False:
            logging.info("load shell: %s", self.name)

            self._load_surfaces()

            # load PNG
            for filename, _ in self._pngs.items():
                p = os.path.join(self.shellpath, filename)
                if p == self.shellmenustyle.background_image \
                        or p == self.shellmenustyle.foreground_image \
                        or p == self.shellmenustyle.sidebar_image:
                    continue
                self._pngs[filename] = QImage(p)

            self.isLoaded = True
        pass

    def _loadPNGindex(self):
        for parent, dirnames, filenames in os.walk(self.shellpath):
            for filename in filenames:
                a = filename[len(filename) - 4:]
                if filename[len(filename) - 4:] == '.png':
                    self._pngs[filename] = None
        pass

    def _open_descript(self, descript_path):
        map = {}
        charset = kikkahelper.checkEncoding(descript_path)

        f = open(descript_path, 'r', encoding=charset)
        for line in f:
            line = line.replace("\n", "").replace("\r", "")
            line = line.strip(' ')

            if line == '': continue
            if line.find('\\') == 0: continue
            if line.find('//') == 0: continue
            if line.find('#') == 0: continue

            index = line.index(',')

            key = line[0:index]
            value = line[index + 1:]

            map[key] = value
        return map

    def _open_surfaces(self, surfaces_path):
        map = {}
        surfaceID = []
        is_load_key = True
        charset = kikkahelper.checkEncoding(surfaces_path)

        f = open(surfaces_path, 'r', encoding=charset)
        for line in f:
            line = line.replace("\n", "").replace("\r", "")
            line = line.strip(' ')

            if line == '': continue
            if line.find('\\') == 0: continue
            if line.find('//') == 0: continue
            if line.find('#') == 0: continue

            if line == '{': is_load_key = False; continue
            if line == '}': is_load_key = True; surfaceID = []; continue

            if is_load_key is False:
                # set value
                for id in surfaceID:
                    map[id].append(line)
            else:
                # set ID
                if 'descript' in line or 'alias' in line: continue

                str = line
                keys = str.replace('surface', '').replace(' ', '').split(',')
                for key in keys:
                    if key == '': continue
                    if key[0] == '!':
                        # remove ID
                        key = key[1:]
                        if '-' in key:
                            v = key.split('-')
                            a = int(v[0])
                            b = int(v[1])
                            for id in range(a, b):
                                if id in map:
                                    surfaceID.remove(id)
                                    map.pop(id)
                        else:
                            id = int(key)
                            surfaceID.remove(id)
                            map.pop(id)
                    else:
                        # add ID
                        if '-' in key:
                            v = key.split('-')
                            a = int(v[0])
                            b = int(v[1])
                            for id in range(a, b):
                                if id not in map:
                                    surfaceID.append(id)
                                    map[id] = []
                        else:
                            id = int(key)
                            if id not in map:
                                surfaceID.append(id)
                                map[id] = []
        pass  # exit for
        f.close()
        return map

    def _load_descript(self, map):
        for keys, values in map.items():
            key = keys.split('.')
            value = values.split(',')

            if key[0] == 'menu':
                if len(key) == 1:
                    self.shellmenustyle.hidden = True
                elif key[1] == 'font':
                    if key[2] == 'name':
                        self.shellmenustyle.font_family = value[0]
                    elif key[2] == 'height':
                        self.shellmenustyle.font_size = int(value[0])
                    else:
                        self._IgnoreParams(keys, values)
                elif key[1] == 'background':
                    if key[2] == 'font' and key[3] == 'color':
                        if key[4] == 'r':
                            self.shellmenustyle.background_font_color[0] = int(value[0])
                        elif key[4] == 'g':
                            self.shellmenustyle.background_font_color[1] = int(value[0])
                        elif key[4] == 'b':
                            self.shellmenustyle.background_font_color[2] = int(value[0])
                        else:
                            self._IgnoreParams(keys, values)
                    elif key[2] == 'bitmap' and key[3] == 'filename':
                        self.shellmenustyle.background_image = os.path.join(self.shellpath, value[0])
                    elif key[2] == 'alignment':
                        self.shellmenustyle.background_alignment = value[0]
                    else:
                        self._IgnoreParams(keys, values)
                elif key[1] == 'foreground':
                    if key[2] == 'font' and key[3] == 'color':
                        if key[4] == 'r':
                            self.shellmenustyle.foreground_font_color[0] = int(value[0])
                        elif key[4] == 'g':
                            self.shellmenustyle.foreground_font_color[1] = int(value[0])
                        elif key[4] == 'b':
                            self.shellmenustyle.foreground_font_color[2] = int(value[0])
                        else:
                            self._IgnoreParams(keys, values)
                    elif key[2] == 'bitmap' and key[3] == 'filename':
                        self.shellmenustyle.foreground_image = os.path.join(self.shellpath, value[0])
                    elif key[2] == 'alignment':
                        self.shellmenustyle.foreground_alignment = value[0]
                    else:
                        self._IgnoreParams(keys, values)
                elif key[1] == 'disable':
                    if key[2] == 'font' and key[3] == 'color':
                        if key[4] == 'r':
                            self.shellmenustyle.disable_font_color[0] = int(value[0])
                        elif key[4] == 'g':
                            self.shellmenustyle.disable_font_color[1] = int(value[0])
                        elif key[4] == 'b':
                            self.shellmenustyle.disable_font_color[2] = int(value[0])
                        else:
                            self._IgnoreParams(keys, values)
                elif key[1] == 'separator':
                    if key[2] == 'color':
                        if key[3] == 'r':
                            self.shellmenustyle.separator_color[0] = int(value[0])
                        elif key[3] == 'g':
                            self.shellmenustyle.separator_color[1] = int(value[0])
                        elif key[3] == 'b':
                            self.shellmenustyle.separator_color[2] = int(value[0])
                        else:
                            self._IgnoreParams(keys, values)
                elif key[1] == 'sidebar':
                    if key[2] == 'bitmap' and key[3] == 'filename':
                        self.shellmenustyle.sidebar_image = os.path.join(self.shellpath, value[0])
                    elif key[2] == 'alignment':
                        self.shellmenustyle.sidebar_alignment = value[0]
                    else:
                        self._IgnoreParams(keys, values)
                else:
                    self._IgnoreParams(keys, values)

            elif key[0] == 'sakura':
                if 'bindgroup' in key[1]:
                    aid = int(key[1][9:])
                    if key[2] == 'name':
                        img = '' if len(value) < 3 else value[2]
                        self.setting.bindgroups[aid] = BindGroup(aid, value[0], value[1], img)
                    elif key[2] == 'default':
                        self.setting.bindgroups[aid].setDefault(value[0])
                    else:
                        self._IgnoreParams(keys, values)
                elif 'menuitem' in key[1]:
                    mid = int(key[1][8:])
                    if value[0] != '-':
                        self.shellmenustyle.menuitem[mid] = int(value[0])
                    else:
                        self.shellmenustyle.menuitem[mid] = -1
                elif key[1] == 'balloon':
                    if key[2] == 'offsetx':
                        self.setting.balloon_offset[0] = int(value[0])
                    elif key[2] == 'offsety':
                        self.setting.balloon_offset[1] = int(value[0])
                    elif key[2] == 'alignment':
                        self.setting.balloon_alignment = value[0]
                    else:
                        self._IgnoreParams(keys, values)
                elif 'bindoption' in key[1]:
                    gid = int(key[1][10:])
                    if key[2] == 'group':
                        self.setting.bindoption[value[0]] = value[1]
                    else:
                        self._IgnoreParams(keys, values)
                else:
                    self._IgnoreParams(keys, values)

            elif key[0] == 'id':
                self.id = value[0]
            elif key[0] == 'name':
                self.name = value[0]
            elif key[0] == 'type':
                self.type = value[0]
            elif key[0] == 'craftman' or key[0] == 'craftmanw':
                self.author.name = value[0]
            elif key[0] == 'crafmanurl':
                self.author.webside = value[0]
            elif key[0] == 'homeurl':
                self.author.updateurl = value[0]
            elif key[0] == 'readme':
                self.author.readme = value[0]

            # skip params
            elif key[0] == 'charset' \
                    or key[0] == 'kero' \
                    or key[0:4] == 'char' \
                    or key[0] == 'shiori' \
                    or key[0] == 'mode' \
                    or key[0] == 'seriko':
                # self._IgnoreParams(keys, values)
                pass

            # unknow params
            else:
                self._IgnoreParams(keys, values)
        pass

    def _load_surfaces(self):
        surfaces_path = os.path.join(self.shellpath, 'surfaces.txt')
        if not os.path.exists(surfaces_path): return
        surfaces_map = self._open_surfaces(surfaces_path)

        i = 2
        while 1:
            surfaces_path = os.path.join(self.shellpath, 'surfaces%d.txt' % i)
            if not os.path.exists(surfaces_path): break
            surfaces_map = self._open_surfaces(surfaces_path)
            i = i + 1

        for key, values in surfaces_map.items():
            self.surfaces[key] = Surface(key, values)

    def _IgnoreParams(self, key, values):
        print('unknow shell params: %s,%s' % (key, values))
        pass

    def setSurfaces(self, surfacesID):
        if self.isLoaded is False:
            self.loadShell()

        if surfacesID in self.surfaces:
            old = self._CurfaceID
            self._CurfaceID = surfacesID
            surface = self.surfaces[surfacesID]

            base_image_name = "surface%04d.png" % surfacesID if 0 not in surface.elements else surface.elements[
                0].filename

            if base_image_name in self._pngs:
                self._base_image = self._pngs[base_image_name]
            else:
                logging.warning("Shell.setSurfaces: png %s NOT found!" % base_image_name)
                self.setSurfaces(old)
        else:
            logging.warning("Shell.setSurfaces: surfaceID: %d NOT exist" % surfacesID)
            self.setSurfaces(0)

    def _getSurfacePath(self, surfacesID):

        return os.path.join(self.shellpath, "surface%04d.png" % surfacesID)

    def update(self, updatetime):
        isNeedUpdate = False
        self._updatetime += updatetime

        surface = self.surfaces[self._CurfaceID]
        for aid, ani in surface.animations.items():
            ret = ani.update(updatetime)
            if ret is True:
                isNeedUpdate = True

        return isNeedUpdate

    def getCurImage(self, isDebug=False):
        img = QImage(self._base_image)
        painter = QPainter(img)

        surface = self.surfaces[self._CurfaceID]
        for aid, ani in surface.animations.items():
            id, x, y = ani.getCurSurfaceData()
            if id == -1: continue

            face = QImage(self._getSurfacePath(id))
            painter.drawImage(QPoint(x, y), face)

        if isDebug is True:
            # logging.info("debug draw")
            for cid, col in surface.CollisionBoxes.items():
                painter.setPen(Qt.red)
                rect = QRect(QPoint(col.Point1[0], col.Point1[1]), QPoint(col.Point2[0], col.Point2[1]))
                painter.drawRect(rect)
                painter.fillRect(rect, QColor(255, 255, 255, 64))
                painter.setPen(Qt.black)
                painter.drawText(rect, Qt.AlignCenter, col.tag)

        return img

    def getCollisionBoxes(self):
        surface = self.surfaces[self._CurfaceID]
        return surface.CollisionBoxes

    def getShellMenuStyle(self):
        return self.shellmenustyle


class Animation:
    def __init__(self, id, parent):
        self._parent = parent
        self.ID = id
        self.interval = 'never'
        self.intervalValue = 0
        self.exclusive = False
        self.patterns = {}

        self.isRuning = False
        self.updatetime = 0
        self.curPattern = -1
        self._lasttime = 0

    def start(self):
        if self.isRuning is False:
            self.isRuning = True
            self.updatetime = 0
            self.curPattern = -1

    def stop(self):
        self.isRuning = False

    def randomSatrt(self):
        if self.interval == 'never' \
                or self.interval == 'talk' \
                or self.interval == 'bind' \
                or self.interval == 'yen-e' \
                or self.interval == 'runonce':
            return False

        elif self.interval == 'sometimes':
            # 30% per second = 0.3 / 1000
            return True if random.random() < 0.0003 else False

        elif self.interval == 'rarely':
            # 10% per second = 0.1 / 1000
            return True if random.random() < 0.0001 else False

        elif self.interval == 'random':
            # n% per second = n / 1000
            return True if random.random() < self.intervalValue / 1000 else False

        elif self.interval == 'periodic':
            now = time.clock()
            if now - self._lasttime >= self.intervalValue:
                self._lasttime = now
                return True
            else:
                return False

        elif self.interval == 'always':
            return True

        pass

    def _animationControl(self):

        for pid, pattern in self.patterns.items():
            m_type = self.patterns[0].methodType
            if m_type == 'alternativestart' \
                    or m_type == 'start' \
                    or m_type == 'insert':
                r = random.choice(self.patterns[0].aid)
                if r in self._parent: self._parent[r].start()
            elif m_type == 'alternativestop' \
                    or m_type == 'stop':
                for aid in self.patterns[0].aid:
                    if aid in self._parent: self._parent[aid].stop()

    def update(self, updatetime):
        isNeedUpdate = False

        if self.isRuning is False:
            if self.randomSatrt() is True:
                # self._animationControl()
                self.isRuning = True
                isNeedUpdate = True

            elif self._lasttime == 0 and self.interval == 'runonce':
                self._lasttime = time.clock()
                self.isRuning = True
                isNeedUpdate = True

            return isNeedUpdate

        self.updatetime += updatetime
        if self.updatetime > self.patterns[self.curPattern + 1].time:
            self.curPattern += 1
            while self.patterns[self.curPattern].time == 0:
                m_type = self.patterns[self.curPattern].methodType
                if m_type == 'alternativestart' \
                        or m_type == 'start' \
                        or m_type == 'insert':
                    r = random.choice(self.patterns[0].aid)
                    if r in self._parent: self._parent[r].start()
                elif m_type == 'alternativestop' \
                        or m_type == 'stop':
                    for aid in self.patterns[0].aid:
                        if aid in self._parent: self._parent[aid].stop()

                self.curPattern += 1
                if self.curPattern >= len(self.patterns) - 1:
                    self.curPattern = -1
                    self.updatetime = 0
                    self.isRuning = False
                    isNeedUpdate = True
                    return isNeedUpdate
            self.updatetime -= self.patterns[self.curPattern].time
            isNeedUpdate = True

        if self.curPattern >= len(self.patterns) - 1:
            self.curPattern = -1
            self.updatetime = 0
            self.isRuning = False
            isNeedUpdate = True
        return isNeedUpdate

    def getCurSurfaceData(self):
        if self.isRuning is False or self.curPattern == -1:
            return -1, 0, 0

        pattern = self.patterns[self.curPattern]
        return pattern.surfaceID, pattern.offset[0], pattern.offset[1]


class EPatternType(Enum):
    Normal = 0
    New = 1
    Alternative = 2


class Pattern:
    def __init__(self, params, matchtype=EPatternType.Normal):
        if matchtype == EPatternType.Normal:
            self.ID = int(params[1])
            self.methodType = params[4]
            self.surfaceID = int(params[2])
            self.time = int(params[3]) * 10
            self.offset = [int(params[5]), int(params[6])]
            self.aid = [-1]
        elif matchtype == EPatternType.New:
            self.ID = int(params[1])
            self.methodType = params[2]
            self.surfaceID = int(params[3])
            self.time = int(params[4])
            self.offset = [int(params[5]), int(params[6])]
            self.aid = [-1]
        elif matchtype == EPatternType.Alternative:
            self.ID = int(params[1])
            self.methodType = params[4]
            self.surfaceID = int(params[2])
            self.time = int(params[3])
            self.offset = [0, 0]
            if '.' in params[5]:
                self.aid = list(map(int, params[5].split('.')))
            elif ',' in params[5]:
                self.aid = list(map(int, params[5].split(',')))
            else:
                self.aid = [int(params[5])]

    pass


class Element:
    def __init__(self, params):
        self.ID = int(params[0])
        self.PaintType = params[1]
        self.filename = params[2]
        self.offset = [int(params[3]), int(params[4])]


class CollisionBox:
    def __init__(self, params):
        self.ID = int(params[0])
        self.Point1 = [int(params[1]), int(params[2])]
        self.Point2 = [int(params[3]), int(params[4])]
        self.tag = params[5]


class SurfaceMatchLine(Enum):
    Unknow = 0
    Elements = 100

    AnimationInterval = 200
    AnimationPattern = 201
    AnimationPatternNew = 202
    AnimationPatternAlternative = 203
    AnimationOptionExclusive = 204

    CollisionBoxes = 300

    OffectPointX = 401
    OffectPointY = 402
    OffectKinokoPointX = 403
    OffectKinokoPointY = 404

    @staticmethod
    def matchLine(line):

        # Element
        # element[ID],[PaintType],[filename],[X],[Y]
        res = re.match(
            r'^element(\d+),(base|overlay|overlayfast|replace|interpolate|asis|move|bind|add|reduce|insert),(\w+.png),(\d+),(\d+)$',
            line)
        if res is not None: return SurfaceMatchLine.Elements, res.groups()

        # Animation Interval
        # [aID]interval,[interval]
        res = re.match(
            r'^(?:animation)?(\d+).?interval,(sometimes|rarely|random,\d+|periodic,\d+[.][0-9]*|always|runonce|never|yen-e|talk,\d+|bind)$',
            line)
        if res is not None: return SurfaceMatchLine.AnimationInterval, res.groups()

        # Animation Pattern Alternative
        # [aID]pattern[pID],[surfaceID],[time],[methodType],[[aID1], [aID2], ...]
        res = re.match(
            r'^(\d+)pattern(\d+),(\-?\d+),(\d+),(insert|start|stop|alternativestart|alternativestop),(?:[\[\(]?((?:\d+[\.\,])*\d+)[\]\)]?)$',
            line)
        if res is not None: return SurfaceMatchLine.AnimationPatternAlternative, res.groups()

        # Animation Pattern Normal
        # [aID]pattern[pID],[surfaceID],[time],[methodType],[X],[Y]
        res = re.match(
            r'^(\d+)pattern(\d+),(\-?\d+),(\d+),(base|overlay|overlayfast|replace|interpolate|asis|move|bind|add|reduce),(\-?\d+),(\-?\d+)$',
            line)
        if res is not None: return SurfaceMatchLine.AnimationPattern, res.groups()

        # Animation Pattern New
        # animation[aID].pattern[pID],[methodType],[surfaceID],[time],[X],[Y]
        res = re.match(
            r'^animation(\d+).pattern(\d+),(base|overlay|overlayfast|replace|interpolate|asis|move|bind|add|reduce),(\-?\d+),(\d+),(\-?\d+),(\-?\d+)$',
            line)
        if res is not None: return SurfaceMatchLine.AnimationPatternNew, res.groups()

        # Animation Option exclusive
        # [aID]option,exclusive
        res = re.match(r'^(\d+)option,exclusive$', line)
        if res is not None: return SurfaceMatchLine.AnimationOptionExclusive, res.groups()

        # CollisionBox
        # Collision[cID],[sX],[sY],[eX],[eY],[Tag]
        res = re.match(r'^collision(\d+),(\d+),(\d+),(\d+),(\d+),(\w+)$', line)
        if res is not None: return SurfaceMatchLine.CollisionBoxes, res.groups()

        # Offect PointX
        # point.centerx,[int] | point.basepos.centerx,[int]
        res = re.match(r'^point(?:.basepos)?.centerx,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.OffectPointX, res.groups()

        # Offect PointY
        # point.centery,[int] | point.basepos.centery,[int]
        res = re.match(r'^point(?:.basepos)?.centery,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.OffectPointY, res.groups()

        # Kinoko Offect PointX
        # point.kinoko.centerx,[int]
        res = re.match(r'^point.kinoko.centerx,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.OffectKinokoPointX, res.groups()

        # Kinoko Offect PointY
        # point.kinoko.centery,[int]
        res = re.match(r'^point.kinoko.centery,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.OffectKinokoPointY, res.groups()

        # Unknow
        return SurfaceMatchLine.Unknow, None

    pass


class AuthorInfo:
    def __init__(self):
        self.name = ''
        self.webside = ''
        self.updateurl = ''
        self.readme = ''


class ShellMenuStyle:
    def __init__(self):
        self.hidden = False
        self.menuitem = {}

        self.font_family = ''
        self.font_size = -1

        self.background_image = ''
        self.background_font_color = [-1, -1, -1]
        self.background_alignment = 'lefttop'

        self.foreground_image = ''
        self.foreground_font_color = [-1, -1, -1]
        self.foreground_alignment = 'lefttop'

        self.disable_font_color = [-1, -1, -1]
        self.separator_color = [-1, -1, -1]

        self.sidebar_image = ''
        self.sidebar_alignment = 'lefttop'


class BindGroup:
    def __init__(self, aID, type, title, image=''):
        self.aID = aID
        self.type = type
        self.title = title
        self.image = image
        self.default = False

    def setDefault(self, boolean):
        self.default = False if boolean == '0' else True


class ShellSetting:
    def __init__(self):
        self.name = ''
        self.offset = [0, 0]
        self.balloon_offset = [0, 0]
        self.balloon_alignment = 'lefttop'
        self.bindoption = {}
        self.bindgroups = {}

    def addBingGroup(self, aID, bindgroup):
        self.bindgroups[aID] = bindgroup


class Surface:
    def __init__(self, name, values):
        self.name = name
        self.elements = {}
        self.animations = {}
        self.CollisionBoxes = {}
        self.offest1 = [0, 0]
        self.offest2 = [0, 0]

        self._load_surface(values)
        pass

    def _load_surface(self, values):
        for line in values:
            if line == "":
                continue

            matchtype, params = SurfaceMatchLine.matchLine(line)
            if matchtype == SurfaceMatchLine.Unknow:
                logging.warning("NO Match Line: %s", line)

            elif matchtype == SurfaceMatchLine.Elements:
                self.elements[int(params[0])] = Element(params)

            elif matchtype == SurfaceMatchLine.CollisionBoxes:
                self.CollisionBoxes[int(params[0])] = CollisionBox(params)

            elif matchtype == SurfaceMatchLine.AnimationInterval:
                aid = int(params[0])
                ani = Animation(aid, self.animations) if aid not in self.animations else self.animations[aid]
                if ',' in params[1]:
                    p = params[1].split(',')
                    ani.interval = p[0]
                    ani.intervalValue = float(p[1])
                else:
                    ani.interval = params[1]
                    ani.intervalValue = 0
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.AnimationPattern:
                aid = int(params[0])
                ani = Animation(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.patterns[int(params[1])] = Pattern(params, EPatternType.Normal)
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.AnimationPatternNew:
                aid = int(params[0])
                ani = Animation(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.patterns[int(params[1])] = Pattern(params, EPatternType.New)
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.AnimationPatternAlternative:
                aid = int(params[0])
                ani = Animation(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.patterns[int(params[1])] = Pattern(params, EPatternType.Alternative)
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.AnimationOptionExclusive:
                aid = int(params[0])
                ani = Animation(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.exclusive = True
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.OffectPointX:
                self.offest1[0] = int(params[0])

            elif matchtype == SurfaceMatchLine.OffectPointY:
                self.offest1[1] = int(params[0])

            elif matchtype == SurfaceMatchLine.OffectKinokoPointX:
                self.offest2[0] = int(params[0])

            elif matchtype == SurfaceMatchLine.OffectKinokoPointY:
                self.offest1[1] = int(params[0])

        pass
