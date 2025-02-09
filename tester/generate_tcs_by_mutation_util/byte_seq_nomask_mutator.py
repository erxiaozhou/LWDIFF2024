import random


def mutate_without_mask(s):
    """Return s with a random mutation applied"""
    mutators = [
        _delete_random_character,
        _insert_random_character,
        _replace_random_character
    ]
    mutator = random.choice(mutators)
    s = bytearray(s)
    return mutator(s)


def _delete_random_character(s: bytearray):
    """Returns s with a random character deleted"""
    if len(s) == 0:
        return s
    pos = random.randint(0, len(s) - 1)
    s = _delete_op(pos, s)
    return s


def _delete_op(pos, s):
    s = s.copy()
    s.pop(pos)
    return s


def _insert_random_character(s):
    """Returns s with a random character inserted"""
    pos = random.randint(0, len(s))
    random_character = random.randint(0, 255)
    s = _insert_op(pos, random_character, s)
    return s


def _insert_op(pos, inserted_char, s):
    s = s.copy()
    s.insert(pos, inserted_char)
    return s


def _replace_random_character(s):
    if len(s) == 0:
        return s
    pos = random.randint(0, len(s) - 1)
    random_char = random.randint(0, 255)
    s = _replace_op(pos, random_char, s)
    return s


def _replace_op(pos, new_char, s):
    s = s.copy()
    s[pos] = new_char
    return s
