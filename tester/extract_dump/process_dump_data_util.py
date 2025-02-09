import numpy as np


def get_int(bytes_):
    return int.from_bytes(bytes_, 'little')


def get_f32(bytes_):
    return np.frombuffer(bytes_, np.float32)[0]


def get_f64(bytes_):
    return np.frombuffer(bytes_, np.float64)[0]


def get_u64(bytes_):
    return np.frombuffer(bytes_, np.uint64)[0]


def get_u32(bytes_):
    return np.frombuffer(bytes_, np.uint32)[0]


def get_u16(bytes_):
    return np.frombuffer(bytes_, np.uint16)[0]
