# coding=utf-8
import logging

import kikka
from mouseevent import MouseEvent
from kikka_shell import Surface


def getEventList():
    e = {}

    name = 'Head'
    e[name] = {}
    e[name][MouseEvent.MouseDown] = head_click
    e[name][MouseEvent.MouseMove] = head_touch
    e[name][MouseEvent.MouseDoubleClick] = head_doubleclick

    name = 'Face'
    e[name] = {}
    e[name][MouseEvent.MouseDown] = face_click
    e[name][MouseEvent.MouseMove] = face_touch
    e[name][MouseEvent.MouseDoubleClick] = face_doubleclick

    name = 'Bust'
    e[name] = {}
    e[name][MouseEvent.MouseDown] = bust_click
    e[name][MouseEvent.MouseMove] = bust_touch
    e[name][MouseEvent.MouseDoubleClick] = bust_doubleclick

    name = 'Hand'
    e[name] = {}
    e[name][MouseEvent.MouseDown] = hand_click
    e[name][MouseEvent.MouseMove] = hand_touch
    e[name][MouseEvent.MouseDoubleClick] = hand_doubleclick

    return e


def head_touch(gid, nid):
    logging.info("head_touch")
    kikka.core.getGhost(kikka.KIKKA).setSurface(kikka.SAKURA, Surface.ENUM_NORMAL)
    pass


def head_click(gid, nid):
    logging.info("head_click")
    pass


def head_doubleclick(gid, nid):
    logging.info("head_doubleclick")
    pass


def face_touch(gid, nid):
    logging.info("face_touch")
    kikka.core.getGhost(kikka.KIKKA).setSurface(kikka.SAKURA, Surface.ENUM_ANGER2)
    pass


def face_click(gid, nid):
    logging.info("face_click")
    pass


def face_doubleclick(gid, nid):
    logging.info("face_doubleclick")
    pass


def bust_touch(gid, nid):
    logging.info("bust_touch")
    pass


def bust_click(gid, nid):
    logging.info("bust_click")
    pass


def bust_doubleclick(gid, nid):
    logging.info("bust_doubleclick")
    pass


def hand_touch(gid, nid):
    logging.info("hand_touch")
    pass


def hand_click(gid, nid):
    logging.info("hand_click")
    pass


def hand_doubleclick(gid, nid):
    logging.info("hand_doubleclick")
    pass





