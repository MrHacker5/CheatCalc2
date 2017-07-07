
from enum import IntEnum
from os import path
from .helpers import *
from .process import Process


class TType(IntEnum):
    text = 0
    func = 1
    sf = 2
    alpha = 3
    opts = 4
    up = 5
    right = 6
    down = 7
    left = 8
    bottom = 9
    reset = 10 #on button
    shutdown = 11
    mode = 12
    clear = 13
    esc = 14
    tab = 15
    caps = 16
    shift = 17
    ctrl = 18
    meta = 19
    alt = 20
    space = 21
    enter = 22
    bs = 23
    delete = 24
    copy = 25
    paste = 26
    undo = 27
    redo = 28
    ans = 29
    drg = 30


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Coord:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Dir(IntEnum):
    left = 0
    up = 1
    right = 2
    down = 3


def relat_path(s):
    return path.join(path.dirname(__file__), s)




ALIVE = True
TIMENOW = 0
ROOT = None
SHIFTCAPS = 0
SFUNC = False
ALPHA = True

WINDOWS = []


CHAR_WIDTH = 6
CHAR_HEIGHT = 8
LCD_WIDTH = 128
LCD_HEIGHT = 64

CUR_POS = Coord()
CUR_ON = False

from .graphics import LCD_WIDTH, LCD_HEIGHT, CHAR_WIDTH, CHAR_HEIGHT
