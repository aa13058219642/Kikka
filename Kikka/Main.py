# coding=utf-8
import sys
import logging
import logging.handlers

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

def awake():
    # logging level (low to hight):
    # CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    file_handler = setLogging(logging.INFO)
    sys.excepthook = handle_exception

    # init all Singletion class
    import kikka

    # set debug mode
    if '-c' in sys.argv:
        kikka.memory.isDebug = True
        kikka.app.isDebug = True
        kikka.core.isDebug = True
        file_handler.setLevel(logging.DEBUG)

    kikka.app.awake()

    #font = QFont(kikka.helper.getPath(kikka.helper.PATH_RESOURCES) + "InconsolataGo-Regular.ttf", 10)
    #QApplication.instance().setFont(font)
    pass

def setLogging(level):
    if level == logging.DEBUG or level == logging.NOTSET:
        fmt = '%(asctime)s | line:%(lineno)-4d %(filename)-20s %(funcName)-30s | %(levelname)-8s| %(message)s'
        logging.basicConfig(level=level, format=fmt)
        file_handler = logging.handlers.RotatingFileHandler(
            'kikka.log', mode='w', maxBytes=5.01*1024*1024, backupCount=0, encoding='utf-8')
        formatter = logging.Formatter(fmt)
    else:
        fmt = '%(asctime)s | line:%(lineno)-4d %(filename)-20s | %(levelname)-8s| %(message)s'
        logging.basicConfig(level=level, format=fmt)
        file_handler = logging.handlers.RotatingFileHandler(
            'kikka.log', mode='a', maxBytes=1.01*1024*1024, backupCount=0, encoding='utf-8')
        formatter = logging.Formatter(fmt)

    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)
    return file_handler


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Run time error\n%s: %s\n%s"%(exc_type.__name__, exc_value, "-"*40), exc_info=(exc_type, exc_value, exc_traceback))
    logging.info("\n%s\n%s"%("-"*120, "-"*120))


def run():
    try:
        qapp = QApplication(sys.argv)
        awake()
        sys.exit(qapp.exec_())
    except SystemExit:
        pass


if __name__ == '__main__':
    run()
