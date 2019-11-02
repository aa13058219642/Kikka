

import time
import logging
import datetime

import kikka
from ghostbase import GhostBase


class GhostAI(GhostBase):
    def __init__(self, ghost_id=-1, name=''):
        GhostBase.__init__(self, ghost_id, name)
        self._last_talk_time = self._now()
        self._talk_speed = 50
        self._ending_wait = 5000

        self._istalking = False
        self._tokens = []
        self._current_talk_soul = 0
        self._script_wait = 0
        self._variables = {}

    def init(self):
        super().init()

        self._variables['selfname'] = self.name
        self._variables['selfname2'] = ''
        self._variables['keroname'] = ''

        self._variables['username'] = self.memoryRead('username', '')
        if self._variables['username'] == '':
            self._variables['username'] = 'A.A君'

    def execSakuraScript(self, updatetime):
        if self._script_wait > 0:
            self._script_wait -= updatetime
            return

        if self._istalking is True and len(self._tokens) <= 0:
            self._istalking = False
            self._last_talk_time = self._now()

            for sid in range(self.getSoulCount()):
                self.getSoul(sid).setDefaultSurface()
                self.getSoul(sid).getDialog().hide()
            return

        while len(self._tokens) > 0:
            token = self._tokens.pop(0)
            if token[0] == '':
                if len(token[1]) > 0:
                    self.onTalk(token[1][0])
                    if len(token[1]) > 1:
                        self._tokens.insert(0, ('', token[1][1:]))
                    self._script_wait = self._talk_speed
                    break
                else:
                    continue
            elif '\\0' == token[0]:
                self._current_talk_soul = 0
                continue
            elif '\\1' == token[0]:
                self._current_talk_soul = 1
                continue
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
            elif '%' == token[0][0]:
                command = token[0][1:]
                now = datetime.datetime.now()
                if command == 'month':
                    text = str(now.minute)
                elif command == 'day':
                    text = str(now.day)
                elif command == 'hour':
                    text = str(now.hour)
                elif command == 'hour12':
                    text = str(now.hour%12)
                elif command == 'minute':
                    text = str(now.minute)
                elif command == 'second':
                    text = str(now.second)

                elif command == 'screenwidth':
                    w, h = kikka.helper.getScreenResolution()
                    text = str(w)
                elif command == 'screenheight':
                    w, h = kikka.helper.getScreenResolution()
                    text = str(h)

                elif command in self._variables:
                    text = self._variables[command]
                elif command == 'property':
                    text = str(kikka.core.getProperty(token[1]))
                else:
                    text = ''
                    logging.warning('unknow sakura script command: %s %s' % (token[0], token[1]))
                if len(text) > 1:
                    self._tokens.insert(0, ('', text))
            else:
                logging.warning('unknow sakura script command: %s %s' % (token[0], token[1]))
        pass

    def onUpdate(self, updatetime):
        super().onUpdate(updatetime)

        # if self._istalking is False and self._now() - self._last_talk_time>3000:
        #     self.talk(self.getAITalk())

        self.execSakuraScript(updatetime)

    def talk(self, script):
        if script is None or script == '':
            return

        ss = SakuraScript(script)
        self._tokens = ss.tokens
        self.getSoul(self._current_talk_soul).getDialog().talkClear()
        self._last_talk_time = self._now()
        self._istalking = True
        self._script_wait = 0

    def isTalking(self):
        return self._istalking

    def _now(self):
        return time.clock() * 1000

    def onTalk(self, message):
        dlg = self.getSoul(self._current_talk_soul).getDialog()
        dlg.showTalk()
        dlg.onTalk(message, self._talk_speed)

    def getAITalk(self):
        return ''


class SakuraScript():
    def __init__(self, script=''):
        self.tokens = []
        self.question_record = {}
        self.last_talk_exiting_surface = {}

        try:
            self.unserialize(script)
        except:
            logging.error("ERROR SakuraScript: %s" % script)
            raise

    def isdigit(self, uchar):
        """判断一个unicode是否是数字"""
        return uchar >= u'\u0030' and uchar <= u'\u0039'

    def aredigits(self, string):
        p = 0
        if string[p] == '-':
            p += 1
        if string[p] == '\0':
            return False
        while string[p] != '\0':
            if not self.isdigit(string[p]):
                return False
            p += 1
        return True

    def isalpha(self, uchar):
        """判断一个unicode是否是英文字母"""
        return (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a')

    def serialize(self):
        script = ''
        for i in self.tokens:
            script += i[0] + i[1]
        return script

    def unserialize(self, script):
        if script == '':
            return

        vec = []
        acum = ''
        content = False
        is_first_question = True
        last_speaker = 0

        p = 0
        while p < len(script):
            c = script[p]
            p += 1

            if c == '\\' or c == '%':
                if script[p] == '\\' or script[p] == '%':
                    acum += c + script[p]
                    p += 1
                    continue

                start = p
                while p < len(script) and (self.isalpha(script[p]) or self.isdigit(script[p]) or script[p] in ['!', '*', '&', '?', '_']):
                    p += 1
                command = script[start:p]
                if p < len(script) and c == '%' and script[p] == '(':
                    p += 1
                    s = p
                    while p < len(script) and script[p] != ')':
                        if script[p] == '\\' and script[p + 1] == ')':
                            p += 1
                        p += 1
                    command += script[s:p]
                    p += 1

                option = ''
                if p < len(script) and script[p] == '[':
                    p += 1
                    s = p
                    while p < len(script) and script[p] != ']':
                        if script[p] == '\\' and script[p+1] == ']':
                            p += 1
                        p += 1
                    option = script[s:p]
                    p += 1


                if command == 'q' and option != '' and ',' in option:
                    if is_first_question:
                        self.question_record.clear()
                        is_first_question = False

                    svec = option.split(',')
                    if len(svec) == 1:
                        svec.append('')
                    slabel = svec[0]
                    sid = svec[1]
                    if sid.find('on') != 0 and sid.find('On') != 0 \
                        and sid.find('http://') != 0 and sid.find('https://') != 0:
                        if sid.find('script:') != 0 and sid.find('\"script:') != 0:
                            count = len(self.question_record)
                            self.question_record[sid] = (count, slabel)

                            vec_id = []
                            if len(sid) == 0:
                                vec_id.append("")
                            else:
                                vec_id = sid.split('\\1')

                            byte1_dlmt = chr(1) + chr(0)
                            option = slabel + ',' + vec_id[0] + byte1_dlmt + slabel + byte1_dlmt + str(count)
                            for i in range(2, len(svec)):
                                option += ',' + svec[i]
                elif command == '0' or command == 'h':
                    last_speaker = 0
                elif command == '1' or command == 'u':
                    last_speaker = 1
                elif command == 'p' and self.aredigits(option):
                    last_speaker = int(option)
                    if last_speaker <= 1:
                        command = '0' if option == '0' else '1'
                        option = ''
                elif command == 's' and not option.isspace():
                    self.last_talk_exiting_surface[last_speaker] = int(option)
                elif len(command) == 2 and command[0] == 's' and self.isdigit(command[1]):
                    self.last_talk_exiting_surface[last_speaker] = command[1] - '0'

                if len(acum) > 0:
                    vec.append(('', acum))

                vec.append((c + command, '') if option == '' else (c + command, option))
                acum = ''

                if command not in ['0', '1', 'h', 'u', 'p', 'n', 'w', '_w', 'e']:
                    content = True
            else:
                content = True
                acum += c
        pass  # exit while

        if len(acum) > 0:
            vec.append(('', acum))

        if not content:
            return False

        self.tokens = vec
