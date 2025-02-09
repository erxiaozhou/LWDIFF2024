
from random import randint, random, uniform
from numpy import inf, nan


# generate imm_repr
def generate_randon_common_i32():
    r = random()
    if random() > 0.0001:
        return randint(0, 1024)
    else:
        return randint(-2147483648, 2147483647)


def generate_randon_i64():
    if random() > 0.0001:
        return randint(0, 1024)
    else:
        # return randint(-2147483648, 2147483647)
        return randint(-9223372036854775808, 9223372036854775807)


def generate_randon_f32():
    r = random()
    if r < 0.001:
        return nan
    elif r < 0.002:
        return -nan
    elif r < 0.003:
        return inf
    elif r < 0.004:
        return -inf
    if r < 0.005:
        return uniform(-3.40282347e+38, 3.40282347e+38)
    if r < 0.007:
        return -0
    if r < 0.01:
        return 0
    return uniform(-10, 10)


def generate_randon_f64():
    r = random()
    if r < 0.001:
        return nan
    elif r < 0.002:
        return -nan
    elif r < 0.003:
        return inf
    elif r < 0.004:
        return -inf
    if r < 0.005:
        return uniform(-1.7976931348623157e+308, 1.7976931348623157e+308)
    if r < 0.007:
        return -0
    if r < 0.01:
        return 0
    return uniform(-10, 10)

