n = 0
m = 0
cnt = 0
finished = False


def init():
    global n, m
    n, m = map(int, input().split())


def guess(a):
    global finished, cnt
    cnt += 1

    if a == n:
        if cnt > m:
            print("Too_many_queries")
            print("WRONG")
            finished = True
            return 0
        else:
            print("Correct")
            print("OK")
            finished = True
            return 0
    if a < n:
        return -1
    if a > n:
        return 1


def quit():
    if not finished:
        print("Not_correct")
        print("WRONG")
    exit(0)
