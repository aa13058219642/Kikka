
import os
import sys
from win32api import GetSystemMetrics

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


PATH_ROOT = 0
PATH_SCRIPTS = 1
PATH_BIN = 11
PATH_MOUDLES = 12
PATH_RESOURCES = 2
PATH_SHELL = 21

def getPath(tag):
    path = ''
    if tag == PATH_ROOT: path = sys.path[0]
    elif tag == PATH_SCRIPTS: path = os.path.join(sys.path[0], 'Scripts')
    elif tag == PATH_BIN: path = os.path.join(sys.path[0], 'Scripts/Bin')
    elif tag == PATH_MOUDLES: path = os.path.join(sys.path[0], 'Scripts/Moudles')
    elif tag == PATH_RESOURCES: path = os.path.join(sys.path[0], 'Resources')
    elif tag == PATH_SHELL: path = os.path.join(sys.path[0], 'Resources/Shell')
    return path

def getScreenResolution():
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    return w, h