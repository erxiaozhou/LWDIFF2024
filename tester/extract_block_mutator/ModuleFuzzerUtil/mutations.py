from .import_related import insert_import
from .DefMutation import Mutation

from .data_count_related import can_apply_insert_data_count, insert_data_count
from .custom_related import can_insrt_custom_section, insert_custom_section, custom_section_exist, delete_custom_section, rewrite_custom_section
from .data_memory_related import memory_exist, can_insert_memory, insert_memory, reset_random_memory
from .data_memory_related import can_insert_passive_data, insert_passive_data, can_insert_active_data, insert_active_data, delete_data, reset_random_data, can_reset_random_data, data_exist
from .global_related import insert_global, can_insert_global
from .table_and_elem_related import can_insert_table, insert_table, table_exist, delete_table, reset_random_table
from .table_and_elem_related import elem_seg_exist, reset_random_elem_sec, delete_elem_sec
from .table_and_elem_related import can_insert_passive_elem, insert_passive_elem, can_insert_active_elem, insert_active_elem, can_insert_declarative_elem, insert_declarative_elem
from .func_related import insert_type, insert_func, insert_local, extend_return_type, can_extend_return_type
from .start_related import can_insert_start, insert_start, can_replace_start, replace_start
from .export_related import insert_export, can_apply_rewrite_export_name, rewrite_export_name
from WasmInfoCfg import SectionType

def always_true(*args, **kwargs):
    return True

# data count
insert_data_count_mutation = Mutation('insert_data_count', SectionType.DataCount, can_apply_insert_data_count, insert_data_count)
# custom
insert_custom_section_mutaiton = Mutation('insert_custom_section', SectionType.Custom, can_insrt_custom_section, insert_custom_section)
rewrite_custom_section_mutation = Mutation('rewrite_custom_section', SectionType.Custom, custom_section_exist, rewrite_custom_section)
delete_custom_section_mutation = Mutation('delete_custom_section', SectionType.Custom, custom_section_exist, delete_custom_section)
# memory
insert_memory_mutation = Mutation('insert_memory', SectionType.Memory, can_insert_memory, insert_memory)
reset_random_memory_mutation = Mutation('reset_random_memory', SectionType.Memory, memory_exist, reset_random_memory)
# data
insert_passive_data_mutation = Mutation('insert_passive_data', SectionType.Data, can_insert_passive_data, insert_passive_data)
insert_active_data_mutation = Mutation('insert_active_data', SectionType.Data, can_insert_active_data, insert_active_data)
delete_data_mutation = Mutation('delete_data', SectionType.Data, data_exist, delete_data)
reset_random_data_mutation = Mutation('reset_random_data', SectionType.Data, can_reset_random_data, reset_random_data)
# global
insert_global_mutation = Mutation('insert_global', SectionType.Global, can_insert_global, insert_global)
# table
insert_table_mutation = Mutation('insert_table', SectionType.Table, can_insert_table, insert_table)
delete_table_mutation = Mutation('delete_table', SectionType.Table, table_exist, delete_table)
reset_table_mutation = Mutation('reset_table', SectionType.Table, table_exist, reset_random_table)
# elem
reset_elem_seg_mutation = Mutation('reset_elem_seg', SectionType.Element, elem_seg_exist, reset_random_elem_sec)
delete_elem_seg_mutation = Mutation('delete_elem_seg', SectionType.Element, elem_seg_exist, delete_elem_sec)
rename_export_mutation = Mutation('rename_export', SectionType.Export,can_apply_rewrite_export_name, rewrite_export_name)
insert_passive_elem_mutation = Mutation('insert_passive_elem', SectionType.Element, can_insert_passive_elem, insert_passive_elem)
insert_active_elem_mutation = Mutation('insert_active_elem', SectionType.Element, can_insert_active_elem, insert_active_elem)
insert_declarative_elem_mutation = Mutation('insert_declarative_elem', SectionType.Element, can_insert_declarative_elem, insert_declarative_elem)
# function & type
insert_type_mutation = Mutation('insert_type', SectionType.Code, always_true, insert_type)
insert_func_mutation = Mutation('insert_func', SectionType.Code, always_true, insert_func)
insert_local_mutation = Mutation('insert_local', SectionType.Code, always_true, insert_local)
extend_return_type_mutation = Mutation('extend_return_type', SectionType.Code, can_extend_return_type, extend_return_type)
# start
insert_start_mutation = Mutation('insert_start', SectionType.Start,can_insert_start, insert_start)
replace_start_mutation = Mutation('replace_start', SectionType.Start,can_replace_start, replace_start)
# export & import
insert_export_mutaiton = Mutation('insert_export', SectionType.Export,always_true, insert_export)
insert_import_mutation = Mutation('insert_import', SectionType.Import,always_true, insert_import)
