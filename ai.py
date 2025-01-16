
from gmpy2 import is_prime
from itertools import permutations




def comb(nbs, k):
    'Get all the possible combinations of the numbers'
    return [list(p) for p in permutations(nbs, k)]

def get_largest_prime(nbs):
    'Get the largest prime number from the numbers'
    nbs = [str(nb) for nb in nbs]
    ans = 0
    for i in range(len(nbs)):
        ls = comb(nbs, i+1)
        for l in ls:
            num = int(''.join(l))
            if is_prime(num) and num > ans:
                ans = num
    return ans

print(get_largest_prime([10,7,8,12,4]))
