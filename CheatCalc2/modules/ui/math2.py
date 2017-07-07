from . import Window, Text, InputField2, TType, Rect, Coord, Dir, LCD_WIDTH, LCD_HEIGHT
from .. import Process


class Math2(Window):
    def _inCb(self, s):
        self._proc.sendInput(s + '\n')
        self._text.addLines([s])

    def __init__(self):
        super().__init__(None)
        self.name = 'math'
        self._text = Text(Rect(0, 0, LCD_WIDTH, LCD_HEIGHT), [], True, False)
        self._proc = Process('wolfram')
        self.addCtrl(self._text)
        self.setSubWin(InputField2(self, self._inCb))

    def subLoop(self):
        s = self._proc.getInput()
        if len(s) > 0:
            s = [l for l in s if not l.startswith('In[')]
            self._text.addLines(s)
            self._text.pan(Coord(0, len(self._text.text)), incr=False)

    def procCmd(self, t):
        ttype = t[0]
        if ttype in [TType.text, TType.func]:
            self.setSubWin(InputField2(self, self._inCb))
            self.sub_win.procToken(t)
        elif ttype == TType.up:
            self._text.pan(Dir.up)
        elif ttype == TType.down:
            self._text.pan(Dir.down)
        elif ttype == TType.left:
            self._text.pan(Dir.left)
        elif ttype == TType.right:
            self._text.pan(Dir.right)
