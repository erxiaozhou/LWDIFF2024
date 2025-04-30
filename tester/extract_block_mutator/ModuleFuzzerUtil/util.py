from random import choice, randint
from random import choices
import string


def generate_random_utf8_str(n):
    result = ''
    while len(result) < n:
        r = randint(0, 0x10ffff)
        if r < 0x80:
            result += chr(r)
        elif r < 0x800:
            result += chr(((r >> 6) & 0x1f) | 0xc0)
            result += chr((r & 0x3f) | 0x80)
        elif r < 0x10000:
            result += chr(((r >> 12) & 0xf) | 0xe0)
            result += chr(((r >> 6) & 0x3f) | 0x80)
            result += chr((r & 0x3f) | 0x80)
        else:
            result += chr(((r >> 18) & 0x7) | 0xf0)
            result += chr(((r >> 12) & 0x3f) | 0x80)
            result += chr(((r >> 6) & 0x3f) | 0x80)
            result += chr((r & 0x3f) | 0x80)
    return result[:n]


def gen_random_bytes(length):
    return bytearray(choices(range(256), k=length))