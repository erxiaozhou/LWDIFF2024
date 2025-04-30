from .LaneDesc import LaneDesc
from z3 import BitVecRef, Extract, fpBVToFP, Float32, Float64


def get_lane_symbol_smry(lane_desc:LaneDesc, simd_val):
    lane_idx = lane_desc.lane_idx
    lane_type_repr = lane_desc.lane_type_repr
    if lane_desc.is_int:
        return _get_lane_symbol_as_int(lane_idx, simd_val, int(lane_type_repr[1:]))
    elif lane_type_repr == 'f32':
        return _get_lane_symbol_as_f32(lane_idx, simd_val)
    elif lane_type_repr == 'f64':
        return _get_lane_symbol_as_f64(lane_idx, simd_val)
    else:
        raise NotImplementedError(f'Failed to get symbl val for {lane_type_repr}')

def _get_lane_symbol_as_int(lane_idx:int, simd_val:BitVecRef, bw:int):
    return Extract((lane_idx + 1) * bw - 1, lane_idx * bw, simd_val)

def _get_lane_symbol_as_f32(lane_idx:int, simd_val:BitVecRef):
    int_val = _get_lane_symbol_as_int(lane_idx=lane_idx, simd_val=simd_val, bw=32)
    return fpBVToFP(int_val, Float32())


def _get_lane_symbol_as_f64(lane_idx:int, simd_val:BitVecRef):
    int_val = _get_lane_symbol_as_int(lane_idx=lane_idx, simd_val=simd_val, bw=64)
    return fpBVToFP(int_val, Float64())


