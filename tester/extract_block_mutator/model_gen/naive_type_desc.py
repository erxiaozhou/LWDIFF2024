from GPT_API_ENV.ResponseChecker.each_def_checker import extract_terms_from_desc


class NaiveTypeDesc:
    def __init__(self, cur_def:list[dict], ref_dicts:dict[str, list[dict]]):
        self.cur_def = cur_def
        self.comp_names = [d['name'] for d in cur_def]

    def contains(self, comp_name:str):
        return comp_name in self.comp_names

    def get_comp_type_desc(self, comp_name:str):
        comp_type_desc_str = None
        for d in self.cur_def:
            if d['name'] == comp_name:
                comp_type_desc_str = d['type']
                break
        assert comp_type_desc_str is not None, f'comp_name: {comp_name}'
        # sub_type_names = extract_terms_from_desc(comp_type_desc_str)
        # if len(sub_type_names) == 0:
        #     return None

def _a_field_exist(cur_def:list[dict], ref_dicts:dict[str, list[dict]], query_name:str):
    if query_name in [d['name'] for d in cur_def]:
        return True
    if '.' not in query_name:
        return False
    comp_name, next_query_field = query_name.split('.', 1)
    if comp_name not in [d['name'] for d in cur_def]:
        return False
    comp_type_desc_str = None
    for d in cur_def:
        if d['name'] == comp_name:
            comp_type_desc_str = d['type']
            break
    assert comp_type_desc_str is not None, f'comp_name: {comp_name}'
    sub_type_names = extract_terms_from_desc(comp_type_desc_str)
    for sub_type_name in sub_type_names:
        # sub_type_def = 
        # assert 
        if sub_type_name in ref_dicts:
            if _a_field_exist(ref_dicts[sub_type_name], ref_dicts, next_query_field):
                return True
    return False
    