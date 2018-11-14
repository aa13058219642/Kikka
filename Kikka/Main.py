# coding=utf-8
import sys
import logging
import logging.handlers

from PyQt5.QtWidgets import QApplication


def awake():
    # logging level (low to hight):
    # CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    setLogging(logging.INFO)

    # init all Singletion class
    import kikka

    # set debug mode
    if '-c' in sys.argv:
        kikka.memory.isDebug = True
        kikka.app.isDebug = True
        kikka.core.isDebug = True

    # start
    kikka.memory.awake()
    kikka.shell.loadAllShell(kikka.helper.getPath(kikka.helper.PATH_SHELL))
    kikka.balloon.loadAllBalloon(kikka.helper.getPath(kikka.helper.PATH_BALLOON))

    import mainmenu
    kikka.core.start()
    kikka.app.start()

    kikka.core.addGhost(kikka.KIKKA)

    kikka.menu.setAppMenu(kikka.core.getGhost(kikka.KIKKA).getMenu(kikka.KIKKA))
    kikka.core.show()

    pass


def setLogging(level):
    if level == logging.DEBUG or level == logging.NOTSET:
        fmt = '%(asctime)s | line:%(lineno)-4d %(filename)-20s %(funcName)-30s | %(levelname)-8s| %(message)s'
        logging.basicConfig(level=level, format=fmt)
        file_handler = logging.handlers.RotatingFileHandler(
            'kikka.log', mode='a', maxBytes=5.01*1024*1024, backupCount=1, encoding='utf-8')
        formatter = logging.Formatter(fmt)
    else:
        fmt = '%(asctime)s | line:%(lineno)-4d %(filename)-20s | %(levelname)-8s| %(message)s'
        logging.basicConfig(level=level, format=fmt)
        file_handler = logging.handlers.RotatingFileHandler(
            'kikka.log', mode='a', maxBytes=1.01*1024*1024, backupCount=1, encoding='utf-8')
        formatter = logging.Formatter(fmt)

    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)


def run():
    try:
        qapp = QApplication(sys.argv)
        awake()
        sys.exit(qapp.exec_())
    except SystemExit:
        pass
    except Exception:
        logging.exception('Kikka: run time error')
        raise SyntaxError('run time error')


if __name__ == '__main__':
    run()
