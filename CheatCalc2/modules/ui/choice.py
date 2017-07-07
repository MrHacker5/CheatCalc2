from . import Window, List2, Text, Rect, TType, Dir, LCD_WIDTH, LCD_HEIGHT, CHAR_HEIGHT


class Choice(Window):
    def __init__(self, title, actList):
        super().__init__(None)
        self.name = 'choice'
        self._list = List2(
            Rect(0, 2 * CHAR_HEIGHT, LCD_WIDTH, LCD_HEIGHT - 2 * CHAR_HEIGHT), actList, False)
        self.addCtrl(
            Text(Rect(0, 0, LCD_WIDTH, 2 * CHAR_HEIGHT), title, False, False))
        self.addCtrl(self._list)

    def procCmd(self, t):
        ttype = t[0]
        if ttype in [TType.up, TType.down]:
            self._list.changeSelection(Dir.up if ttype == TType.up else Dir.down)
        elif ttype == TType.enter:
            self._list.confirm()
