from time import time

def squareRootCeiling(n):
    i = 0
    while True:
        if i**2 >= n:
            return i

        i += 1

def sieve(n):
    if n < 2:
        return []

    table = list(False for _ in range(n))
    table[0] = True
    table[1] = True

    i = 2
    end = squareRootCeiling(n)
    while i < end:
        square = i**2
        j = 0
        while square + i * j < n:
            table[square + i * j] = True
            j += 1

        i += 1

    result = []
    i = 0
    while i < len(table):
        if not table[i]:
            result.append(i)

        i += 1

    return result

start = time()
print(sieve(1000000))
print("Time: {}".format(time()-start))