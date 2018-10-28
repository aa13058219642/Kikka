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
    import kikkahelper

    # set debug
    if '-c' in sys.argv:
        kikka.memory.isDebug = True
        kikka.app.isDebug = True
        kikka.core.isDebug = True

    # start
    shellpath = kikkahelper.getPath(kikkahelper.PATH_SHELL)
    kikka.memory.awake()
    kikka.shell.loadAllShell(shellpath)

    import mainmenu
    # kikka.menu.setMenu(mainmenu.createTestMenu())
    kikka.menu.setMenu(mainmenu.createMainMenu())
    #kikka.menu.getTestMenu()
    kikka.core.start()
    kikka.app.start()

    kikka.core.updateMenu()
    pass


def setLogging(level):
    if level == logging.DEBUG or level == logging.NOTSET:
        logging.basicConfig(level=level,
                            format='%(asctime)s %(filename)s %(funcName)s[line:%(lineno)d] ''%(levelname)s: %(message)s')
        file_handler = logging.handlers.RotatingFileHandler(
            'kikka.log', mode='a', maxBytes=5.01*1024*1024, backupCount=1, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(filename)s%(funcName)s[line:%(lineno)d] %(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=level,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] ''%(levelname)s: %(message)s')
        file_handler = logging.handlers.RotatingFileHandler(
            'kikka.log', mode='a', maxBytes=1.01*1024*1024, backupCount=1, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s')

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
