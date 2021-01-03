import itertools

a, b, c, e, f = 0, 0, 0, 0, 0
while True:
    c = b | 65536
    b = 10605201
    while True:
        f = c & 255
        b = (((b + (c & 255)) & 16777215) * 65899) & 16777215
        if c < 256:
            break
        for f in itertools.count():
            if c < (f + 1) * 256:
                break
        c = f
    if b == a:
        break
