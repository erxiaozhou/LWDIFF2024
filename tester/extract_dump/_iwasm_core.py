from file_util import print_ba
from util import process_f32_64
from .process_dump_data_util import get_int
from .process_dump_data_util import get_f32
from .process_dump_data_util import get_f64
from .dumpDataBase import halfDumpData

class iwasmHalfDumpDataCore(halfDumpData):
    def _init_stack(self, stack_path):
        with open(stack_path, 'rb') as f:
            ba = f.read()
            # print_ba(ba)
        with open(stack_path, 'rb') as f:
            # print(self.name)
            self.stack_num = get_int(f.read(8))
            # print('stack_num', self.stack_num)
            for i in range(self.stack_num):
                ty = f.read(1)
                # print('cur ty', ty)
                processed_ba = None
                if ty == b'\x7F':
                    self.stack_types.append('i32')
                    cur_bytes = f.read(4)
                    self.stack_infered_vals.append(get_int(cur_bytes))
                elif ty == b'\x7E':
                    self.stack_types.append('i64')
                    cur_bytes = f.read(8)
                    self.stack_infered_vals.append(get_int(cur_bytes))
                elif ty == b'\x7D':
                    self.stack_types.append('f32')
                    cur_bytes = f.read(4)
                    self.stack_infered_vals.append(get_f32(cur_bytes))
                    processed_ba = process_f32_64(cur_bytes)
                elif ty == b'\x7C':
                    self.stack_types.append('f64')
                    cur_bytes = f.read(8)
                    self.stack_infered_vals.append(get_f64(cur_bytes))
                    processed_ba = process_f32_64(cur_bytes)
                elif ty == b'\x7B':
                    self.stack_types.append('v128')
                    cur_bytes = f.read(16)
                    self.stack_infered_vals.append([x for x in bytearray(cur_bytes)])
                elif ty == b'\x70':
                    cur_bytes = bytearray([])
                    f.read(4)
                    f.read(4)
                    self.stack_infered_vals.append([])

                    self.stack_types.append('funcref')

                    # cur_bytes = f.read(4)
                    # func_idx = get_int(cur_bytes)
                    # is_null_bytes = f.read(4)
                    # is_null = get_int(is_null_bytes)
                    # processed_ba = bytearray(cur_bytes) + bytearray(is_null_bytes)
                    # self.stack_infered_vals.append((func_idx, is_null))
                elif ty == b'\x6F':
                    cur_bytes = bytearray([])
                    f.read(4)
                    f.read(4)
                    self.stack_infered_vals.append([])

                    self.stack_types.append('externref')

                    # cur_bytes = f.read(4)
                    # content_as_int = get_int(cur_bytes)
                    # is_null_bytes = f.read(4)
                    # is_null = get_int(is_null_bytes)
                    # processed_ba = bytearray(cur_bytes) + bytearray(is_null_bytes)
                    # self.stack_infered_vals.append((content_as_int, is_null))
                else:
                    assert 0, print('ty is ', ty)
                self.stack_bytes.append(cur_bytes)
                if processed_ba is None:
                    processed_ba = bytearray(cur_bytes)
                self.stack_bytes_process_nan.append(processed_ba)
