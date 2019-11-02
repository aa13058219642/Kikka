# coding=utf-8
import random
import logging
import datetime

from PyQt5.QtWidgets import QWidget, QPushButton, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout

import kikka
from kikka_const import SurfaceEnum, GhostEvent
from ghost_ai import GhostAI

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
        self.initLayout()
        self.initTalk()
        self.initMenu()

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

    def initLayout(self):

        self._mainLayout = QVBoxLayout()
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._stackedLayout = QStackedLayout()
        self._topLayout = QVBoxLayout()

        # 0 main Layout
        self._mainLayout.addLayout(self._topLayout)
        self._mainLayout.addLayout(self._stackedLayout)

        # 1.0 top layout
        self._toplabel = QLabel("Hello")
        self._toplabel.setObjectName('Hello')
        self._topLayout.addWidget(self._toplabel)

        # 1.2 tab layout
        self._tabLayout = QHBoxLayout()
        self._topLayout.addLayout(self._tabLayout)

        # 1.2.1 tab button
        p1 = QPushButton("page1")
        p2 = QPushButton("page2")
        p3 = QPushButton("page3")
        p1.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(0))
        p2.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(1))
        p3.clicked.connect(lambda: self._stackedLayout.setCurrentIndex(2))
        self._tabLayout.addWidget(p1)
        self._tabLayout.addWidget(p2)
        self._tabLayout.addWidget(p3)

        # 2.0 gird layouts
        self._girdlayouts = []
        for i in range(3):
            girdlayout = QGridLayout()
            self._girdlayouts.append(girdlayout)

            page = QWidget()
            page.setLayout(girdlayout)
            self._stackedLayout.addWidget(page)

        callback_ResizeWindow = lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, GhostEvent.CustomEvent, 'ResizeWindow', {'bool':False, 'SoulID':KIKKA}))
        callback_CloseDialog = lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, GhostEvent.CustomEvent, 'CloseDialog', {'bool':False, 'SoulID':KIKKA}))

        # 2.1 page1
        for i in range(3):
            girdlayout = self._girdlayouts[i]
            for j in range(3):
                btn = QPushButton("move dialog%d(%d)" % (i, j))
                btn.clicked.connect(callback_ResizeWindow)
                girdlayout.addWidget(btn, j, 0)

                btn2 = QPushButton("close%d(%d)" % (i, j))
                btn2.clicked.connect(callback_CloseDialog)
                girdlayout.addWidget(btn2, j, 1)
            btn = QPushButton("move dialog%d(%d)" % (i, 5))
            btn.clicked.connect(callback_ResizeWindow)
            girdlayout.addWidget(btn, 5, 0)

        self.getSoul(KIKKA).getDialog().setMenuLayout(self._mainLayout)

        mainLayout = QVBoxLayout()
        btn1 = QPushButton("move dialog")
        btn1.clicked.connect(lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, GhostEvent.CustomEvent, 'ResizeWindow', {'bool':False, 'SoulID':TOWA})))

        btn2 = QPushButton("close")
        btn2.clicked.connect(lambda : self.emitGhostEvent(kikka.helper.makeGhostEventParam(self.ID, GhostEvent.CustomEvent, 'CloseDialog', {'bool':False, 'SoulID':TOWA})))
        mainLayout.addWidget(btn1)
        mainLayout.addWidget(btn2)
        self.getSoul(TOWA).getDialog().setMenuLayout(mainLayout)

    def ghostEvent(self, param):
        super().ghostEvent(param)

        istalking = self.touchTalk(param)
        if not istalking and param.eventType == GhostEvent.MouseDoubleClick:
            self.getSoul(param.data['SoulID']).getDialog().showMenu()

        if param.eventType == GhostEvent.CustomEvent:
            if param.eventTag == 'ResizeWindow':
                self.resizeWindow(param)
            elif param.eventTag == 'CloseDialog':
                self.closeDlg(param)

    def changeShell(self, shellID):
        logging.debug("Please don't peek at me to change clothes!")
        super().changeShell(shellID)

    # ########################################################################################################
    def resizeWindow(self, param):
        dlg = kikka.core.getGhost(param.ghostID).getSoul(param.data['SoulID']).getDialog()
        dlg.setFramelessWindowHint(param.data['bool'])

    def closeDlg(self, param):
        kikka.core.getGhost(param.ghostID).getSoul(param.data['SoulID']).getDialog().hide()

    def onUpdate(self, updatetime):
        super().onUpdate(updatetime)
        self.onDatetime()

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
                if now.hour == 0:
                    script = r"\0凌晨12点了呢.又是新的一天～\e"
                elif now.hour >= 1 and now.hour <= 4:
                    script = random.choice([
                        r"\0%(hour)点了.%(username)还不睡吗\e",
                        r"\0%(hour)点了.%(username)不睡吗？熬夜会变笨的喔\e"
                    ])
                elif now.hour in [5, 6]:
                    script = random.choice([
                        r"\0%(hour)点了..要去看日出吗\e",
			            r"\0呼哈～唔..%(hour)点了\e"
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
                        r"\012点了.午餐时间～\e"
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
                elif now.hour >= 19 and now.hour <= 23:
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
        sid = param.data['SoulID']
        phase = self.getPhase()

        if param.eventTag not in self._touch_count[sid].keys():
            self._touch_count[sid][param.eventTag] = 0

        # touchtalk[soulID][eventType][eventTag][phase][touchcount]
        if sid in self._touchtalk.keys() \
        and param.eventType in self._touchtalk[sid].keys() \
        and param.eventTag in self._touchtalk[sid][param.eventType].keys():
            if phase not in self._touchtalk[sid][param.eventType].keys():
                phase = 0

            if len(self._touchtalk[sid][param.eventType][param.eventTag]) <= 0 \
            and len(self._touchtalk[sid][param.eventType][param.eventTag][phase]) <= 0:
                return False

            count = self._touch_count[sid][param.eventTag] % len(self._touchtalk[sid][param.eventType][param.eventTag][phase])
            if len(self._touchtalk[sid][param.eventType][param.eventTag][phase][count]) <= 0:
                return False

            script = random.choice(self._touchtalk[sid][param.eventType][param.eventTag][phase][count])
            self._touch_count[sid][param.eventTag] += 1
            self.talk(script)
            return True
        return False

    def initTalk(self):
        # touchtalk[soulID][eventType][eventTag][phase][touchcount]
        self._touchtalk = {
            KIKKA: {
                GhostEvent.MouseTouch: {
                    'Head': {0: {}, 1: {}, 2: {}},
                    'Face': {0: {}},
                    'Bust': {0: {}, 1: {}, 2: {}},
                    'Hand': {0: {}},
                },
                GhostEvent.MouseDoubleClick: {
                    'Head': {0: {}, 1: {}, 2: {}},
                    'Face': {0: {}, 1: {}, 2: {}},
                    'Bust': {0: {}, 1: {}, 2: {}},
                    'Hand': {0: {}, 1: {}, 2: {}},
                },
                GhostEvent.WheelEvent: {
                    'Hand': {0: {}, 1: {}},
                }
            },
            TOWA: {
                GhostEvent.MouseTouch: {
                    'Head': {0: {}},
                    'Tail': {0: {}},
                },
                GhostEvent.MouseDoubleClick: {
                    'Head': {0: {}},
                    'Tail': {0: {}},
                },
                GhostEvent.WheelEvent: {
                    'Head': {0: {}},
                    'Tail': {0: {}},
                },
            }
        }

        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][0][0] = [
            r"\0\s[1]怎、\w9\w5怎么了吗？\e",
            r"\0\s[2]呀…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]这个…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][0][1] = [
            r"\0\s[9]…\w9…\w9…\e",
            r"\0\s[33]…哎呀…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][1][0] = [
            r"\0\s[1]怎、\w9\w5怎么了吗？\e",
            r"\0\s[2]呀…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]这个…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][1][1] = [
            r"\0\s[1]…\w9嗯？\e",
            r"\0\s[1]那个…\w9\s[1]这个…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][1][2] = [
            r"\0\s[1]%(username)…\e",
            r"\0\s[1]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][1][3] = [
            r"\0\s[29]…\w9谢谢。\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][1][4] = [
            r"\0\s[1]那个…\w9已经可以了…\e",
            r"\0\s[1]那个…\w9我没关系的…\e",
            r"\0\s[1]…\w9…\w9…\e",
            r"\0\s[1]唔…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][2][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\e",
            r"\0\s[26]…\w9…\w9…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]那个…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][2][1] = [
            r"\0\s[1]谢…\w9谢谢…\e",
            r"\0\s[1]%(username)…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][2][2] = [
            r"\0\s[29]…\w9…\w9…\e",
            r"\0\s[1]这个…\w9\w9我的头发、\w9怎么了吗？\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][2][3] = [
            r"\0\s[29]…\w9那个。\w9\w9\s[1]\n啊…\w9没事…\e",
            r"\0\s[1]那、\w9那个…\w9\w9\n我会害羞的。\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Head'][2][4] = [
            r"\0\s[29]嗯…\e",
            r"\0\s[1]…\w9…\w9…\e",
            r"\0\s[1]那个…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9唔…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Face'][0][0] = [
            r"\0\s[6]嗯。\w9\w9\s[0]\n怎么了？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Face'][0][1] = [
            r"\0\s[6]嗯？\w9\w9\s[20]\n那个、\w9我脸上有什么东西吗？\e",
            r"\0\s[6]唔嗯…\w9\w9\s[2]那个、\w9怎么了？\e",
            r"\0\s[21]好痒喔。\e",
            r"\0\s[6]唔…\w9\w9\s[2]\n…\w9…\w9…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Bust'][0][0] = [
            r"\0\s[35]…\w9…\w9…\1\s[12]你就这么喜欢摸女生胸部吗……\0\e",
            r"\0\s[35]唔…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[35]啊…\e",
            r"\0\s[35]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Bust'][1][0] = [
            r"\0\s[1]呃…\w9\w9那、那个？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Bust'][1][1] = [
            r"\0\s[1]嗯…\w9\w9啊…\e",
            r"\0\s[1]那、\w9那个…\e",
            r"\0\s[1]那个…\w9那个…\e",
            r"\0\s[1]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Bust'][2][0] = [
            r"\0\s[1]耶…\w9\w9那、那个？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Bust'][2][1] = [
            r"\0\s[1]嗯…\w9\w9啊…\e",
            r"\0\s[1]那、\w9那个…\e",
            r"\0\s[1]…\w9…\w9…\e",
            r"\0\s[1]那个…\w9那个…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Hand'][0][0] = [
            r"\0\s[0]…\w9…\w9…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseTouch]['Hand'][0][1] = [
            r"\0\s[29]…\w9…\w9…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[29]啊…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Head'][0][0] = [
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜…\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[3]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Head'][1][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\s[3]\n真过分…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\s[7]\n为什么…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Head'][2][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\s[9]\n呜呜…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[33]啊…\w9\w9\w9\nもう、\w9\w5\s[9]请不要故意欺负我…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Face'][0][0] = [
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜…\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[3]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Face'][1][0] = [
            r"\0\![raise,OnPlay,se_02.wav]\s[1]呀啊…\e",
            r"\0\![raise,OnPlay,se_02.wav]\s[3]好痛…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Face'][2][0] = [
            r"\0\![raise,OnPlay,se_02.wav]\s[33]咿呀…\w9\w9\s[1]\n这…\e",
            r"\0\![raise,OnPlay,se_02.wav]\s[33]呜嗯…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Bust'][0][0] = [
            r"\0\s[23]…\w9\w9你到底要干什么…\e",
            r"\0\s[23]\w9\w9找死！！！\w9\w9\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[35]呜…\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[35]…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Bust'][1][0] = [
            r"\0\![raise,OnPlay,se_04.wav]\s[4]那…\w9\w9\w9那个…\e",
            r"\0\![raise,OnPlay,se_04.wav]\s[2]咿呀…\w9\w9\s[1]\n…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Bust'][1][1] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9\w9\s[9]不、\w9不行啦…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Bust'][1][2] = [
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜！\e",
            r"\0\![raise,OnPlay,se_03.wav]\s[3]呜…\w9好痛…\e",
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9讨厌…\e",
            r"\0\s[6]哼…\e",
            r"\0\s[23]…\w9\w9你到底要干什么…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Bust'][2][0] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9\w9那个…\e",
            r"\0\![raise,OnPlay,se_02.wav]\s[2]咿呀…\w9\w9\s[1]\n…\w9…\w9…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Bust'][2][1] = [
            r"\0\![raise,OnPlay,se_01.wav]\s[1]啊…\w9\w9\w9\s[9]不、\w9不可以…\e",
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Bust'][2][2] = [
            r"\0\![raise,OnPlay,se_03.wav]\0\s[3]呜！\e",
            r"\0\![raise,OnPlay,se_03.wav]\0\s[3]呜…\w9好痛…\e",
            r"\0\![raise,OnPlay,se_01.wav]\0\s[1]啊…\w9\w9讨厌…\e",
            r"\0\s[22]%(username)想吃枪子儿吗？\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Hand'][0][0] = [
            # keep empty for show main menu
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Hand'][1][0] = [
            r"\0\s[26]？\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.MouseDoubleClick]['Hand'][2][0] = [
            r"\0\![raise,OnPlay,se_04.wav]\s[2]哇…\w9\w9\s[1]\n这…\e",
            r"\0\![raise,OnPlay,se_04.wav]\s[2]哇…\w9\w9\s[29]\n…\w9…\w9…\e",
        ]

        # ############################################################
        self._touchtalk[KIKKA][GhostEvent.WheelEvent]['Hand'][0][0] = [
            r"\0\s[3]…\w9…\w9…\e"
        ]
        self._touchtalk[KIKKA][GhostEvent.WheelEvent]['Hand'][0][1] = [
            r"\0\s[29]…\w9…\w9…\e",
            r"\0\s[29]\![raise,OnPlay,se_05.wav]行きます\w9…",
            r"\0\s[26]要带橘花去哪呢？\e",
        ]

        # ############################################################
        self._touchtalk[TOWA][GhostEvent.MouseDoubleClick]['Head'][0][0] = [

        ]
        self._touchtalk[TOWA][GhostEvent.MouseDoubleClick]['Tail'][0][0] = [
            r"\1\s[12]…\w9…\w9…\w9\s[10]\e",
            r"\1\s[12]动物保护团体的那些家伙会生气喔。\e",
            r"\1\s[12]\![move,-100,,500,me]\e",
        ]
        self._touchtalk[TOWA][GhostEvent.MouseTouch]['Head'][0][0] = \
        self._touchtalk[TOWA][GhostEvent.WheelEvent]['Head'][0][0] = [
            r"\1\s[12]…\w9…\w9…\w9\s[10]\e",
            r"\1\s[10]呣…\e",
            r"\1\s[10]嗯～。\w9\w9\n算了、\w9随你高兴吧。\e",
            r"\1\s[10]呼噜呼噜…………",
        ]
        self._touchtalk[TOWA][GhostEvent.MouseTouch]['Tail'][0][0] = \
        self._touchtalk[TOWA][GhostEvent.WheelEvent]['Tail'][0][0] = [
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
