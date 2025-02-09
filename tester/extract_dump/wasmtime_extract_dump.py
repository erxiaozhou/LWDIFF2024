
from pathlib import Path
from file_util import print_ba

from util import process_f32_64
from .process_dump_data_util import get_int, get_u64
from .process_dump_data_util import get_f32
from .process_dump_data_util import get_f64
from .dumpDataBase import fullDumpResultData
from .dumpDataBase import halfDumpData


class wasmtimeHalfDumpData(halfDumpData):
    def _init_stack(self, stack_path):
        with open(stack_path, 'rb') as f:
            self.stack_num = get_int(f.read(8))
            # print('#$@!$###--#', self.stack_num)
            for i in range(self.stack_num):
                ty = f.read(1)
                # print_ba(ty)
                # print('-----------------------')
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
                    
                    f.read(1)
                    self.stack_infered_vals.append([])
                    self.stack_types.append('funcref')
                elif ty == b'\x6F':
                    cur_bytes = bytearray([])

                    f.read(1)
                    self.stack_infered_vals.append([])
                    self.stack_types.append('externref')
                else:
                    assert 0
                self.stack_bytes.append(cur_bytes)
                if processed_ba is None:
                    processed_ba = bytearray(cur_bytes)
                self.stack_bytes_process_nan.append(processed_ba)

