def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def dec2bin(d):
    b = [0, 0, 0, 0]
    for i in range(4):
        b[i] = d % 2 == 0
        d //= 2
    return b


def bin2dec(b):
    d = 0
    l = len(b)
    for i in range(l):
        d += b[i] * 2**i
    return d
