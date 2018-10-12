import logging

from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction


class SystemMenu(QMenu):
    def __init__(self, parent):
        QMenu.__init__(self)
        self._parent = parent

        self.createAction()

    def createAction(self):
        self.addAction(QAction('Exit', self._parent, triggered=self.onExit))

    def onExit(self):
        logging.info("SystemMenu-onExit")
        from .kikka import KikkaApp
        KikkaApp.get_instance().exitApp()
        # sys.exit(0)
        pass
