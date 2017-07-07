from time import sleep
import threading
import modules


class Window(object):
    def __init__(self, parent):
        self.name = ''
        self.parent = parent
        self.ctrls = []
        self.sub_win = None

        self._active = False
        self.setActive(True)

    def invalidate(self):
        if self.sub_win != None:
            self.sub_win.invalidate()
        else:
            for c in self.ctrls:
                c.inval = True

    def setActive(self, active):
        self._active = active
        self.invalidate()

    def procToken(self, t):
        if self._active:
            if self.sub_win != None:
                self.sub_win.procToken(t)
            else:
                self.procCmd(t)

    def procCmd(self, t):
        pass

    def loop(self):
        if self._active:
            if self.sub_win != None:
                self.sub_win.loop()
            else:
                self.subLoop()
                for c in self.ctrls:
                    c.loop()

    def subLoop(self):
        pass

    def addCtrl(self, ctrl):
        self.ctrls.append(ctrl)

    def removeCtrl(self, ctrl):
        self.ctrls.remove(ctrl)

    def setSubWin(self, subWin):
        self.sub_win = subWin

    def draw(self):
        if self._active:
            if self.sub_win != None:
                self.sub_win.draw()
            else:
                for c in self.ctrls:
                    c.draw()

    def close(self):
        self.setActive(False)
        self.setSubWin(None)
        for c in self.ctrls:
            self.removeCtrl(c)
        if self.parent != None:
            self.parent.setSubWin(None)
            self.parent.invalidate()
