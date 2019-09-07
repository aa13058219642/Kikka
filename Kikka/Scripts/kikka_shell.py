# coding=utf-8
import os
import re
import logging
import random
import time
import collections
from enum import Enum
from collections import OrderedDict

from PyQt5.QtCore import QPoint, QRect

import kikka
from kikka_const import WindowConst

class KikkaShell:
    _instance = None
    isDebug = False

    def __init__(self, **kwargs):
        raise SyntaxError('The class is Singletion, please use ShellManager.this() or kikka.shell_manager')

    @staticmethod
    def this():
        if KikkaShell._instance is None:
            KikkaShell._instance = object.__new__(KikkaShell)
            KikkaShell._instance._init()
        return KikkaShell._instance

    def _init(self):
        self._shells = []
        self.shelldir = ''

    def loadShell(self, shelldict, shellpath):
        shell = Shell(shellpath)
        if shell.isInitialized is False:
            return

        isExist = False
        for name, s in shelldict.items():
            if shell.id == s.id and shell.name == name:
                isExist = True
                break

        if not isExist:
            logging.info("scan shell: %s", shell.name)
            shelldict[shell.name] = shell
        else:
            logging.warning("load fail. shell name exist: %s", shell.name)
        pass

    def scanShell(self, shelldir):
        self.shelldir = shelldir

        shelldict = {}
        for parent, dirnames, filenames in os.walk(shelldir):
            for dirname in dirnames:
                shellpath = os.path.join(parent, dirname)
                self.loadShell(shelldict, shellpath)
        pass #exit for

        shellordereddict = collections.OrderedDict(sorted(shelldict.items(), key=lambda t: t[0]))
        for name, shell in shellordereddict.items():
            self._shells.append(shell)

        logging.info("shell scan finish: count %d", len(self._shells))

    def getShell(self, index):
        if 0 <= index < len(self._shells):
            shell = self._shells[index]
            return shell
        else:
            logging.error("getShell: index NOT in shell list")
            raise ValueError

    def getShellCount(self):
        return len(self._shells)


class Shell:
    def __init__(self, shellpath):
        self.shellpath = shellpath  # root path of this shell
        self.id = ''
        self.name = ''
        self.type = ''
        self.author = AuthorInfo()
        self.version = 0
        self.maxwidth = 0
        self.collision_sort = 'none'
        self.animation_sort = 'descend'

        self.bind = []
        self.alias = {}
        self.pnglist = []
        self.setting = {}
        self.isLoaded = False
        self.isInitialized = False
        self.shellmenustyle = ShellMenuStyle()

        self._surfaces = {}
        self._updatetime = 0

        # path check
        if os.path.exists(shellpath):
            descript_map = self._open_descript()
            if descript_map is not None:
                self._load_descript(descript_map)
                self._loadPNGindex()
                self.isInitialized = True
        pass

    def load(self):
        if self.isLoaded is False:
            logging.info("load shell: %s", self.name)
            self._load_surfaces()
            self._sort_data()
            self._updatetime = time.clock()
            self.isLoaded = True
        pass

    def _loadPNGindex(self):
        for parent, dirnames, filenames in os.walk(self.shellpath):
            for filename in filenames:
                if filename[len(filename) - 4:] == '.png':
                    self.pnglist.append(filename)
        pass

    def _open_descript(self):
        descript_path = os.path.join(self.shellpath, 'descript.txt')
        if not os.path.exists(descript_path):
            return None

        map = {}
        charset = kikka.helper.checkEncoding(descript_path)

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
        f.close()
        return map

    def _open_surfaces(self, surfaces_path, map=None):
        surfaces_map = {} if map is None else map
        surfaceID = []

        the_line_is_key = True
        struct_type = 0
        ALIAS_DATA = 1
        SURFACES_DATA = 2
        DESCRIPT_DATA = 3

        charset = kikka.helper.checkEncoding(surfaces_path)

        f = open(surfaces_path, 'r', encoding=charset)
        for line in f:
            line = line.replace("\n", "").replace("\r", "")
            line = line.strip(' ')

            if line == '' \
            or line.find(r'\\') == 0 \
            or line.find('//') == 0 \
            or line.find('#') == 0:
                continue

            if line == '{':
                the_line_is_key = False
                continue

            if line == '}':
                the_line_is_key = True
                surfaceID = []
                continue

            if the_line_is_key is False:
                # set value
                if struct_type == SURFACES_DATA:
                    for id in surfaceID:
                        surfaces_map[id].append(line)
                elif struct_type == ALIAS_DATA:
                    index = line.index(',')
                    id = int(line[0:index])
                    arr = line[index+2:-1].split(',')
                    irr = [int(i) for i in arr]
                    self.alias[id] = irr
                elif struct_type == DESCRIPT_DATA:
                    keys = line.replace(' ', '').split(',')
                    if keys[0] == 'version':
                        self.version = int(keys[1])
                    elif keys[0] == 'maxwidth':
                        self.maxwidth = int(keys[1])
                    elif keys[0] == 'collision-sort' and keys[1] in ['none', 'ascend', 'descend']:
                        self.collision_sort = keys[1]
                    elif keys[0] == 'animation-sort' and keys[1] in ['ascend', 'descend']:
                        self.animation_sort = keys[1]
                    else:
                        self._IgnoreParams(keys[0], keys[1])
            else:
                # check struct ID
                if 'descript' in line:
                    struct_type = DESCRIPT_DATA
                    continue

                if 'alias' in line:
                    struct_type = ALIAS_DATA
                    continue

                struct_type = SURFACES_DATA
                keys = line.replace('surface', '').replace(' ', '').split(',')
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
                                if id in surfaces_map:
                                    surfaceID.remove(id)
                                    surfaces_map.pop(id)
                        else:
                            id = int(key)
                            surfaceID.remove(id)
                            surfaces_map.pop(id)
                    else:
                        # add ID
                        if '-' in key:
                            v = key.split('-')
                            a = int(v[0])
                            b = int(v[1])
                            for id in range(a, b):
                                if id not in surfaces_map:
                                    surfaceID.append(id)
                                    surfaces_map[id] = []
                        else:
                            id = int(key)
                            surfaceID.append(id)
                            if id not in surfaces_map:
                                surfaces_map[id] = []
                    pass
                pass # exit for
            pass
        pass  # exit for
        f.close()
        return surfaces_map

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

            elif key[0] in ['sakura','kero'] or key[0:4] == 'char':

                if key[0] == 'sakura':
                    sid = 0
                elif key[0] == 'kero':
                    sid = 1
                else:
                    sid = int(key[5:])

                if sid not in self.setting.keys():
                    self.setting[sid] = ShellSetting()

                if 'bindgroup' in key[1]:
                    aid = int(key[1][9:])
                    if key[2] == 'name':
                        img = '' if len(value) < 3 else value[2]
                        self.setting[sid].bindgroups[aid] = BindGroup(aid, value[0], value[1], img)
                    elif key[2] == 'default':
                        self.setting[sid].bindgroups[aid].setDefault(value[0])
                    else:
                        self._IgnoreParams(keys, values)
                elif 'menuitem' in key[1]:
                    mid = int(key[1][8:])
                    if value[0] != '-':
                        self.setting[sid].clothesmenu[mid] = int(value[0])
                    else:
                        self.setting[sid].clothesmenu[mid] = -1
                elif key[1] == 'balloon':
                    if key[2] == 'offsetx':
                        self.setting[sid].balloon_offset.setX(int(value[0]))
                    elif key[2] == 'offsety':
                        self.setting[sid].balloon_offset.setY(int(value[0]))
                    elif key[2] == 'alignment':
                        self.setting[sid].balloon_alignment = value[0]
                    else:
                        self._IgnoreParams(keys, values)
                elif 'bindoption' in key[1]:
                    gid = int(key[1][10:])
                    if key[2] == 'group':
                        self.setting[sid].bindoption[value[0]] = value[1]
                    else:
                        self._IgnoreParams(keys, values)
                elif 'defaultx' in key[1]:
                    self.setting[sid].offset.setX(int(value[0]))
                elif 'defaulty' in key[1]:
                    self.setting[sid].offset.setY(int(value[0]))
                elif 'defaultleft' in key[1]:
                    self.setting[sid].position.setX(int(value[0]))
                elif 'defaulttop' in key[1]:
                    self.setting[sid].position.setY(int(value[0]))
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
            if not os.path.exists(surfaces_path):
                break
            surfaces_map = self._open_surfaces(surfaces_path, surfaces_map)
            i = i + 1

        for key, values in surfaces_map.items():
            self._surfaces[key] = Surface(key, values)

    def _IgnoreParams(self, key, values):
        logging.info('unknow shell params: %s,%s' % (key, values))
        pass

    def _sort_data(self):

        def _sort(item, reverse=False):
            return collections.OrderedDict(sorted(item, key=lambda t: t[0], reverse=reverse))

        self._surfaces = _sort(self._surfaces.items())
        for sid, surface in self._surfaces.items():
            self._surfaces[sid].elements = _sort(surface.elements.items())
            self._surfaces[sid].animations = _sort(surface.animations.items(), self.animation_sort == 'ascend')
            if self.collision_sort != 'none':
                self._surfaces[sid].CollisionBoxes = _sort(surface.CollisionBoxes.items(), self.collision_sort == 'ascend')
        pass

    def getSurface(self, surfacesID):
        if surfacesID in self._surfaces:
            return self._surfaces[surfacesID]
        else:
            logging.error("setCurShell: index[%d] NOT in shells list" % (surfacesID))

    def getCollisionBoxes(self, surfacesID):
        surface = self._surfaces[surfacesID]
        return surface.CollisionBoxes

    def getOffset(self, soulId):
        return self.setting[soulId].offset

    def getShellMenuStyle(self):
        return self.shellmenustyle

    def addBind(self, aid):
        if aid not in self.bind:
            self.bind.append(aid)
            self.bind.sort()

    def getBind(self):
        return self.bind

    def setClothes(self, aid, isEnable=True):
        if isEnable is True and aid not in self.bind:
            self.addBind(aid)
        elif aid in self.bind:
            self.bind.remove(aid)


class AnimationData:
    def __init__(self, id, parent):
        self._parent = parent
        self.ID = id
        self.interval = 'never'
        self.intervalValue = 0
        self.exclusive = False
        self.patterns = OrderedDict()

        self.isRuning = False
        self.updatetime = 0
        self.curPattern = -1
        self._lasttime = 0


class Surface:
    def __init__(self, id, values):
        self.ID = id
        self.elements = {}
        self.animations = {}
        self.CollisionBoxes = {}
        self.rect = QRect()

        self.basepos = QPoint(WindowConst.UNSET)
        self.surfaceCenter = QPoint(WindowConst.UNSET)
        self.kinokoCenter = QPoint(WindowConst.UNSET)

        self._load_surface(values)

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
                ani = AnimationData(aid, self.animations) if aid not in self.animations else self.animations[aid]
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
                ani = AnimationData(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.patterns[int(params[1])] = Pattern(params, EPatternType.Normal)
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.AnimationPatternNew:
                aid = int(params[0])
                ani = AnimationData(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.patterns[int(params[1])] = Pattern(params, EPatternType.New)
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.AnimationPatternAlternative:
                aid = int(params[0])
                ani = AnimationData(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.patterns[int(params[1])] = Pattern(params, EPatternType.Alternative)
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.AnimationOptionExclusive:
                aid = int(params[0])
                ani = AnimationData(aid, self.animations) if aid not in self.animations else self.animations[aid]
                ani.exclusive = True
                self.animations[aid] = ani

            elif matchtype == SurfaceMatchLine.SurfaceCenterX:
                self.surfaceCenter.setX(int(params[0]))

            elif matchtype == SurfaceMatchLine.SurfaceCenterY:
                self.surfaceCenter.setY(int(params[0]))

            elif matchtype == SurfaceMatchLine.KinokoCenterX:
                self.kinokoCenter.setX(int(params[0]))

            elif matchtype == SurfaceMatchLine.KinokoCenterY:
                self.kinokoCenter.setY(int(params[0]))

            elif matchtype == SurfaceMatchLine.BaseposX:
                self.basepos.setX(int(params[0]))

            elif matchtype == SurfaceMatchLine.BaseposX:
                self.basepos.setY(int(params[0]))
        pass # exit for


class EPatternType(Enum):
    Normal = 0
    New = 1
    Alternative = 2


class Pattern:
    def __init__(self, params, matchtype=EPatternType.Normal):
        self.bindAnimation = -1
        if matchtype == EPatternType.Normal:
            self.ID = int(params[1])
            self.methodType = params[4]
            self.surfaceID = int(params[2])
            self.time = int(params[3]) * 10
            self.offset = QPoint(int(params[5]), int(params[6]))
            self.aid = [-1]
        elif matchtype == EPatternType.New:
            self.ID = int(params[1])
            self.methodType = params[2]
            self.surfaceID = int(params[3])
            self.time = int(params[4])
            self.offset = QPoint(int(params[5]), int(params[6]))
            self.aid = [-1]
        elif matchtype == EPatternType.Alternative:
            self.ID = int(params[1])
            self.methodType = params[4]
            self.surfaceID = int(params[2])
            self.time = int(params[3])
            self.offset = QPoint()
            if '.' in params[5]:
                self.aid = list(map(int, params[5].split('.')))
            elif ',' in params[5]:
                self.aid = list(map(int, params[5].split(',')))
            else:
                self.aid = [int(params[5])]

    def isControlPattern(self):
        return self.methodType in ['alternativestart', 'start', 'insert', 'alternativestop', 'stop']
    pass


class Element:
    def __init__(self, params):
        self.ID = int(params[0])
        self.PaintType = params[1]
        self.filename = params[2]
        self.offset = QPoint(int(params[3]), int(params[4]))


class CollisionBox:
    def __init__(self, params):
        self.ID = int(params[0])
        self.Point1 = QPoint(int(params[1]), int(params[2]))
        self.Point2 = QPoint(int(params[3]), int(params[4]))
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

    SurfaceCenterX = 401
    SurfaceCenterY = 402
    KinokoCenterX = 403
    KinokoCenterY = 404
    BaseposX = 405
    BaseposY = 406

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

        # Surface Center X
        # point.centerx,[int]
        res = re.match(r'^point.centerx,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.SurfaceCenterX, res.groups()

        # Surface Center Y
        # point.centery,[int]
        res = re.match(r'^point.centery,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.SurfaceCenterY, res.groups()

        # Kinoko Center X
        # point.kinoko.centerx,[int]
        res = re.match(r'^point.kinoko.centerx,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.KinokoCenterX, res.groups()

        # Kinoko Center Y
        # point.kinoko.centery,[int]
        res = re.match(r'^point.kinoko.centery,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.KinokoCenterY, res.groups()

        # basepos X
        # point.basepos.centerx,[int]
        res = re.match(r'^point.basepos.centerx,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.BaseposX, res.groups()

        # basepos Y
        # point.basepos.centery,[int]
        res = re.match(r'^point.basepos.centery,(\d+)$', line)
        if res is not None: return SurfaceMatchLine.BaseposY, res.groups()

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
        self.offset = QPoint(0, 0)
        self.position = QPoint(0, 0)
        self.balloon_offset = QPoint(0, 0)
        self.balloon_alignment = 'lefttop'
        self.bindoption = {}
        self.bindgroups = {}
        self.clothesmenu = {}

    def addBingGroup(self, aID, bindgroup):
        self.bindgroups[aID] = bindgroup

