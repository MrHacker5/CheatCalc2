from . import Text, Coord, CHAR_WIDTH
import modules

SCRL_TM = 2


class List2(Text):
    def __init__(self, bounds, actList, ybar):
        super().__init__(bounds, [x for x, _ in actList], False, ybar)
        self._old_tm_scrl = 0
        self.setActList(actList)
        self._line_x = 0
        self.sel_enab = True

    def setActList(self, actList):
        self._act_list = actList
        self.changeSelection(Coord())

    def confirm(self):
        if self._act_list:
            self._act_list[self.cursor.y][1]()

    def changeSelection(self, dir):
        self._line_x = 0
        self._old_tm_scrl = modules.TIMENOW
        cur = self.cursor
        self.setText([x for x, _ in self._act_list])  # restore scrolled lines
        self.cursor = cur
        self.moveCursor(dir)
        y = self.cursor.y
        if y < len(self.text):
            self.sel_enab = True
            self.selection = [Coord(0, y), Coord(len(self.text[y]), y)]

    def loop(self):
        pass
        # y = self.cursor.y
        # if y < len(self._act_list) and (len(self._act_list[y][0]) * CHAR_WIDTH > self.bounds.w and
        #                                 modules.TIMENOW - self._old_tm_scrl > SCRL_TM):
        #     self._old_tm_scrl = modules.TIMENOW
        #     self.changeRow(self._act_list[y][0][self._line_x:], y)
        #     self._line_x += 6
        #     if (len(self._act_list[y][0]) - self._line_x + 3) * CHAR_WIDTH < self.bounds.w:
        #         self._line_x = 0
        # super().loop()
