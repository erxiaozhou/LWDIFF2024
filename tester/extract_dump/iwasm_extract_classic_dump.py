from util import process_f32_64
from .process_dump_data_util import get_int, get_u64
from .process_dump_data_util import get_f32
from .process_dump_data_util import get_f64
from .dumpDataBase import fullDumpResultData
from ._iwasm_core import iwasmHalfDumpDataCore


class iwasmFullClassicInterpDumpData(fullDumpResultData, iwasmHalfDumpDataCore):
    def _init_store(self, store_path):
        with open(store_path, 'rb') as f:
            global_count_bytes = f.read(4)
            self.global_num = get_int(global_count_bytes)
            for i in range(self.global_num):
                ty = f.read(1)
                if ty == b'\x7F':
                    self.global_types.append('i32')
                    cur_bytes = f.read(4)
                    self.global_bytes.append(cur_bytes)
                    self.global_infered_vals.append(get_int(cur_bytes))
                elif ty == b'\x7E':
                    self.global_types.append('i64')
                    cur_bytes = f.read(8)
                    self.global_bytes.append(cur_bytes)
                    self.global_infered_vals.append(get_int(cur_bytes))
                elif ty == b'\x7D':
                    self.global_types.append('f32')
                    cur_bytes = f.read(4)
                    self.global_bytes.append(cur_bytes)
                    self.global_infered_vals.append(get_f32(cur_bytes))
                elif ty == b'\x7C':
                    self.global_types.append('f64')
                    cur_bytes = f.read(8)
                    self.global_bytes.append(cur_bytes)
                    self.global_infered_vals.append(get_f64(cur_bytes))
                elif ty == b'\x7B':
                    assert 0
                    self.global_types.append('v128')
                    cur_bytes = f.read(16)
                    self.global_bytes.append(cur_bytes)
                    self.global_infered_vals.append([x for x in bytearray(cur_bytes)])
            self.table_num = get_int(f.read(4))
            if self.table_num > 0:
                self.default_table_len = get_int(f.read(4))
                self.default_table_func_idxs = []
                for i in range(self.default_table_len):
                    self.default_table_func_idxs.append(get_int(f.read(4)))
            else:
                self.default_table_len = 0
            local_num = get_int(f.read(4))
            for i in range(local_num):
                ty = f.read(1)
                if ty == b'\x7F':
                    cur_bytes = f.read(4)
                elif ty == b'\x7E':
                    cur_bytes = f.read(8)
                elif ty == b'\x7D':
                    cur_bytes = f.read(4)
                elif ty == b'\x7C':
                    cur_bytes = f.read(8)
                elif ty == b'\x7B':
                    assert 0
                elif ty in [b'\x6F', b'\x70']:
                    cur_bytes = f.read(4)
                else:
                    assert 0, print(ty)
            stack_len = get_int(f.read(4))
            for i in range(stack_len):
                f.read(4)

            self.mem_num = get_int(f.read(4))
            if self.mem_num > 0:
                self.default_mem_length = get_u64(f.read(8))
                self.default_mem_page_num = get_int(f.read(4))
                self.default_mem_data = f.read(self.default_mem_length)
