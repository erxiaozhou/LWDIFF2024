import leb128


id_name_dict = {
    0: 'custom',
    1: 'type',
    2: 'import',
    3: 'function',
    4: 'table',
    5: 'memory',
    6: 'global',
    7: 'export',
    8: 'start',
    9: 'element',
    10: 'code',
    11: 'data',
    12: 'data_count'
}

seq_encode_seq = [
    'custom',
    'type',
    'import',
    'function',
    'table',
    'memory',
    'global',
    'export',
    'start',
    'element',
    'data_count',
    'code',
    'data',
]

sec_name2_id = {v:k for k,v in id_name_dict.items()}

def prepare_template(template_path):
    with_table_template = {}
    f_temp_src = open(template_path, 'rb')
    # prepare pre
    f_temp_len = f_temp_src.seek(0, 2)
    f_temp_src.seek(0, 0)
    with_table_template['pre'] = f_temp_src.read(0x8)
    while f_temp_src.tell() < f_temp_len:
        cur_section_id_raw_content = f_temp_src.read(1).hex()
        cur_section_id = int(cur_section_id_raw_content, 16)
        cur_section_name = id_name_dict[cur_section_id]
        section_length = leb128.u.decode_reader(f_temp_src)[0]
        content = f_temp_src.read(section_length)
        with_table_template[cur_section_name] = content
    return with_table_template


def prepare_sec_name2all_ba(template_path):
    with_table_template = {}
    f_temp_src = open(template_path, 'rb')
    # prepare pre
    f_temp_len = f_temp_src.seek(0, 2)
    f_temp_src.seek(0, 0)
    with_table_template['pre'] = f_temp_src.read(0x8)
    while f_temp_src.tell() < f_temp_len:
        cur_section_id_raw_content = f_temp_src.read(1).hex()
        cur_section_id = int(cur_section_id_raw_content, 16)
        cur_section_name = id_name_dict[cur_section_id]
        section_length = leb128.u.decode_reader(f_temp_src)[0]
        content = f_temp_src.read(section_length)
        with_table_template[cur_section_name] = _add_necessary_ba(cur_section_name, section_length, content)
    return with_table_template

def _add_necessary_ba(section_name, section_length, raw_ba)->bytearray:
    len_ba = leb128.u.encode(section_length)
    id_part = leb128.u.encode(sec_name2_id[section_name])
    # return len_ba,id_part
    return id_part + len_ba + raw_ba
    
