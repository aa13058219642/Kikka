# coding=utf-8

from enum import Enum

class GhostEvent(Enum):
    EventNone       = 0
    MouseDown       = 1
    MouseMove       = 2
    MouseTouch      = 3
    MouseUp         = 4
    MouseDoubleClick = 5
    WheelEvent      = 6

    CustomEvent = 100





