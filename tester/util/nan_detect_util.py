from file_util import bytes2uint


def is_nan(bs):
    length = len(bs)
    assert length in [4, 8], print(length)
    if length == 4:
        N = 23
        epart_mask = 0b011111111 << N
    else:
        N = 52
        epart_mask = 0b011111111111 << N
    int_val = bytes2uint(bs)
    m_part = 2 ** N - 1
    eparts_val = int_val & epart_mask
    if not epart_mask == eparts_val:
        return False
    else:
        if (m_part & int_val) == 0:
            return False
    return True

def is_anan(bs):
    if not is_nan(bs):
        return False
    length = len(bs)
    assert length in [4, 8], print(length)
    int_val = bytes2uint(bs)
    if length == 4:
        N = 22
    else:
        N = 51
    mask = 2 ** (N + 1) - 1
    if (int_val & mask) > 2 ** N:
        return True
    else:
        return False


def is_cnan(bs):
    if not is_nan(bs):
        return False
    length = len(bs)
    assert length in [4, 8], print(length)
    int_val = bytes2uint(bs)
    if length == 4:
        N = 22
    else:
        N = 51
    mask = 2 ** (N + 1) - 1
    if (int_val & mask) == 2 ** N:
        return True
    else:
        return False


def is_illegal_anan(bs):
    if not is_nan(bs):
        return False
    if is_anan(bs):
        return False
    if is_cnan(bs):
        return False
    return True


def process_f32_64(bs):
    if is_anan(bs):
        val = _process_anan(bs)
    else:
        val = bs
    return val


def _process_anan(bs):
    assert is_anan(bs)
    if len(bs) == 4:
        val = _process_32anan(bs)
    else:
        assert len(bs) == 8
        val = _process_64anan(bs)
    return val


def _process_32anan(bs):
    assert is_anan(bs)
    int_val = bytes2uint(bs)
    highest_32_10 = 0b0111111111 << 22
    int_val = int_val & highest_32_10
    val = bytearray(int.to_bytes(int_val, 4, byteorder='little', signed=False))
    return val


def _process_64anan(bs):
    assert is_anan(bs)
    int_val = bytes2uint(bs)
    highest_64_13 = 0b0111111111111 << 51
    int_val = int_val & highest_64_13
    val = bytearray(int.to_bytes(int_val, 8, byteorder='little', signed=False))
    return val
