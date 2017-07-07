from enum import IntEnum
from collections import namedtuple
from . import isInt, TType, relat_path, CHAR_WIDTH, CHAR_HEIGHT, LCD_WIDTH
import png


class KMode(IntEnum):
    norm = 0
    sf = 1
    alpha = 2


def parse_key_layout():
    lines = open(relat_path('../key-layout.txt')).read().splitlines()
    tkns = [l.split() for l in lines]
    in_pins = [int(tkns[0][i]) for i in range(1, 5)]
    out_pins = [int(tkns[1][i]) for i in range(1, 5)]

    keys = []
    for i in range(len(lines)):
        if len(tkns[i]) == 0 or not isInt(tkns[i][0]):
            continue
        in_pin = int(tkns[i].pop(0))
        out_pin = int(tkns[i].pop(0))
        keys.append(([], [], [], in_pin, out_pin))

        kmode = KMode.norm
        for tkn in tkns[i]:
            if tkn == '%':
                kmode = KMode.sf
            elif tkn == '@':
                kmode = KMode.alpha
            else:
                ttype = TType.text
                if tkn.startswith('%'):
                    tkn = tkn[1:]
                    if '@' != tkn != '%':
                        ttype = TType[tkn]
                elif '@' in tkn:
                    ttype = TType.func
                keys[-1][kmode].append((ttype, tkn))
    keys.sort(key=lambda x: x[4]) #sort by out code
    return in_pins, out_pins, keys
#keys: [([(ttype, ttext)], [(ttype, ttext)], [(ttype, ttext)], inp, out)]


def parse_notes():
    lines = open(relat_path('../notes.txt'),
                 encoding='utf-8').read().splitlines()
    notes = []
    comment = False
    for l in lines:
        tkns = l.split()
        if len(tkns) > 0:
            if tkns[0].startswith('%title'):
                notes.append([l[len(tkns[0]):].strip(), [], []])
            elif tkns[0].startswith('%tags'):
                notes[-1][1] = tkns[1:]
            elif tkns[0].startswith('%%%'):
                comment = not comment
            elif not comment and not tkns[0].startswith('%%'):
                notes[-1][2] += [l[i:i + LCD_WIDTH // CHAR_WIDTH - 1]
                                 for i in range(0, len(l), LCD_WIDTH // CHAR_WIDTH - 1)]
    return notes
# [(title, [tags], [body])]


def parse_macros():
    lines = open(relat_path('../macros.txt')).read().splitlines()
    macros = []
    for l in lines:
        tkns = l.split()
        if len(tkns) > 0:
            first = tkns[0]
            if first.startswith('%'):
                continue
            idx = first.find('(') + 1
            name = first[:idx - 1]
            params = []
            while True:
                newidx = first.find(',', idx)
                if newidx == -1:
                    params.append((first[idx:len(first) - 1], []))
                    break
                params.append((first[idx:newidx], []))
                idx = newidx + 1
            params = [x for x in params if x[0] != '']
            idx = 0
            string = l[l.find(tkns[1]):]
            while idx < len(string):
                paridx = [x for x in range(len(params))
                          if string[idx:].startswith(params[x][0])
                          and (idx == 0 or not string[idx - 1].isalnum())
                          and (idx + len(params[x][0]) >= len(string)
                               or not string[idx + len(params[x][0])].isalnum())]
                if len(paridx) == 0:
                    idx += 1
                    continue
                paridx = paridx[0]
                params[paridx][1].append(idx)
                parlen = len(params[paridx][0])
                string = string[:idx] + string[idx + parlen:]
            macros.append((name, params, string))
    # generate matrix macros
    for y in range(1, 7):
        for x in range(1, 7):
            name = '@' + str(y) + str(x)
            params = []
            string = ''
            for y1 in range(y):
                string += ',' if y1 > 0 else '{'
                for x1 in range(x):
                    string += ',' if x1 > 0 else '{'
                    params.append(('', [len(string)]))
                string += '}'
            string += '}'
            macros.append((name, params, string))
    return macros
# macros: [(name, [(param name, pos)], string)]


def parse_fontsheet():
    img = png.Reader(relat_path('../fontsheet.png')).read()
    rows = list(img[2])
    height = len(rows)
    width = len(rows[0])
    sheet = []
    for y in range(height // CHAR_HEIGHT):
        for x in range(width // CHAR_WIDTH):
            char = []
            for sy in range(CHAR_HEIGHT):
                char.append(rows[y * CHAR_HEIGHT + sy]
                            [x * CHAR_WIDTH:(x + 1) * CHAR_WIDTH])
            sheet.append(char)
    return sheet
