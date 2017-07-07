import math
from difflib import SequenceMatcher  # included in std libraries, incredible!
from itertools import product
from . import Window, List2, Text, InputField2, Rect, Dir, TType, LCD_WIDTH, LCD_HEIGHT
from .. import parser

TITLES, TAGS, NOTES = zip(*parser.parse_notes())
TITLE_TKNS = [x.split() for x in TITLES]

NTLS = len(TITLES)


class _Note_view(Window):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.body = Text(Rect(0, 0, LCD_WIDTH, LCD_HEIGHT), text, False, True)
        self.addCtrl(self.body)

    def procCmd(self, t):
        ttype = t[0]
        if ttype == TType.up:
            self.body.pan(Dir.up)
        elif ttype == TType.down:
            self.body.pan(Dir.down)
        elif ttype in [TType.esc, TType.bs]:
            self.close()


class Notes2(Window):

    def _setRanks(self, tkns, seq, coeff):
        ranks = [0] * NTLS
        for i in range(NTLS):
            cp = list(product(tkns, seq[i]))  # cartesian product
            for s1, s2 in cp:
                # try real_quick_ratio
                ranks[i] += coeff * 3 * SequenceMatcher(None, s1, s2).ratio()
                l = min(len(s1), len(s2))
                ranks[
                    i] += coeff * math.log10((len([1 for x in range(l) if s1[x] == s2[x]]) + 1) / l)
        return ranks

    def _search(self, s):
        actList = list(self._entries)  # copy
        if s != '':  # else return all entries in natural order
            tkns = s.split()
            ranks = self._setRanks(tkns, TITLE_TKNS, 4)
            ranks2 = self._setRanks(tkns, TAGS, 3)
            ranks = [ranks[i] + ranks2[i] for i in range(NTLS)]
            # reorder actList by decreasing rank
            idxList = list(zip(*(sorted(zip(ranks, range(NTLS)))[::-1])))[1]
            actList = [actList[x] for x in idxList]
        self._list.setActList(actList)

    def _set_note_view(self, i):
        self.setSubWin(_Note_view(self, NOTES[i]))

    def __init__(self):
        super().__init__(None)
        self.name = 'notes'
        self._entries = [(TITLES[i], lambda i=i: self._set_note_view(i)) for i in range(NTLS)]
        self._list = List2(Rect(0, 0, LCD_WIDTH, LCD_HEIGHT), [], False)
        self.addCtrl(self._list)
        self.setSubWin(InputField2(self, self._search))

    def procCmd(self, t):
        ttype = t[0]
        if ttype in [TType.text, TType.func]:
            self.setSubWin(InputField2(self, self._search))
            self.sub_win.procToken(t)
        elif ttype == TType.up:
            self._list.changeSelection(Dir.up)
        elif ttype == TType.down:
            self._list.changeSelection(Dir.down)
        elif ttype == TType.enter:
            self._list.confirm()
