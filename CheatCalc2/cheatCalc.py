from time import perf_counter, sleep
import threading
import RPi.GPIO as io
import modules as m
import modules.graphics as g
from modules import parser, TType, Rect, LCD_WIDTH, LCD_HEIGHT, CHAR_WIDTH, CHAR_HEIGHT
from modules.ui import InputField2, Window, List2, Math2, Notes2, Text, Choice


K_REP_THRESH = 0.7
PRSD_THRESH = 0.15


class _cc:
    inPins, outPins, keys = parser.parse_key_layout()
    nKeys = len(keys)
    oldKey = -1
    lastTime = 0
    lastPrsdTime = 0
    oldValidKey = -1
    actCnt = 0
    token = ('', TType.text)
    waiting = False
    thr = None
    gthread_alive = True


def clean_wins():
    idx = len(m.WINDOWS)
    while idx > 0:
        idx -= 1
        if m.WINDOWS[idx].name in ['math', 'notes']:
            m.WINDOWS[idx].setActive(False)
        else:
            w = m.WINDOWS.pop(idx)
            w.close()


def activate_win(name):
    clean_wins()
    for w in m.WINDOWS:
        if w.name == name:
            w.setActive(True)


def restart():
    m.ALIVE = False


def shutdown():
    # close process
    f = open('shutdown.txt', mode='w')
    f.close()
    m.ALIVE = False


def proc_token():
    """under certain circumstances, this is called twice per cicle, most of the time not at all"""
    ttype = _cc.token[0]
    if ttype == TType.sf:
        m.SFUNC = not m.SFUNC
    elif ttype == TType.alpha:
        m.ALPHA = not m.ALPHA
    elif ttype in [TType.shift, TType.caps]:
        m.SHIFTCAPS = 0 if m.SHIFTCAPS != 0 else (
            1 if ttype == TType.shift else 2)
    elif ttype == TType.mode:
        which = False
        for w in m.WINDOWS:
            if w.name == 'math' and w._active:
                which = True
        clean_wins()
        for w in m.WINDOWS:
            if w.name == ('notes' if which else 'math'):
                w.setActive(True)
    elif ttype == TType.reset:
        #clean_wins()
        #fakeinp = InputField2(None, lambda x: activate_win('math'))
        #for c in fakeinp.ctrls:
        #    if type(c) != Text:
        #        fakeinp.removeCtrl(c)
        #fakeinp.addCtrl(
        #    Text(Rect(0, 0, LCD_WIDTH, LCD_HEIGHT - CHAR_HEIGHT), [''], False, False))
        #m.WINDOWS.append(fakeinp)
    elif ttype == TType.shutdown:
        clean_wins()
        m.WINDOWS.append(
            Choice(['Shutdown?'], [('No', lambda: activate_win('math')),
                                   ('Shutdown', shutdown), ('Restart', restart)]))
    elif ttype == TType.meta:
        startDrawThread()
    else:
        for w in m.WINDOWS:
            w.procToken(_cc.token)
    if ttype != TType.sf:
        m.SFUNC = False
    if ttype != TType.shift and m.SHIFTCAPS == 1:
        m.SHIFTCAPS = 0

    print(ttype, _cc.token[1])


# one input line is defective: i must reject repeated key faster than 0.1s
def proc_keys_state():
    """this function detect key press based on duration and discard glitches
    then chooses the right token based on timing and key repetition"""
    currkey = -1
    # get physical key
    old_out_pin = -1
    for k in range(_cc.nKeys):
        _, _, _, in_pin, out_pin = _cc.keys[k]
        if out_pin != old_out_pin:
            old_out_pin = out_pin
            b = m.dec2bin(out_pin)
            for i in range(4):
                io.output(_cc.outPins[i], not b[i])
        if not io.input(_cc.inPins[in_pin]):
            currkey = k
    if currkey != -1:
        if m.TIMENOW - _cc.lastPrsdTime > PRSD_THRESH:
            _cc.lastPrsdTime = m.TIMENOW
            if currkey != _cc.oldKey:
                if _cc.waiting:
                    if _cc.oldValidKey == currkey:
                        _cc.actCnt += 1
                    else:
                        proc_token()
                        _cc.actCnt = 0
                        _cc.waiting = False
                kmode = 1 if m.SFUNC and len(_cc.keys[currkey][1]) > 0 else 2 if m.ALPHA and len(
                    _cc.keys[currkey][2]) > 0 else 0
                l = len(_cc.keys[currkey][kmode])
                if l > 0:
                    _cc.token = _cc.keys[currkey][kmode][_cc.actCnt % l]
                    if l == 1:
                        proc_token()
                    else:
                        _cc.waiting = True
                _cc.oldValidKey = currkey
                _cc.lastTime = m.TIMENOW
    elif _cc.waiting and m.TIMENOW - _cc.lastTime > K_REP_THRESH:
        proc_token()
        _cc.actCnt = 0
        _cc.waiting = False
    _cc.oldKey = currkey


def graphics_thread():
    while m.ALIVE and _cc.gthread_alive:
        for w in m.WINDOWS:
            w.draw()
        x1 = LCD_WIDTH - 4
        if m.SFUNC or m.ALPHA:
            char = '\xfc' if m.SFUNC else '\xfd'
            for x in range(4):
                for y in range(8):
                    g.draw_char_dot(char, x1 + x, y, x, y)
        else:
            g.fill_rect(x1, 0, LCD_WIDTH, 8, False)
        if m.SHIFTCAPS > 0:
            char = '\xfe' if m.SFUNC else '\xff'
            for x in range(4):
                for y in range(7):
                    g.draw_char_dot(char, x1 + x, y + 7, x, y)
        else:
            g.fill_rect(x1, 7, LCD_WIDTH, 14, False)
        g.updInvalRows(0, 14)

        g.fill_rect(m.CUR_POS.x - 1, m.CUR_POS.y,
                    m.CUR_POS.x + 1, m.CUR_POS.y + CHAR_HEIGHT)
        g.redraw()


## INIT ##
g.clear()

# GPIO setup
io.setwarnings(False)
io.setmode(io.BOARD)
for i in range(4):
    io.setup(_cc.inPins[i], io.IN, pull_up_down=io.PUD_UP)

for i in range(4):
    io.setup(_cc.outPins[i], io.OUT)

m.WINDOWS = [Notes2(), Math2()]


def startDrawThread():
    clean_wins()
    if _cc.thr != None:
        _cc.gthread_alive = False
        _cc.thr.join(5.0)
    _cc.gthread_alive = True
    _cc.thr = threading.Thread(target=graphics_thread)
    _cc.thr.start()
    activate_win('math')


startDrawThread()

##### MAIN LOOP #####
while m.ALIVE:
    m.TIMENOW = perf_counter()

    proc_keys_state()

    for w in m.WINDOWS:
        w.loop()

## RELEASE ##
for w in m.WINDOWS:
    w.close()
_cc.thr.join(10.0)

g.clear()
g.draw_text('  Shutting down...', 0, 28)
g.updInvalRows(0,LCD_HEIGHT)
g.redraw()

g.close()
io.cleanup()
