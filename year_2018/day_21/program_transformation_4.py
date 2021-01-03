a, b, c, e, f = 0, 0, 0, 0, 0
while True:
    c = b | 65536
    b = 10605201
    while True:
        f = c & 255
        b += f
        b &= 16777215
        b *= 65899
        b &= 16777215
        if 256 > c:
            break
        f = 0
        while True:
            e = f + 1
            e *= 256
            if e > c:
                break
            f += 1
        c = f
    if b == a:
        break
