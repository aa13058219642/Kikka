# coding=utf-8
import logging
from enum import Enum

import kikka


class MouseEvent(Enum):
    MouseDown = 0
    MouseMove = 1
    MouseUp = 2
    MouseDoubleClick = 3
    WheelEvent = 4

    @staticmethod
    def event_selector(gid, nid, event, eventtag):
        if gid == kikka.KIKKA: import ghost_kikka as ghost_event
        elif gid == kikka.SSP: import ghost_ssp as ghost_event
        else: import ghost_kikka as ghost_event

        e = ghost_event.getEventList()
        if eventtag in e and event in e[eventtag]:
            e[eventtag][event](gid, nid)
