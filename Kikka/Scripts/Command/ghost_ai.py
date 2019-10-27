

import time
import logging

from ghostbase import GhostBase
from sakurascript import SakuraScript


class GhostAI(GhostBase):
    def __init__(self, ghost_id=-1, name=''):
        GhostBase.__init__(self, ghost_id, name)
        self._last_talk_time = self._now()
        self._talk_speed = 50
        self._ending_wait = 3000

        self._istalking = False
        self._tokens = []
        self._current_talk_soul = 0
        self._script_wait = 0

    def getAITalk(self):
        return ''

    def execSakuraScript(self, updatetime):
        if self._script_wait > 0:
            self._script_wait -= updatetime
            return

        if self._istalking is True and len(self._tokens) <= 0:
            self._istalking = False
            self._last_talk_time = self._now()

            for sid in range(self.getSoulCount()):
                self.getSoul(sid).setSurface(0)
                self.getSoul(sid).getDialog().hide()
            return

        while len(self._tokens) > 0:
            token = self._tokens.pop(0)
            if token[0] == '' and len(token[1]) > 0:
                self.onTalk(token[1][0])
                if len(token[1]) > 1:
                    self._tokens.insert(0, ('', token[1][1:]))
                self._script_wait = self._talk_speed
                break
            elif '\\0' == token[0]:
                self._current_talk_soul = 0
            elif '\\1' == token[0]:
                self._current_talk_soul = 1
            elif '\\w' in token[0]:
                t = token[0][2:]
                self._script_wait = int(t) * self._talk_speed
                break
            elif '\\_w' in token[0]:
                self._script_wait = int(token[1])
                break
            elif '\\s' == token[0]:
                self.getSoul(self._current_talk_soul).setSurface(int(token[1]))
                break
            elif '\\e' == token[0]:
                self._tokens = []
                self._script_wait = self._ending_wait
                break
            else:
                logging.warning('unknow sakura script command: %s %s' % (token[0], token[1]))
        pass

    def update(self, updatetime):
        super().update(updatetime)

        # if self._istalking is False and self._now() - self._last_talk_time>3000:
        #     self.talk(self.getAITalk())

        self.execSakuraScript(updatetime)

    def talk(self, script):
        if script is None or script == '':
            return

        ss = SakuraScript(script)
        self._tokens = ss.getTokens()
        self.getSoul(self._current_talk_soul).getDialog().talkClear()
        self._last_talk_time = self._now()
        self._istalking = True
        self._script_wait = 0

    def _now(self):
        return time.clock() * 1000

    def onTalk(self, message):
        dlg = self.getSoul(self._current_talk_soul).getDialog()
        dlg.showTalk()
        dlg.onTalk(message, self._talk_speed)
