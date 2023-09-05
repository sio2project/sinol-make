from lsalib import *


def main():
    a, b = 0, 100

    while a <= b:
        mid = (a + b) // 2
        g = guess(mid)
        if g == 0:
            quit()
        elif g == 1:
            b = mid + 1
        else:
            a = mid - 1
    guess(a)
    quit()


main()
