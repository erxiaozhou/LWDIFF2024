import leb128


def read_next_leb_num(byte_seq, offset:int) -> tuple[int, int]:
    a = bytearray()
    while True:
        b = byte_seq[offset]
        offset += 1
        a.append(b)
        if (b & 0x80) == 0:
            break
    return leb128.u.decode(a), offset
def read_next_leb_int_num(byte_seq, offset:int) -> tuple[int, int]:
    a = bytearray()
    while True:
        b = byte_seq[offset]
        offset += 1
        a.append(b)
        if (b & 0x80) == 0:
            break
    return leb128.i.decode(a), offset


def read_s33(byte_seq, offset:int) -> tuple[int, int]:
    result = 0
    shift = 0
    # offset = 0
    for byte in byte_seq:
        offset += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if (byte & 0x80) == 0:
            break

    if shift < 33 and (result & (1 << (shift - 1))) != 0:
        result |= - (1 << shift)

    return result, offset