import random
import math
import sys


# computes base^exp mod modulus
def modexp(base, exp, modulus):
    return pow(base, exp, modulus)

def generate_keys():
    rand1 = random.randint(100, 300)
    rand2 = random.randint(100, 300)
    # store the txt file of prime numbers in a python list
    fo = open('lib/primes-to-100k.txt', 'r')
    lines = fo.read().splitlines()
    fo.close()

# store our prime numbers in these variables
    p = int(lines[rand1])
    g = int(lines[rand2])
    g = modexp(g, 2, p)
    x = random.randint(1, (p - 1) // 2)
    h = modexp(g, x, p)

    pk = [p, g, h]
    sk = [p, g, x]

    return pk, sk
# encrypts a string sPlaintext using the public key k

def encrypt( pk, pt):

    p = pk[0]
    g = pk[1]
    h = pk[2]
    # pick random y from (0, p-1) inclusive
    y = random.randint(0, p)
    # c = g^y mod p
    c = modexp(g, y, p)
    # d = ih^y mod p
    d = (pt * modexp(h, y, p)) % p
    # add the pair to the cipher pairs list
    return c, d

# performs decryption on the cipher pairs found in Cipher using
# prive key K2 and writes the decrypted values to file Plaintext
def decrypt( sk, ct):
    c = ct[0]
    d = ct[1]

    p = sk[0]
    g = sk[1]
    x = sk[2]

    # s = c^x mod p
    s = modexp(c, x, p)
    # plaintext integer = ds^-1 mod p
    pt = (d * modexp(s, p-2, p)) % p
    return pt
