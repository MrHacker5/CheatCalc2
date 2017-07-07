import spidev
import threading
from . import parser, CHAR_WIDTH, CHAR_HEIGHT, LCD_WIDTH, LCD_HEIGHT


class _g:
    spi = spidev.SpiDev()
    fontsheet = []
    lcdBuf = []
    invalRows = [False] * LCD_HEIGHT
    # oldInvalRows = [[True] * LCD_HEIGHT]


def updInvalRows(frm, to):
    for i in range(frm, to):
        _g.invalRows[i] = True


def _spi_msg(rs, cmds):
    b1 = 0b11111000 | ((rs & 0x01) << 1)
    bytes = []
    for cmd in cmds:
        bytes.append(cmd & 0xF0)
        bytes.append((cmd & 0x0F) << 4)
    return _g.spi.xfer2([b1] + bytes)


def clear():
    # [[0] * (LCD_WIDTH // 8) for i in range(LCD_HEIGHT)]
    _g.lcdBuf = [[False] * LCD_WIDTH for i in range(LCD_HEIGHT)]


def fill_rect(x1, y1, x2, y2, set=True):
    for y in range(y1, y2):
        for x in range(x1, x2):
            plot(x, y, set)


def plot(x, y, set):
    if x >= 0 and x < LCD_WIDTH and y >= 0 and y < LCD_HEIGHT:
        _g.lcdBuf[y][x] = set


def draw_text(string, x, y):
    for c in string:
        for cy in range(CHAR_HEIGHT):
            for cx in range(CHAR_WIDTH):
                draw_char_dot(c, x + cx, y + cy, cx, cy)
        x += CHAR_WIDTH


def draw_char_dot(char, px, py, cx, cy, light=True):
    idx = ord(char)
    if idx < 256:
        plot(px, py, _g.fontsheet[idx][cy][cx] ^ (not light))


def redraw():
    for y in range(LCD_HEIGHT):
        yy = 63 - y
        if _g.invalRows[yy]:
            #_g.oldInvalRows[yy] = list(_g.invalRows)
            _spi_msg(0, [0x80 + y % 32, 0x80 + (8 if y >= 32 else 0)])
            #_spi_msg(1, _g.lcdBuf[y])
            _spi_msg(1, [sum(v << i for i, v in enumerate(
                _g.lcdBuf[yy][j - 8:j])) for j in range(LCD_WIDTH, -1, -8)])
    _g.invalRows = [False] * LCD_HEIGHT


def close():
    _g.spi.close()


_g.spi.open(0, 0)
_g.spi.cshigh = True  # use inverted CS
_g.spi.max_speed_hz = 1000000  # set SPI clock to 1.8MHz, up from 125kHz


_spi_msg(0, [0x30])  # basic instruction set
_spi_msg(0, [0x30])  # repeated
_spi_msg(0, [0x0C])  # display on

_spi_msg(0, [0x34])  # enable RE mode
_spi_msg(0, [0x34])
_spi_msg(0, [0x36])  # enable graphics display

_g.fontsheet = parser.parse_fontsheet()


# splash screen
clear()
draw_text('  CheatCalc 2.0', 0, 20)
draw_text('        loading...', 0, 30)
updInvalRows(0, LCD_HEIGHT)
redraw()
