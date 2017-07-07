import modules
from ..graphics import draw_char_dot, fill_rect, plot, updInvalRows
from . import Coord, Dir, CHAR_WIDTH, CHAR_HEIGHT

BLK_TM = 1.5
DRAW_Y_STEP = 10


class Text(object):

    def __init__(self, bounds, text, xbar, ybar):
        self.bounds = bounds
        self.text = []
        self.cursor = Coord()
        self.pos = Coord()
        self.cols = 0
        self.selection = [Coord(), Coord()]
        self.sel_enab = False
        self.cur_enab = False
        self._xbar = xbar
        self._ybar = ybar
        #self._old_tm = 0
        #self._cur_blk_state = False
        self.setText(text)
        self.inval = True

    def loop(self):
        pass
        # if self.cur_enab:
        #     self._cur_blk_state = False
        #     if modules.TIMENOW - self._old_tm > BLK_TM / 2:
        #         self._cur_blk_state = True
        #         if modules.TIMENOW - self._old_tm > BLK_TM:  # blink cursor
        #             self._old_tm = modules.TIMENOW
        #     if self._cur_blk_state != modules.CUR_ON:
        #         modules.CUR_ON = self._cur_blk_state
        #         if self._cur_blk_state:
        #             modules.CUR_POS = Coord(
        #                 self.bounds.x - self.pos.x + self.cursor.x * CHAR_WIDTH,
        #                 self.bounds.y - self.pos.y + self.cursor.y * CHAR_HEIGHT)
        #             self.inval = True

    def setText(self, lines):
        self.text = []
        self.cols = 0
        self.pos = Coord()
        self.cursor = Coord()
        self.selection = [Coord(), Coord()]
        self.sel_enab = False
        self.addLines(lines)

    def changeRow(self, line, idx=0):
        self.text[idx] = line
        if len(self.text) == 1:
            self.cols = len(line)
        self._gtext = self.text[:]

    def addLines(self, lines):
        self.text.extend(lines)
        for l in lines:
            self.cols = max(self.cols, len(l) + 1)
        self.inval = True

    def pan(self, dir, incr=True, chars=True):
        x = 0
        y = 0
        if type(dir) is Dir:
            if dir in [Dir.left, Dir.right]:
                x = 6 * (-1 if dir == Dir.left else 1)
            else:
                y = 3 * (-1 if dir == Dir.up else 1)
        else:  # type Coord
            x = dir.x
            y = dir.y
        if chars:
            x *= CHAR_WIDTH
            y *= CHAR_HEIGHT
        if incr:
            x += self.pos.x
            y += self.pos.y
        self.pos.x = max(0, min(x, self.cols * CHAR_WIDTH -
                                self.bounds.w + 3 * self._ybar))
        self.pos.y = max(0, min(y, len(self.text) * CHAR_HEIGHT -
                                self.bounds.h + 3 * self._xbar))
        # todo: drag cursor inside bounds
        self.inval = True

    def moveCursor(self, dir, incr=True):
        self._old_tm = modules.TIMENOW
        x = 0
        y = 0
        if type(dir) is Dir:
            if dir in [Dir.left, Dir.right]:
                x = -1 if dir == Dir.left else 1
            else:
                y = -1 if dir == Dir.up else 1
        else:
            x = dir.x
            y = dir.y
        if incr:
            x += self.cursor.x
            y += self.cursor.y
        x = max(0, min(x, self.cols))  # todo: wrap if overflow
        y = max(0, min(y, len(self.text) - 1))
        self.cursor = Coord(x, y)
        # drag view
        self.pos.x = max(min(self.pos.x, x * CHAR_WIDTH),
                         (x + 1) * CHAR_WIDTH - self.bounds.w + 3 * self._ybar)
        self.pos.y = max(min(self.pos.y, y * CHAR_HEIGHT),
                         (y + 1) * CHAR_HEIGHT - self.bounds.h + 3 * self._xbar)
        modules.CUR_POS = Coord(
            self.bounds.x - self.pos.x + self.cursor.x * CHAR_WIDTH,
            self.bounds.y - self.pos.y + self.cursor.y * CHAR_HEIGHT)
        self.inval = True

    def draw(self):
        if self.inval:
            self.inval = False
            gtext = list(self.text)
            for y in range(self.bounds.h - 3 * self._xbar):
                py = self.pos.y + y
                for x in range(self.bounds.w - 3 * self._ybar):
                    px = self.pos.x + x
                    ychars = py // CHAR_HEIGHT
                    xchars = px // CHAR_WIDTH
                    if 0 <= ychars < len(gtext) and 0 <= xchars < len(gtext[ychars]):
                        # hack shortcut
                        light = not(
                            self.sel_enab and self.selection[0].y == ychars)
                        draw_char_dot(gtext[ychars][xchars], self.bounds.x + x, self.bounds.y +
                                      y, px % CHAR_WIDTH, py % CHAR_HEIGHT, light)
                    else:
                        plot(self.bounds.x + x, self.bounds.y + y, False)
            self.drawOthers()
            updInvalRows(self.bounds.y, self.bounds.y + self.bounds.h)

    def drawOthers(self):
        if self._xbar or self._ybar:
            p2x = self.bounds.x + self.bounds.w
            p2y = self.bounds.y + self.bounds.h
            fill_rect(p2x - 3, p2y - 3, p2x, p2y)
            if self._xbar and self.cols > 0:
                fill_rect(self.bounds.x, p2y - 3, p2x, p2y, False)
                barw = int((self.bounds.w - 3) *
                           min(1, self.bounds.w / (self.cols * CHAR_WIDTH)))
                barx = int((self.bounds.w - 3) *
                           self.pos.x / (self.cols * CHAR_WIDTH))
                fill_rect(self.bounds.x + barx, p2y - 2,
                          self.bounds.x + barx + barw, p2y - 1)
            if self._ybar and self.text:
                fill_rect(p2x - 3, self.bounds.y, p2x, p2y, False)
                barh = int((self.bounds.h - 3) *
                           min(1, self.bounds.h / (len(self.text) * CHAR_HEIGHT)))
                bary = int((self.bounds.h - 3) *
                           self.pos.y / (len(self.text) * CHAR_HEIGHT))
                fill_rect(p2x - 2, self.bounds.y + bary,
                          p2x - 1, self.bounds.y + bary + barh)
