import random


def mutate_with_mask(s, masks):
    """Return s with a random mutation applied"""
    mutators = [
        _delete_random_character,
        _insert_random_character,
        _replace_random_character
    ]
    mutator = random.choice(mutators)
    return mutator(s, masks)


def _delete_random_character(s: bytearray, masks):
    """Returns s with a random character deleted"""
    if len(s) == 0:
        return s
    pos = _get_pos_outof_masks(s, masks)
    s = _delete_op(pos, s)
    return s


def _delete_op(pos, s):
    s = s.copy()
    s.pop(pos)
    return s


def _insert_random_character(s, masks):
    """Returns s with a random character inserted"""
    pos = _get_pos_outof_masks_insert(s, masks)
    random_character = random.randint(0, 255)
    s = _insert_op(pos, random_character, s)
    return s


def _insert_op(pos, inserted_char, s):
    s = s.copy()
    s.insert(pos, inserted_char)
    return s


def _replace_random_character(s, masks):
    if len(s) == 0:
        return s
    pos = _get_pos_outof_masks(s, masks)
    random_char = random.randint(0, 255)
    s = _replace_op(pos, random_char, s)
    return s


def _replace_op(pos, new_char, s):
    s = s.copy()
    s[pos] = new_char
    return s


def _get_pos_outof_masks(s, masks):
    s_length = len(s)
    while True:
        pos = random.randint(0, s_length - 1)
        if not _in_masks(pos, masks):
            break
    return pos


def _get_pos_outof_masks_insert(s, masks):
    s_length = len(s)
    ms2 = [[m[0] + 1, m[1]] for m in masks]
    while True:
        pos = random.randint(0, s_length)
        if not _in_masks(pos, ms2):
            break
    return pos


def _in_masks(pos, masks):
    is_in_mask = False
    for m in masks:
        if pos >= m[0] and pos < m[1]:
            is_in_mask = True
    return is_in_mask
