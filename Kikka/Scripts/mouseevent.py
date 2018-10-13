import logging
from enum import Enum

from core import Core


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



def head_touch():
    logging.info("head_touch")
    Core.get_instance().setSurface(0)
    pass

def head_click():
    logging.info("head_click")
    pass

def head_doubleclick():
    logging.info("head_doubleclick")
    pass

def face_touch():
    logging.info("face_touch")
    Core.get_instance().setSurface(33)
    pass

def face_click():
    logging.info("face_click")
    pass

def face_doubleclick():
    logging.info("face_doubleclick")
    pass

def bust_touch():
    logging.info("bust_touch")
    pass

def bust_click():
    logging.info("bust_click")
    pass

def bust_doubleclick():
    logging.info("bust_doubleclick")
    pass

def hand_touch():
    logging.info("hand_touch")
    pass

def hand_click():
    logging.info("hand_click")
    pass

def hand_doubleclick():
    logging.info("hand_doubleclick")
    pass






class MouseEvent(Enum):
    MouseDown = 0
    MouseMove = 1
    MouseUp = 2
    MouseDoubleClick = 3
    WheelEvent = 4

    def event_selector(event, boxtag):
        e = getEventList()

        if boxtag in e \
        and event in e[boxtag]:
            e[boxtag][event]()



