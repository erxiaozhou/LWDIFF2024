
from pathlib import Path
from file_util import print_ba

from util import process_f32_64
from .process_dump_data_util import get_int, get_u64
from .process_dump_data_util import get_f32
from .process_dump_data_util import get_f64
from .dumpDataBase import fullDumpResultData
from .dumpDataBase import halfDumpData


class wasmedgeHalfDumpData(halfDumpData):
    def _init_stack(self, stack_path):
        with open(stack_path, 'rb') as f:
            self.stack_num = get_int(f.read(8))
            for i in range(self.stack_num):
                ty = f.read(1)
                # print('-----------------------')
                # print_ba(ty)
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
                    self.stack_infered_vals.append([])
                    self.stack_types.append('funcref')
                elif ty == b'\x6F':
                    cur_bytes = bytearray([])
                    self.stack_infered_vals.append([])
                    self.stack_types.append('externref')
                else:
                    print('unexpected type in wasmedge',ty, str(ty), self.stack_num, len(ty))
                    self.stack_types.append('unknown')
                    cur_bytes = bytearray([])
                    self.stack_infered_vals.append([])
                self.stack_bytes.append(cur_bytes)
                if processed_ba is None:
                    processed_ba = bytearray(cur_bytes)
                self.stack_bytes_process_nan.append(processed_ba)


class wasmedgeFullDumpData(fullDumpResultData, wasmedgeHalfDumpData):
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
                    self.global_types.append('v128')
                    cur_bytes = f.read(16)
                    self.global_bytes.append(cur_bytes)
                    self.global_infered_vals.append([x for x in bytearray(cur_bytes)])
                if get_int(f.read(1)):
                    self.global_muts.append(True)
                else:
                    self.global_muts.append(False)
            self.table_num = get_int(f.read(4))
            if self.table_num > 0:
                self.default_table_len = get_int(f.read(4))
            else:
                self.default_table_len = 0
            self.mem_num = get_int(f.read(4))
            if self.mem_num > 0:
                self.default_mem_page_num = get_int(f.read(4))
                self.default_mem_length = get_u64(f.read(8))
                self.default_mem_data = f.read(self.default_mem_length)
