h = 0
for b in range(106500, 123500 + 1, 17):
    for d in range(2, b + 1):
        if d % b == 0 and (2 <= d // b <= b):
            h += 1
            break
    if b % (17 * 17 * 17) == 0:
        print(b, h)
