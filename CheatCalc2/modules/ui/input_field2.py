from . import Window, Text, List2, TType, Rect, Coord, Dir, LCD_WIDTH, LCD_HEIGHT, CHAR_HEIGHT
from .. import SHIFTCAPS, parser
import modules


class InputField2(Window):
    HIST = []

    def __init__(self, parent, inputCb):
        super().__init__(parent)
        self.name = 'inpfield'
        self.sugs = List2(
            Rect(0, 0, LCD_WIDTH, LCD_HEIGHT - CHAR_HEIGHT), [], True)
        self.field = Text(Rect(0, LCD_HEIGHT - CHAR_HEIGHT,
                               LCD_WIDTH, CHAR_HEIGHT), [''], False, False)
        self.field.cur_enab = True
        self.addCtrl(self.sugs)
        self.addCtrl(self.field)
        self.cb = inputCb
        self.sugs_enab = False

    def _updateField(self, sug, idx, other):
        x = self.field.cursor.x
        text = self.field.text[0]
        self.field.changeRow(text[:x] + sug[idx:] + text[x:])
        self.field.moveCursor(Coord(len(sug) - idx, 0))
        if other != None:
            text = self.field.text[0]
            x = self.field.cursor.x
            parens = '('
            parens += ',' * max(0, len(other[0]) - 1)
            parens += ')'
            self.field.changeRow(text[:x] + parens + text[x:])
            self.field.moveCursor(Dir.right)

    def _setSugs(self):
        entries = []  # (sug start idx/ rank, sug text)
        inp = self.field.text[0][:self.field.cursor.x]
        if inp == '':
            entries = list(reversed([(0, x, None) for x in IF.HIST]))
        else:
            # this generates duplicates!!
            # for x in range(max(len(inp) - 7, len(inp) - 1), len(inp)):
            subinp = inp[-1]
            entries.extend([(1, y, [z, w])
                            for y, z, w in macros_noparens if y.startswith(subinp)])
            entries.extend([(len(inp), x, None)
                            for x in IF.HIST if x.startswith(inp)])
            #entries.sort(key=lambda y: y[0], reverse=True)
        self.sugs.setActList([(y, lambda sug=y, idx=i, other=zw: self._updateField(
            sug, idx, other)) for i, y, zw in entries])

    def procCmd(self, t):
        ttype, ttext = t
        c = self.field.cursor.x
        text = self.field.text[0]
        if ttype in [TType.text, TType.func, TType.space]:
            idx = 0
            if ttype == TType.space:
                ttext = ' '
            elif ttype == TType.func:
                idx = ttext.index('@')
                ttext = ttext.replace('@', '')
            if len(ttext) == 1:
                ttext = ttext.upper() if SHIFTCAPS > 0 else ttext.lower()
            text = text[:c] + ttext + text[c:]
            self.field.changeRow(text)
            self.field.moveCursor(Coord(len(ttext) if idx == 0 else idx, 0))
            self.sugs_enab = False
        elif ttype == TType.bs:
            if c > 0:
                self.field.changeRow(text[:c - 1] + text[c:])
                self.field.moveCursor(Dir.left)
                self.sugs_enab
        elif ttype == TType.enter and text != '':
            IF.HIST.append(text)
            IF.HIST = IF.HIST[-10:]  # keep last 10
            self.cb(expand_macros(text))
            self.close()
        elif ttype == TType.tab:
            if not self.sugs_enab:
                self._setSugs()
            else:
                self.sugs.confirm()
            self.sugs_enab = not self.sugs_enab
        elif ttype in [TType.left, TType.right]:
            self.field.moveCursor(Dir.left if ttype ==
                                  TType.left else Dir.right)
            self.sugs_enab = False
        elif ttype in [TType.up, TType.down]:
            self.sugs.changeSelection(
                Dir.up if ttype == TType.up else Dir.down)
        elif ttype == TType.esc:
            self.close()


IF = InputField2

macros = parser.parse_macros()
macros_noparens = [m for m in macros if not m[0].startswith('@')]


def expand_macros(inp):
    idx = len(inp) - 3
    while idx >= 0:
        macroidx = [x for x in range(len(macros))
                    if inp[idx:].startswith(macros[x][0])
                    and (idx == 0 or not (inp[idx - 1].isalnum() or inp[idx - 1] == '_'))
                    and (idx + len(macros[x][0]) >= len(inp)
                         or inp[idx + len(macros[x][0])] == '(')]
        if not macroidx:  # empty -> false
            idx -= 1
            continue
        macroidx = macroidx[0]
        params = []
        paramidx = idx + len(macros[macroidx][0]) + 1
        laststartidx = paramidx
        layer = 1
        while layer > 0 and paramidx < len(inp):
            char = inp[paramidx]
            if char in '([{':
                layer += 1
            else:
                if layer == 1 and char in ',)':
                    if paramidx != laststartidx:
                        params.append(inp[laststartidx:paramidx])
                    laststartidx = paramidx + 1
                if char in ')]}':
                    layer -= 1
            paramidx += 1
        if layer != 0 or len(params) != len(macros[macroidx][1]):
            idx -= 2
            continue  # the input is invalid, leave the macro not replaced
        inp = inp[:idx] + macros[macroidx][2] + \
            (inp[paramidx:] if paramidx < len(inp) else '')
        paramidx = idx + len(macros[macroidx][2])
        while paramidx >= 0:
            idxarr = [x for x in range(len(macros[macroidx][1]))
                      if paramidx - idx in macros[macroidx][1][x][1]]
            if len(idxarr) != 0:
                inp = inp[:paramidx] + params[idxarr[0]] + inp[paramidx:]
            paramidx -= 1
        idx = len(inp) - 3  # restart for recursive macros
    return inp
