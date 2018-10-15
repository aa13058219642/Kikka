import sys
import signal
import logging
import logging.handlers


from kikka import KikkaApp


def runApp():
    # logging level (low to hight): 
    # CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    initLogging(logging.INFO)

    try:
        app = KikkaApp.get_instance()
        sys.exit(app.exec_())
    except SystemExit:
        pass
    except Exception:
        logging.exception('KikkaApp: run time error')
        raise SyntaxError('run time error')


def initLogging(level):
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(filename)s[line:%(lineno)d] ''%(levelname)s: %(message)s')
    file_handler = logging.handlers.RotatingFileHandler('kikka.log', mode='a', maxBytes=1.01*1024*1024, backupCount=1, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)


if __name__ == '__main__':
    runApp()
