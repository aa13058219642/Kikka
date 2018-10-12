
import os
import sys


class Helper:
    def checkEncoding(filepath):
        CODES = ['UTF-8', 'GBK', 'Shift-JIF', 'GB18030', 'BIG5','UTF-16']

        # UTF-8 BOM前缀字节
        UTF_8_BOM = b'\xef\xbb\xbf'

        f = None
        b = ""
        filecode = None
        for code in CODES:
            try:
                f = open(filepath, 'rb')
                b = f.read()
                b.decode(encoding=code)
                f.close()
                filecode = code
                break
            except Exception:
                f.close()
                continue

        if 'UTF-8' == filecode and b.startswith(UTF_8_BOM):
            filecode = 'UTF-8-SIG'

        if filecode == None:
            raise SyntaxError('Uknow file encoding: %s' % filepath)

        return filecode



