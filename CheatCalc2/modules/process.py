from time import sleep
import threading
from subprocess import Popen, PIPE, STDOUT


class Process():

    def _procThr(self):
        stm = self._proc.stdout
        while True:
            s = ''
            if stm.readable():
                s = stm.readline().decode('ascii', 'ignore')
                #s = s.rstrip()
                if s != '':
                    self._queue.extend(s.splitlines())

    def getInput(self):
        l = list(self._queue)  # make a copy!
        self._queue = []
        return l

    def __init__(self, cmd):
        self._proc = Popen(cmd, shell=False, stdout=PIPE,
                           stdin=PIPE, stderr=PIPE)
        self._queue = []
        thr = threading.Thread(target=self._procThr, daemon=True)
        thr.start()

    def sendInput(self, s):
        self._proc.stdin.write(bytes(s, 'ascii'))
        self._proc.stdin.flush()

    # no need to close proc, it will be killed when main exit
