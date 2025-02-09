from pathlib import Path
from GPT_API_ENV.ResponseChecker.each_def_checker import extract_terms_from_desc
from WasmInfoCfg import naive_module_component_types
from file_util import read_json
from GPT_API_ENV.check_module_def_response_struc import content_as_final_kv
from file_util import cp_file, save_json
from file_util import check_dir


def detect_last_responses(src_dir, target_dir):
    target_dir = check_dir(target_dir)
    response_base_name2maxidx = {}
    for p in Path(src_dir).iterdir():
        if p.is_dir():
            continue
        fname = p.name
        if not fname.endswith('_response.txt'):
            continue
        fname = fname[:-len('_response.txt')]
        idx_part = fname.split('_')[-1]
        idx = int(idx_part)
        base_name = '_'.join(fname.split('_')[:-1])
        exist_idx = response_base_name2maxidx.get(base_name, -1)
        if idx > exist_idx:
            response_base_name2maxidx[base_name] = idx
        # print(response_base_name2maxidx)
    for base_name, max_idx in response_base_name2maxidx.items():
        src_path = Path(src_dir) / f'{base_name}_{max_idx}_response.txt'
        # print('src_path:', src_path)
        target_path = Path(target_dir) / f'{base_name}_response.txt'
        cp_file(src_path, target_path)
    print('In total, ', len(response_base_name2maxidx), ' responses are detected.')


def structure_module_def_response(src_dir, target_dir):
    target_dir = check_dir(target_dir)
    for p in Path(src_dir).iterdir():
        if p.is_dir():
            continue
        fname = p.name
        assert fname.endswith('_response.txt')
        base_name = fname[:-len('_response.txt')]
        if base_name.endswith('_binary'):
            base_name = base_name[:-7]
        if base_name in naive_module_component_types:
            continue
        data = content_as_final_kv(p)
        assert isinstance(data, list)
        target_path = Path(target_dir) / f'{base_name}.json'
        save_json(target_path, data)

# content_as_final_kv

def list_all_module_defs(structured_def_dir, raw_list_path, trimmed_list_path):
    raw_defs = []
    for p in Path(structured_def_dir).iterdir():
        assert p.is_file()
        assert p.suffix == '.json'
        data = read_json(p)
        raw_defs.extend(data)
    print('In total, ', len(raw_defs), ' module definitions are detected.')
    save_json(raw_list_path, raw_defs)
    print('The raw list is saved at ', raw_list_path)
    # 
    defname2defs = {}
    for d in raw_defs:
        # define_name = list(d.keys())[0]
        # def2def_num[define_name] = def2def_num.get(define_name, 0) + 1
        defname2defs.setdefault(list(d.keys())[0], []).append(d)
    # 
    final_defs = {}
    for def_name in defname2defs.keys():
        defs = defname2defs[def_name]
        count = len(defs)
        if count > 1:
            # print(f'{def_name} has {count} definitions.')
            not_meaningless_idxs = [i for i, d in enumerate(defs) if not _meanlingless_def(d)]
            defname2defs[def_name] = [defs[i] for i in not_meaningless_idxs]
        if def_name in naive_module_component_types:
            continue
        if len(defname2defs[def_name]) > 1:
            print(f'Warning: {def_name} has {len(defname2defs[def_name])} definitions after removing meaningless definitions.')
            final_defs[def_name] = _identify_longest_def(defname2defs[def_name])
        else:
            final_defs.update(defname2defs[def_name][0])
    print('In total, ', len(final_defs), ' module definitions are detected after removing meaningless definitions.')
    save_json(trimmed_list_path, final_defs)
    print('The trimmed list is saved at ', trimmed_list_path)


def get_sub_def_names_of_defs(def_data_json_path, all_sub_type_json_path):
    defs = read_json(def_data_json_path)
    def_name2direct_sub_types = {}
    for def_name in defs.keys():
        def_name2direct_sub_types[def_name] = get_sub_def_names_of_a_def(defs, def_name)
    def_name2all_sub_types = {}
    # init def_name2all_sub_types
    for def_name, sub_types in def_name2direct_sub_types.items():
        def_name2all_sub_types[def_name] = set(sub_types)
    
    has_update = True
    while has_update:
        has_update = False
        for def_name in def_name2direct_sub_types.keys():
            sub_types = set(def_name2all_sub_types[def_name])
        # for def_name, sub_types in def_name2direct_sub_types.items():
            cur_def_mentioned_types = def_name2all_sub_types.get(def_name, set())
            for sub_type in sub_types:
                if sub_type in def_name2direct_sub_types:
                    cur_def_mentioned_types.update(def_name2all_sub_types[sub_type])
            
            if cur_def_mentioned_types != sub_types:
                has_update = True
                def_name2all_sub_types[def_name] = cur_def_mentioned_types
    # print 
    for def_name in def_name2all_sub_types.keys():
        sub_types = def_name2all_sub_types[def_name]
        print(f'{def_name}: {sub_types}')
        def_name2all_sub_types[def_name] = list(sub_types)
    save_json(all_sub_type_json_path, def_name2all_sub_types)
    # for def_name, sub_types in def_name2direct_sub_types.items():
        # cur_def_mentioned_types = set()
        # 

def get_sub_def_names_of_a_def(defs:dict[str, list], def_name:str):
    cur_def_mentioned_types = set()
    components = defs[def_name]
    print(f'{def_name}: {components}')
    for c in components:
        type_desc = c['type']
        # print('||| type_desc:', type_desc)
        cur_def_mentioned_types.update(extract_terms_from_desc(type_desc))
    return cur_def_mentioned_types


def get_dependency_seq(defname2all_sub_type_path, depandency_json_path):
    defname2all_sub_types = read_json(defname2all_sub_type_path)
    sequence = []
    determined_names = set(naive_module_component_types)
    undetermined_names = set(defname2all_sub_types.keys())
    while undetermined_names:
        for cur_name in undetermined_names:
            depended_types = defname2all_sub_types[cur_name]
            print(f'{cur_name}: {depended_types}')
            depended_types = set(depended_types)
            # determined_names = set(sequence)
            if depended_types.issubset(determined_names):
                sequence.append(cur_name)
                undetermined_names.remove(cur_name)
                determined_names.add(cur_name)
                # determined_names.update(depended_types)
                break
        print('len(undetermined_names):', len(undetermined_names), undetermined_names)
    save_json(depandency_json_path, sequence)


# def _identify_need_validation_defs(
#     defname2all_sub_type_path
# ):
#     data = read_json(defname2all_sub_type_path)
#     need_validation_defs = []
#     donot_need_validation_defs = []
#     undetermined_names = set(data.keys())
#     need_infer_compnents = set(naive_module_component_types)
#     while undetermined_names:
        


# =========================================

def _identify_longest_def(def_dicts):
    max_def = None
    max_def_length = 0
    for d in def_dicts:
        def_length = _detect_a_def_component_num(d)
        if def_length > max_def_length:
            max_def_length = def_length
            max_def = d
    return max_def
    


def _detect_a_def_component_num(def_dict):
    return len(list(def_dict.values())[0])

def _meanlingless_def(val_dict):
    val_part = list(val_dict.values())[0]
    if len(val_part) == 1:
        val_part = val_part[0]
        assert isinstance(val_part, dict)
        name_ = val_part.get('name', None)
        type_ = val_part.get('type', None)
        assert name_ is not None
        assert type_ is not None
        # print(val_part)
        # assert 'name' in val_dict
        # assert 'type' in val_dict
        if name_ == type_:
            return True
    return False


