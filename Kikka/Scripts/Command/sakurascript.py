

class SakuraScript():
    def __init__(self, script=''):
        self._tokens = []
        self.unserialize(script)

    def isdigit(self, uchar):
        """判断一个unicode是否是数字"""
        return uchar >= u'\u0030' and uchar <= u'\u0039'

    def isalpha(self, uchar):
        """判断一个unicode是否是英文字母"""
        return (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a')

    def serialize(self):
        script = ''
        for i in self._tokens:
            script += i[0] + i[1]
        return script

    def unserialize(self, script):
        fragment = ''
        p = 0
        while p < len(script):
            c = script[p]
            p += 1

            if c == '\\' or c == '%':
                if p < len(script) and (script[p] == '\\' or script[p] == '%'):
                    fragment += c + script[p]
                    p += 1
                    continue

                if fragment != '':
                    self._tokens.append(('', fragment))
                    fragment = ''

                s = p
                while p < len(script) and (self.isalpha(script[p]) or self.isdigit(script[p]) or script[p] in ['!', '*', '&', '?', '_']):
                    p += 1
                command = script[s:p]

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

                self._tokens.append((c + command, option))
            else:
                fragment += c
        pass  # exit for

        if fragment != '':
            self._tokens.append(('', fragment))

    def getTokens(self):
        return self._tokens

if __name__ == '__main__':
    s0 = SakuraScript(r"\0\e")
    s1 = SakuraScript(r"\0\s[9]…\w9\w5怎么了吗？\e")
    s2 = SakuraScript(r"\0\![raise,OnPlay,se_01.wav]\s[2]啊…\w9\w9\s[1]那个…\e")
    s3 = SakuraScript(r"\0\s[6]虽然很理所当然…\w9\w9\1\s[10]唔？\w9\w9\0\s[0]\n\n[half]少年(Littleboy)和胖子(Fatman)\n是不同种类的炸弹。\w9\w9\1\s[10]\n\n[half]为什么、\w5会理所当然啊？\w9\w9\0\s[30]\n\n[half]名字不一样、\w9\s[0]\n如果是同样的东西的话应该就没有必要投下两次。\e")
    s4 = SakuraScript(r"\0\s[0]指那些表面很好人，内心很坏思想的人，动漫专业术语之一，一般用在开玩笑等场所，是褒义词...我其实,很腹黑的哦\n\n\q[◇果然腹黑, ForcedClose_4]\n\q[◇小腹黑猪, ForcedCloseCancel_4]\e")
    s5 = SakuraScript(r"\0\s[0]\1\s[10]\0……ねぇ、\_w[30]ウメムチくん。\_w[42]\w9\n\_w[6]\1\cなんですか？＜\_w[42]\n\_w[6]\0ウメムチくんって、\_w[54]\w9\w9\n\0\s[-1]\b[-1]\_w[6]\1\s[-1]\b[-1]\n\_w[6]\0\s[2]\_w[700]\1\n\n\n\n\n\n\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,66,66,す]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,64,64,す]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,138,66,っ]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,136,64,っ]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,210,66,ぱ]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,208,64,ぱ]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,282,66,い]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,280,64,い]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,354,66,も]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,352,64,も]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,426,66,の]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,424,64,の]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,498,66,と]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,496,64,と]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,570,66,か]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,568,64,か]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,642,66,‥]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,640,64,‥]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,714,66,‥]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,712,64,‥]\n\w4\n\n\w9\w5\1\n\n\n\n\n\n\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,98,138,好]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,96,136,好]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,170,138,き]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,168,136,き]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,242,138,か]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,240,136,か]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,314,138,な]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,312,136,な]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,386,138,ぁ]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,384,136,ぁ]\n\w4\n\1\n\![raise,OnDirectSaoriCall,font_color,255,0,255]\n\![raise,OnDirectSaoriCall,text,458,138,？]\n\![raise,OnDirectSaoriCall,font_color,255,240,240]\n\![raise,OnDirectSaoriCall,text,456,136,？]\n\w4\n\n\_w[2500]\![raise,OnDirectSaoriCall,clear]\n\_w[6]\0\c\s[0]\n\_w[6]\1\c\s[1000]\_w[1500]えぇ、\_w[18]\w9好きですよ。\_w[36]＜\_w[6]\n\_w[6]\0\c……そう。\_w[30]\w9\w9\n\n……良かった。\_w[42]\e")
