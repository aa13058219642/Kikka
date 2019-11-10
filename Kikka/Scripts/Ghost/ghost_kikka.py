# coding=utf-8
import os
import sys
import time
import random
import logging
import datetime
import requests

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QImage, QIcon

import kikka
from kikka_const import  GhostEvent
from ghost_ai import GhostAI
from dialogwindow import DialogWindow

KIKKA = 0
TOWA = 1


class GhostKikka(GhostAI):

    def __init__(self, gid=-1, name='Kikka'):
        GhostAI.__init__(self, gid, name)
        self._datetime = datetime.datetime.now()
        self._touch_count = {KIKKA: {}, TOWA: {}}

    def init(self):
        super().init()
        w_kikka = self.addSoul(KIKKA, 0)
        w_towa = self.addSoul(TOWA, 10)
        self._weather = self.getWeather()

        self.initLayout()
        self.initTalk()
        self.initMenu()
        self.onFirstBoot()


    def initLayout(self):
        dlg = self.getSoul(KIKKA).getDialog()
        self._kikkaWidget = QWidget()
        self._mainLayout = QVBoxLayout()
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._stackedLayout = QStackedLayout()
        self._stackedLayout.setContentsMargins(0, 0, 0, 0)
        self._topLayout = QVBoxLayout()
        self._footerLayout = QHBoxLayout()

        # 0 main Layout
        self._mainLayout.addLayout(self._topLayout)
        self._mainLayout.addLayout(self._stackedLayout)
        self._mainLayout.addLayout(self._footerLayout)

        # 1.0 top layout
        self._toplabel = QLabel("Hello")
        self._toplabel.setObjectName('Hello')
        self._topLayout.addWidget(self._toplabel)

        # 1.2 tab layout
        self._tabLayout = QHBoxLayout()
        self._topLayout.addLayout(self._tabLayout)

        # 1.2.1 tab button
        p1 = QPushButton("常用")
        p2 = QPushButton("设置")
        p1.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(0))
        p2.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(1))
        self._tabLayout.addWidget(p1)
        self._tabLayout.addWidget(p2)
        self._tabLayout.addStretch()

        # 2.0 page
        page1 = QWidget(self._kikkaWidget)
        page2 = QWidget(self._kikkaWidget)
        self._stackedLayout.addWidget(page1)
        self._stackedLayout.addWidget(page2)
        page1L = QWidget(page1)
        page1R = QWidget(page1)
        page2L = QWidget(page2)
        page2R = QWidget(page2)

        # 2.1.1 page1L
        pl1 = QVBoxLayout()
        pl1.setContentsMargins(0, 0, 0, 0)
        page1L.setLayout(pl1)
        bt1 = QPushButton("◇复制壁纸")
        bt1.clicked.connect(self.copyWallPaper)
        pl1.addWidget(bt1)

        # 2.1.2 page1R
        pl2 = QVBoxLayout()
        pl2.setContentsMargins(0, 0, 0, 0)

        page1R.setLayout(pl2)
        pl2.addStretch()

        # 2.2.1 page2L
        pl3 = QVBoxLayout()
        pl3.setContentsMargins(0, 0, 0, 0)
        page2L.setLayout(pl3)
        callback_ResizeWindow = lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, KIKKA, GhostEvent.CustomEvent, 'ResizeWindow', {'bool':False}))
        bt1 = QPushButton("◇更改称呼")
        bt2 = QPushButton("◇调整对话框")
        bt3 = QPushButton("◇设置天气APIkey")
        bt1.clicked.connect(lambda : self.getSoul(KIKKA).getDialog().showInputBox("新的称呼: ", self.getVariable('username'), callback=self.callback_setUserName))
        bt2.clicked.connect(callback_ResizeWindow)
        bt3.clicked.connect(lambda : self.getSoul(KIKKA).getDialog().showInputBox("请输入和风天气的APIkey:\n可以在 https://dev.heweather.com/ 免费申请哦~", self.memoryRead('WeatherKey', ''), callback=self.callback_serWeatherAPI))
        pl3.addWidget(bt1)
        pl3.addWidget(bt2)
        pl3.addWidget(bt3)
        pl3.addStretch()

        # 2.2.2 page2R
        pl4 = QVBoxLayout()
        pl4.setContentsMargins(0, 0, 0, 0)
        page2R.setLayout(pl4)
        pl4.addStretch()

        # 3.0 footer layout
        self._footerLayout.addStretch()
        callback_CloseDialog = lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, KIKKA, GhostEvent.CustomEvent, 'CloseDialog', {'bool':False}))
        closebtn = QPushButton("关闭")
        closebtn.clicked.connect(callback_CloseDialog)
        self._footerLayout.addWidget(closebtn)

        self._kikkaWidget.setLayout(self._mainLayout)
        dlg.setPage(DialogWindow.DIALOG_MAINMENU, self._kikkaWidget)


        dlg = self.getSoul(TOWA).getDialog()
        self._towaWidget = QWidget()
        mainLayout = QVBoxLayout()
        btn1 = QPushButton("move dialog")
        btn1.clicked.connect(lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, TOWA, GhostEvent.CustomEvent, 'ResizeWindow', {'bool':False})))

        btn2 = QPushButton("close")
        btn2.clicked.connect(lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, TOWA, GhostEvent.CustomEvent, 'CloseDialog', {'bool':False})))
        mainLayout.addWidget(btn1)
        mainLayout.addWidget(btn2)
        self._towaWidget.setLayout(mainLayout)
        dlg.setPage(DialogWindow.DIALOG_MAINMENU, self._towaWidget)

    def initMenu(self):
        # mainmenu = self.getMenu(KIKKA)
        # menu = Menu(mainmenu.parent(), self.ID, "kikka menu")
        # mainmenu.insertMenu(mainmenu.actions()[0], menu)
        #
        # def _test_callback(index=0, title=''):
        #     logging.info("GhostKikka_callback: click [%d] %s" % (index, title))
        #
        # act = menu.addMenuItem("111", _test_callback)
        # act.setShortcut(QKeySequence("Ctrl+T"))
        # act.setShortcutContext(Qt.ApplicationShortcut)
        # act.setShortcutVisibleInContextMenu(True)
        #
        #
        # w = self.getShellWindow(KIKKA)
        # w.addAction(act)
        pass

    def ghostEvent(self, param):
        super().ghostEvent(param)

        if param.eventType == GhostEvent.Dialog_Show:
            if self._weather is not None:
                text = "%s现在是%s℃哦，%s" % (self._weather['basic']['location'], self._weather['now']['tmp'], self.getVariable('username'))
                self._toplabel.setText(text)
                self._stackedLayout.setCurrentIndex(0)
        elif param.eventType == GhostEvent.CustomEvent:
            if param.eventTag == 'ResizeWindow':
                self.resizeWindow(param)
            elif param.eventTag == 'CloseDialog':
                self.closeDlg(param)

    def changeShell(self, shellID):
        logging.debug("Please don't peek at me to change clothes!")
        super().changeShell(shellID)

    # ########################################################################################################

    def onFirstBoot(self):
        boot_last = datetime.datetime.fromtimestamp(self.memoryRead('BootThis', time.time()))
        today = datetime.datetime.now()
        if boot_last.day == today.day:
            return

        shell_name = None
        # feastival
        if today.month == 1 and today.day == 1:
            shell_name = 'normal-Yukata'
        elif today.month == 2 and today.day == 22:
            shell_name = 'normal-NekoMimi'
        elif today.month == 3 and today.day == 5:
            shell_name = 'cosplay-SilverFox'
        elif today.month == 3 and today.day == 9:
            shell_name = 'cosplay-HatsuneMiku'
        elif today.month == 3 and today.day == 28 \
        or today.month == 4 and today.day == 29:
            shell_name = 'cosplay-Momohime'
        elif today.month == 4 and today.day == 8:
            shell_name = 'cosplay-KonpakuYoumu'
        elif today.month == 5 and today.day == 2:
            shell_name = 'normal-Maid'
        elif today.month == 6 and today.day == 10 \
        or today.month == 8 and today.day == 11 \
        or today.month == 7 and today.day == 27:
            shell_name = 'cosplay-IzayoiSakuya'
        elif today.month == 8 and today.day == 17:
            shell_name = 'cosplay-InubashiriMomizi'
        elif today.month == 9 and today.day == 3:
            shell_name = 'cosplay-SetsukoOhara'
        elif today.month == 10 and today.day == 13:
            shell_name = 'private-Nurse'
        elif today.month == 10 and today.day == 22:
            shell_name = 'cosplay-Win7'
        elif today.month == 10 and today.day == 25:
            shell_name = 'cosplay-Taiwan'
        elif today.month == 10 and today.day == 31:
            shell_name = 'normal-Halloween'
        elif today.month == 12 and today.day == 25:
            shell_name = 'normal-Christmas'

        if shell_name is not None:
            self.setShell(shell_name)
            return

        shell_name = random.choice(self.getShellByWeather(self._weather))
        if shell_name is not None:
            self.setShell(shell_name)
            return

        # auto change shell every day!
        shell_list = []
        if today.month in [3, 4, 5]:
            shell_list = ['_Default_1',
                          '_Default_2',
                          'cosplay-Momohime',
                          'cosplay-SetsukoOhara',
                          'cosplay-WhiteBase',
                          'cosplay-Win7',
                          'cosplay-HatsuneMiku',
                          'cosplay-Taiwan',
                          'cosplay-InubashiriMomizi',
                          'cosplay-RemiliaScarlet',
                          'normal-Maid',
                          'normal-RedDress',
                          'normal-LongSkirt',
                          ]
        elif today.month in [6, 7, 8]:
            shell_list = ['private-HadaY',
                          'private-PolkaDots',
                          'private-China',
                          'private-Lingerie2',
                          'private-Lingerie1',
                          'normal-PinkDress',
                          'normal-ARN-5041W',
                          'normal-Swimsuit',
                          'normal-Sleeveless',
                          'normal-Camisole',
                          'normal-ZashikiChildren',
                          'normal-SummerDress1',
                          'normal-SummerDress2',
                          'normal-SummerDress3',
                          'normal-Yukata',
                          'normal-Taisou',
                          'cosplay-KonpakuYoumu',
                          'cosplay-SilverFox',
                          'cosplay-ZaregotoSeries',
                          'cosplay-LeberechtMaass',
                          ]
        elif today.month in [9, 10, 11]:
            shell_list = ['private-Nurse',
                          'private-BunnyGirl',
                          'normal-Sleeveless',
                          'normal-ZashikiChildren',
                          'cosplay-KonpakuYoumu',
                          'cosplay-SilverFox',
                          'cosplay-RemiliaScarlet',
                          'cosplay-InubashiriMomizi',
                          'cosplay-IzayoiSakuya',
                          'cosplay-HatsuneMiku',
                          'cosplay-Win7',
                          'cosplay-WhiteBase',
                          'cosplay-SetsukoOhara',
                          'cosplay-Momohime',
                          'cosplay-LeberechtMaass',
                          ]
        elif today.month in [12, 1, 2]:
            shell_list = ['_Default_1',
                          '_Default_2',
                          'normal-Winter',
                          'normal-Christmas',
                          'private-Sweater',
                          'private-Nurse',
                          'normal-LongSkirt',
                          'normal-RedDress',
                          'normal-NekoMimi',
                          'normal-DogEar',
                          'normal-Maid',
                          'cosplay-Maetel',
                          '201cosplay-Accessories',
                          ]

        shell_name = self.shell.name
        if shell_name in shell_list:
            shell_list.remove(shell_name)

        shell_name = random.choice(shell_list)
        self.setShell(shell_name)

    def getWeather(self):
        """ Example data:
        {
            "basic": {
                "cid": "CN101010100",
                "location": "Beijing",
                "parent_city": "Beijing",
                "admin_area": "Beijing",
                "cnty": "China",
                "lat": "39.90498734",
                "lon": "116.4052887",
                "tz": "+8.00"
            },
            "update": {
                "loc": "2019-06-05 22:39",
                "utc": "2019-06-05 14:39"
            },
            "status": "ok",
            "now": {
                "cloud": "91",
                "cond_code": "104",
                "cond_txt": "阴",
                "fl": "24",
                "hum": "56",
                "pcpn": "0.0",
                "pres": "1005",
                "tmp": "23",
                "vis": "8",
                "wind_deg": "73",
                "wind_dir": "东北风",
                "wind_sc": "1",
                "wind_spd": "4"
            }
        }
        """

        try:
            # you can get a free weather API key from https://dev.heweather.com/
            key = self.memoryRead('WeatherKey', '')
            if key == '':
                return None

            result = requests.get('https://free-api.heweather.net/s6/weather/now?location=auto_ip&key=' + key)
            if result.status_code != 200:
                logging.warning("getWeather FAIL")
                return None

            weather = result.json()

            # API version s6
            if 'HeWeather6' not in weather and len(weather['HeWeather6']) == 0:
                return None

            data = weather['HeWeather6'][0]
            if data['status'] != 'ok':
                logging.warning("getWeather API FAIL: %s" % data['status'])
                return None

            return data
        except:
            logging.warning("getWeather FAIL")

        return None

    def resizeWindow(self, param):
        dlg = kikka.core.getGhost(param.ghostID).getSoul(param.soulID).getDialog()
        dlg.setFramelessWindowHint(param.data['bool'])

    def closeDlg(self, param):
        kikka.core.getGhost(param.ghostID).getSoul(param.soulID).getDialog().hide()

    def callback_setUserName(self, text):
        if text is None or text == '':
            return
        self.setVariable('username', text)
        self.memoryWrite('UserName', text)
        self.talk(r"\0\s[0]『%(username)』是吗。\w9\w9\n\n[half]\0\s[6]那么再一次…\w9\s[26]\n\n[half]橘花和斗和、以后请多多指教。\1\s[10]多指教啦。\w9\0\s[30]\n\n[half]…终于开口了。")

    def callback_serWeatherAPI(self, text):
        if text is None or text == '':
            return
        self.memoryWrite('WeatherKey', text)
        weather = self.getWeather()
        if weather is None:
            self.talk(r"\0好像设置失败了呢\e")
        else:
            self.talk("\0设置成功\n\w9\s[5]%s现在是%s℃哦" % (self._weather['basic']['location'], self._weather['now']['tmp']))

    def copyWallPaper(self):
        def findImage(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    file = os.path.join(root, f)
                    if QImage().load(file):
                        return file
            return None

        if sys.platform != 'win32':
            self.talk(r'现在只支持复制windows系统呢')
            return

        wallpaper_path = os.path.join(os.path.expanduser('~'), 'AppData/Roaming/Microsoft/Windows/Themes/CachedFiles')
        if os.path.exists(wallpaper_path):
            w, h = kikka.helper.getScreenResolution()
            file = os.path.join(wallpaper_path, "CachedImage_%d_%d_POS2.jpg" % (w, h))
            wallpaper_file = file if os.path.exists(file) else findImage(wallpaper_path)
        else:
            # muti screen
            wallpaper_path = os.path.dirname(wallpaper_path)
            file = os.path.join(wallpaper_path, "Transcoded_000")
            wallpaper_file = file if os.path.exists(file) and QImage().load(file) else findImage(wallpaper_path)

        if wallpaper_file is None:
            self.talk("\0\s[8]好像失败了呢")
        else:
            clipboard = QApplication.clipboard()
            clipboard.setImage(QImage(wallpaper_file))
            self.talk("\0\s[5]已经复制到剪贴板了哦~")
        x = 0
        pass

    def onUpdate(self, updatetime):
        super().onUpdate(updatetime)
        self.onDatetime()

    def getShellByWeather(self, weather):
        if weather is None:
            return []

        tmp = int(weather['now']['tmp'])
        if tmp <= 5:
            shell_list = ['_Default_1',
                          '_Default_2',
                          'normal-Winter',
                          'normal-RedDress',
                          'normal-NekoMimi',
                          'normal-Maid',
                          'normal-LongSkirt',
                          'normal-Halloween',
                          'normal-DogEar',
                          'normal-Christmas',
                          'cosplay-Momohime',
                          'cosplay-Maetel',
                          'cosplay-Accessories'
                          ]
        elif tmp <= 16:
            shell_list = ['_Default_1',
                          '_Default_2',
                          'private-Sweater',
                          'normal-Christmas',
                          'cosplay-Win7',
                          'cosplay-WhiteBase',
                          'cosplay-Taiwan',
                          'cosplay-SilverFox',
                          'cosplay-SetsukoOhara',
                          'cosplay-LeberechtMaass',
                          'cosplay-IzayoiSakuya',
                          'cosplay-InubashiriMomizi'
                          ]
        elif tmp <= 27:
            shell_list = ['_Default_1',
                          '_Default_2',
                          'private-Nurse',
                          'private-HadaY',
                          'private-BunnyGirl',
                          'normal-ZashikiChildren',
                          'normal-Yukata',
                          'cosplay-ZaregotoSeries',
                          'cosplay-SilverFox',
                          'cosplay-RemiliaScarlet',
                          'cosplay-KonpakuYoumu',
                          'cosplay-HatsuneMiku'
                          ]
        else:
            shell_list = ['private-PolkaDots',
                          'private-Lingerie1',
                          'private-Lingerie2',
                          'private-China',
                          'normal-Taisou',
                          'normal-Swimsuit',
                          'normal-SummerDress1',
                          'normal-SummerDress2',
                          'normal-SummerDress3',
                          'normal-Sleeveless',
                          'normal-PinkDress',
                          'normal-Camisole',
                          'normal-ARN-5041W'
                          ]
        return shell_list

    def onDatetime(self):
        if self.isTalking():
            return

        now = datetime.datetime.now()
        if self._datetime.minute != now.minute:
            script = ''
            if now.hour == 7 and now.minute == 30:
                script = r"\0\s[5]早晨%(hour)点%(minute)分了，\w4该吃早餐了哦。\e"
            elif now.hour == 12 and now.minute == 10:
                script = r"\0\s[5]已经%(hour)点%(minute)分了，\w4该吃午餐了哦。\e"
            elif now.hour == 18 and now.minute == 10:
                script = r"\0\s[5]已经%(hour)点%(minute)分了，\w4该吃晚餐了哦。\e"
            elif now.hour == 23 and now.minute == 30:
                script = r"\0\s[5]现在是%(hour)点%(minute)分，\w9\w4要不要考虑吃个宵夜呢。\e"
            elif now.minute == 0:
                weather = self.getWeather()
                if weather is not None:
                    self._weather = weather
                    shell_list = self.getShellByWeather(weather)
                    if self.shell.name not in shell_list:
                        shell_name = random.choice(shell_list)
                    if shell_name is not None:
                        self.changeShell(shell_name)

                if now.hour == 0:
                    script = r"\0凌晨12点了呢.又是新的一天～\e"
                elif 1 <= now.hour <= 4:
                    script = random.choice([
                        r"\0%(hour)点了.%(username)还不睡吗\e",
                        r"\0%(hour)点了.%(username)不睡吗？熬夜会变笨的喔\e"
                    ])
                elif now.hour in [5, 6]:
                    script = random.choice([
                        r"\0%(hour)点了..要去看日出吗\e",
                        r"\0呼哈～唔..%(hour)点了\e",
                    ])
                elif now.hour in [7, 8]:
                    script = random.choice([
                        r"\0%(hour)点了.还沒清醒的话赶快打起精神喔\e"
                    ])
                elif now.hour in [9, 10, 11]:
                    script = random.choice([
                        r"\0%(hour)点了..据说是人一天中记忆能力最好的時段呢，要好好利用喔\e"
                    ])
                elif now.hour == 12:
                    script = random.choice([
                        r"12点了.午餐时间～\e"
                    ])
                elif now.hour in [13, 14]:
                    script = random.choice([
                        r"\0下午%(hour12)点了…總是很想睡的时间呢\e"
                    ])
                elif now.hour in [15, 16]:
                    script = random.choice([
                        r"\0%(hour)点了.要不要來杯下午茶呢\e"
                    ])
                elif now.hour in [17, 18]:
                    script = random.choice([
                        r"\0下午%(hour12)点.晚餐时间～\e"
                    ])
                elif 19 <= now.hour <= 23:
                    script = random.choice([
                        r"\0%(hour)点了..接下來该做什么事呢\e",
                        r"\0晚上%(hour12)了呢..%(username)在做什么呢\e",
                        r"\0晚上%(hour12)了呢..这个时间%(username)应该都在电脑前吧\e"
                    ])

            self._datetime = now
            self.talk(script)
        pass  # exit if

    def getPhase(self):
        return 2

    def touchTalk(self, param):
        sid = param.soulID
        phase = self.getPhase()

        if param.eventTag not in self._touch_count[sid].keys():
            self._touch_count[sid][param.eventTag] = 0

        # touchtalk[soulID][eventType][eventTag][phase][touchcount]
        if sid in self._touchtalk.keys() \
        and param.eventType in self._touchtalk[sid].keys() \
        and param.eventTag in self._touchtalk[sid][param.eventType].keys():
            talks = self._touchtalk[sid]

            if phase not in talks[param.eventType].keys():
                phase = 0

            if len(talks[param.eventType][param.eventTag]) <= 0 \
            and len(talks[param.eventType][param.eventTag][phase]) <= 0:
                return False

            count = self._touch_count[sid][param.eventTag] % len(talks[param.eventType][param.eventTag][phase])
            if len(talks[param.eventType][param.eventTag][phase][count]) <= 0:
                return False

            script = random.choice(talks[param.eventType][param.eventTag][phase][count])
            self._touch_count[sid][param.eventTag] += 1
            self.talk(script)
            return True
        return False

    def initTalk(self):
        # touchtalk[soulID][eventType][eventTag][phase][touchcount]
        self._touchtalk = {
            KIKKA: {
                GhostEvent.Shell_MouseTouch: {
                    'Head': {0: {}, 1: {}, 2: {}},
                    'Face': {0: {}},
                    'Bust': {0: {}, 1: {}, 2: {}},
                    'Hand': {0: {}},
                },
                GhostEvent.Shell_MouseDoubleClick: {
                    'Head': {0: {}, 1: {}, 2: {}},
                    'Face': {0: {}, 1: {}, 2: {}},
                    'Bust': {0: {}, 1: {}, 2: {}},
                    'Hand': {0: {}, 1: {}, 2: {}},
                },
                GhostEvent.Shell_WheelEvent: {
                    'Hand': {0: {}, 1: {}},
                }
            },
            TOWA: {
                GhostEvent.Shell_MouseTouch: {
                    'Head': {0: {}},
                    'Tail': {0: {}},
                },
                GhostEvent.Shell_MouseDoubleClick: {
                    'Head': {0: {}},
                    'Tail': {0: {}},
                },
                GhostEvent.Shell_WheelEvent: {
                    'Head': {0: {}},
                    'Tail': {0: {}},
                },
            }
        }

        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][0][0] = [
            r"\0\s[1]怎、\w9\w5怎么了吗？\e",
            r"\0\s[2]呀…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]这个…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][0][1] = [
            r"\0\s[9]…\w9…\w9…\e",
            r"\0\s[33]…哎呀…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][1][0] = [
            r"\0\s[1]怎、\w9\w5怎么了吗？\e",
            r"\0\s[2]呀…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]这个…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][1][1] = [
            r"\0\s[1]…\w9嗯？\e",
            r"\0\s[1]那个…\w9\s[1]这个…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][1][2] = [
            r"\0\s[1]%(username)…\e",
            r"\0\s[1]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][1][3] = [
            r"\0\s[29]…\w9谢谢。\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][1][4] = [
            r"\0\s[1]那个…\w9已经可以了…\e",
            r"\0\s[1]那个…\w9我没关系的…\e",
            r"\0\s[1]…\w9…\w9…\e",
            r"\0\s[1]唔…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][2][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\e",
            r"\0\s[26]…\w9…\w9…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]那个…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][2][1] = [
            r"\0\s[1]谢…\w9谢谢…\e",
            r"\0\s[1]%(username)…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][2][2] = [
            r"\0\s[29]…\w9…\w9…\e",
            r"\0\s[1]这个…\w9\w9我的头发、\w9怎么了吗？\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][2][3] = [
            r"\0\s[29]…\w9那个。\w9\w9\s[1]\n啊…\w9没事…\e",
            r"\0\s[1]那、\w9那个…\w9\w9\n我会害羞的。\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Head'][2][4] = [
            r"\0\s[29]嗯…\e",
            r"\0\s[1]…\w9…\w9…\e",
            r"\0\s[1]那个…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9唔…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Face'][0][0] = [
            r"\0\s[6]嗯。\w9\w9\s[0]\n怎么了？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Face'][0][1] = [
            r"\0\s[6]嗯？\w9\w9\s[20]\n那个、\w9我脸上有什么东西吗？\e",
            r"\0\s[6]唔嗯…\w9\w9\s[2]那个、\w9怎么了？\e",
            r"\0\s[21]好痒喔。\e",
            r"\0\s[6]唔…\w9\w9\s[2]\n…\w9…\w9…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Bust'][0][0] = [
            r"\0\s[35]…\w9…\w9…\1\s[12]你就这么喜欢摸女生胸部吗……\0\e",
            r"\0\s[35]唔…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[35]啊…\e",
            r"\0\s[35]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Bust'][1][0] = [
            r"\0\s[1]呃…\w9\w9那、那个？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Bust'][1][1] = [
            r"\0\s[1]嗯…\w9\w9啊…\e",
            r"\0\s[1]那、\w9那个…\e",
            r"\0\s[1]那个…\w9那个…\e",
            r"\0\s[1]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Bust'][2][0] = [
            r"\0\s[1]耶…\w9\w9那、那个？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Bust'][2][1] = [
            r"\0\s[1]嗯…\w9\w9啊…\e",
            r"\0\s[1]那、\w9那个…\e",
            r"\0\s[1]…\w9…\w9…\e",
            r"\0\s[1]那个…\w9那个…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Hand'][0][0] = [
            r"\0\s[0]…\w9…\w9…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseTouch]['Hand'][0][1] = [
            r"\0\s[29]…\w9…\w9…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[29]啊…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Head'][0][0] = [
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜…\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[3]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Head'][1][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\s[3]\n真过分…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\s[7]\n为什么…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Head'][2][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\s[9]\n呜呜…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\nもう、\w9\w5\s[9]请不要故意欺负我…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Face'][0][0] = [
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜…\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[3]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Face'][1][0] = [
            r"\0\![raise,OnPlay,se_02.wav]\s[1]呀啊…\e",
            r"\0\![raise,OnPlay,se_02.wav]\s[3]好痛…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Face'][2][0] = [
            r"\0\![raise,OnPlay,se_02.wav]\s[33]咿呀…\w9\w9\s[1]\n这…\e",
            r"\0\![raise,OnPlay,se_02.wav]\s[33]呜嗯…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Bust'][0][0] = [
            r"\0\s[23]…\w9\w9你到底要干什么…\e",
            r"\0\s[23]\w9\w9找死！！！\w9\w9\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[35]呜…\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[35]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Bust'][1][0] = [
            r"\0\![raise,OnPlay,se_04.wav]\s[4]那…\w9\w9\w9那个…\e",
            r"\0\![raise,OnPlay,se_04.wav]\s[2]咿呀…\w9\w9\s[1]\n…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Bust'][1][1] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9\w9\s[9]不、\w9不行啦…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Bust'][1][2] = [
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜！\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜…\w9好痛…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9讨厌…\e",
            r"\0\s[6]哼…\e",
            r"\0\s[23]…\w9\w9你到底要干什么…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Bust'][2][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9\w9那个…\e",
            r"\0\![raise,OnPlay,se_02.wav]\s[2]咿呀…\w9\w9\s[1]\n…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Bust'][2][1] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9\w9\s[9]不、\w9不可以…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Bust'][2][2] = [
            r"\0\![raise,OnPlay,se_03.wav]\0\s[3]呜！\e",
            r"\0\![raise,OnPlay,se_03.wav]\0\s[3]呜…\w9好痛…\e",
            r"\0\![raise,OnPlay,se_01.wav]\0\s[1]啊…\w9\w9讨厌…\e",
            r"\0\s[22]%(username)想吃枪子儿吗？\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Hand'][0][0] = [
            # keep empty for show main menu
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Hand'][1][0] = [
            r"\0\s[26]？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_MouseDoubleClick]['Hand'][2][0] = [
            r"\0\![raise,OnPlay,se_04.wav]\s[2]哇…\w9\w9\s[1]\n这…\e",
            r"\0\![raise,OnPlay,se_04.wav]\s[2]哇…\w9\w9\s[29]\n…\w9…\w9…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.Shell_WheelEvent]['Hand'][0][0] = [
            r"\0\s[3]…\w9…\w9…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.Shell_WheelEvent]['Hand'][0][1] = [
            r"\0\s[29]…\w9…\w9…\e",
            r"\0\s[29]\![raise,OnPlay,se_05.wav]行きます\w9…",
            r"\0\s[26]要带橘花去哪呢？\e",
        ]

        # ############################################################
        self._touchtalk[TOWA][GhostEvent.Shell_MouseDoubleClick]['Head'][0][0] = [

        ]
        self._touchtalk[TOWA][GhostEvent.Shell_MouseDoubleClick]['Tail'][0][0] = [
            r"\1\s[12]…\w9…\w9…\w9\s[10]\e",
            r"\1\s[12]动物保护团体的那些家伙会生气喔。\e",
            r"\1\s[12]\![move,-100,,500,me]\e",
        ]
        self._touchtalk[TOWA][GhostEvent.Shell_MouseTouch]['Head'][0][0] = \
        self._touchtalk[TOWA][GhostEvent.Shell_WheelEvent]['Head'][0][0] = [
            r"\1\s[12]…\w9…\w9…\w9\s[10]\e",
            r"\1\s[10]呣…\e",
            r"\1\s[10]嗯～。\w9\w9\n算了、\w9随你高兴吧。\e",
            r"\1\s[10]呼噜呼噜…………",
        ]
        self._touchtalk[TOWA][GhostEvent.Shell_MouseTouch]['Tail'][0][0] = \
        self._touchtalk[TOWA][GhostEvent.Shell_WheelEvent]['Tail'][0][0] = [
            r"\1\s[10]啊啊啊…\w9\s[12]\n给我停下来！\e",
            r"\1\s[10]呜～。\e",
            r"\1\s[12]咕嘎啊啊～！\w9\w9\n不准碰！\e",
            r"\1\s[12]喵了个咪的，你不知道猫很不喜欢被人摸尾巴吗？",
        ]

    def getAITalk(self):
        aitalk = [
            r"\0\s[9]…\w9\w5怎么了吗？\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]那个…\e",
        ]
        return random.choice(aitalk)
