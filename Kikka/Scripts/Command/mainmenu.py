# coding=utf-8

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt


def createMainMenu():
    import kikka

    from kikka_menu import Menu
    parten = QWidget(flags=Qt.Dialog)
    mainmenu = Menu(parten, "Main")

    menu = Menu(mainmenu, "Shells")
    shells = kikka.shell.shells
    count = len(shells)
    for i in range(count):
        callbackfunc = lambda checked, a=i: kikka.shell.setCurShell(a)
        menu.addMenuItem(shells[i].name, callbackfunc)
    mainmenu.addSubMenu(menu)

    mainmenu.addSeparator()
    from kikka_app import KikkaApp
    callbackfunc = lambda: KikkaApp.this().exitApp()
    mainmenu.addMenuItem("Exit", callbackfunc)

    return mainmenu


def createTestMenu():
    from kikka_menu import Menu
    parten = QWidget(flags=Qt.Dialog)
    icon = QIcon(r"icon.ico")
    testmenu = Menu(parten, "Main")

    from kikka_app import KikkaApp
    callbackfunc = lambda: KikkaApp.this().exitApp()
    testmenu.addMenuItem("Exit", callbackfunc)
    testmenu.addSeparator()

    # MenuItem state ######################################################################
    menu = Menu(testmenu, "MenuItem state")
    testmenu.addSubMenu(menu)
    c = 16
    for i in range(c):
        text = str("%s-item%d" % (menu.title(), i))
        callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
        act = menu.addMenuItem(text, callbackfunc)

        if i >= c / 2: act.setDisabled(True); act.setText("%s-disable" % act.text())
        if i % 8 >= c / 4: act.setIcon(icon); act.setText("%s-icon" % act.text())
        if i % 4 >= c / 8: act.setCheckable(True); act.setText("%s-ckeckable" % act.text())
        if i % 2 >= c / 16: act.setChecked(True); act.setText("%s-checked" % act.text())

    # Separator  ######################################################################
    menu = Menu(testmenu, "Separator")
    testmenu.addSubMenu(menu)
    menu.addSeparator()
    c = 5
    for i in range(c):
        text = str("%s-item%d" % (menu.title(), i))
        callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
        menu.addMenuItem(text, callbackfunc)
        for j in range(i + 2): menu.addSeparator()

    # Multiple item  ######################################################################
    menu = Menu(testmenu, "Multiple item")
    testmenu.addSubMenu(menu)
    for i in range(100):
        text = str("%s-item%d" % (menu.title(), i))
        callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
        menu.addMenuItem(text, callbackfunc)

    # Long text item  ######################################################################
    menu = Menu(testmenu, "Long text item")
    testmenu.addSubMenu(menu)
    for i in range(5):
        text = str("%s-item%d " % (menu.title(), i)) * 20
        callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
        menu.addMenuItem(text, callbackfunc)

    # Submenu  ######################################################################
    menu = Menu(testmenu, "Submenu")
    testmenu.addSubMenu(menu)

    submenu = Menu(menu, "submenu1")
    menu.addSubMenu(submenu)
    m = submenu
    for i in range(8):
        next = Menu(testmenu, "submenu%d" % (i + 2))
        m.addSubMenu(next)
        m = next
    submenu = Menu(menu, "submenu2")
    menu.addSubMenu(submenu)

    m = submenu
    for i in range(8):
        for j in range(10):
            text = str("%s-item%d" % (m.title(), j))
            callbackfunc = lambda checked, a=j, b=text: _test_callback(a, b)
            m.addMenuItem(text, callbackfunc)
        next = Menu(testmenu, "submenu%d" % (i + 2))
        m.addSubMenu(next)
        m = next

    # Large menu  ######################################################################
    menu = Menu(testmenu, "Large menu")
    testmenu.addSubMenu(menu)
    for i in range(60):
        text = str("%s-item%d " % (menu.title(), i)) * 10
        callbackfunc = lambda checked, a=i, b=text: _test_callback(a, b)
        menu.addMenuItem(text, callbackfunc)
        if i % 5 == 0: menu.addSeparator()

    # Image test  ######################################################################
    testmenu.addSeparator()
    menu = Menu(testmenu, "MenuImage-normal")
    for i in range(32): text = " " * 54; menu.addMenuItem(text)
    testmenu.addSubMenu(menu)

    menu = Menu(testmenu, "MenuImage-bit")
    menu.addMenuItem('')
    testmenu.addSubMenu(menu)

    menu = Menu(testmenu, "MenuImage-small")
    for i in range(10): text = " " * 30; menu.addMenuItem(text)
    testmenu.addSubMenu(menu)

    menu = Menu(testmenu, "MenuImage-long")
    for i in range(64): text = " " * 54; menu.addMenuItem(text)
    testmenu.addSubMenu(menu)

    menu = Menu(testmenu, "MenuImage-long2")
    for i in range(32): text = " " * 300; menu.addMenuItem(text)
    testmenu.addSubMenu(menu)

    menu = Menu(testmenu, "MenuImage-large")
    for i in range(64): text = " " * 300; menu.addMenuItem(text)
    testmenu.addSubMenu(menu)

    menu = Menu(testmenu, "MenuImage-verylarge")
    for i in range(100): text = " " * 600; menu.addMenuItem(text)
    testmenu.addSubMenu(menu)

    testmenu.addSeparator()
    callbackfunc = lambda: KikkaApp.this().exitApp()
    testmenu.addMenuItem("Exit", callbackfunc)

    return testmenu


def _test_callback(index=0, title=''):
    import logging
    logging.info("MainMenu_callback: click [%d] %s" % (index, title))







