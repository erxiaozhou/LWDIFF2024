from curses.ascii import isdigit
from pathlib import Path
import sys
import traceback
from tqdm import tqdm
from config import MONGO_HOST, MONGO_PORT
from extract_block_mutator.WasmParser import WasmParser
from smith_util.rewrite_case_generated_by_wasm_smith import rewrite_a_case, is_expected_case
from smith_util.rewrite_case_generated_by_wasm_smith import ByteSmithRewriter
from debug_util.debug_util import validate_wasm
from debug_util.debug_util import wasms_dir2wats
from file_util import check_dir, cp_file
from pymongo import MongoClient
from random import random



def get_latest_file_name(directory_path):
    directory = Path(directory_path)

    files = [file for file in directory.iterdir() if file.is_file()]

    latest_file = max(files, key=lambda x: x.stat().st_mtime, default=None)

    return latest_file.name if latest_file else None


def run_a_case_by_wat(p, outpur_dir, exception_dir, collection,can_invalid):
    new_path = outpur_dir / p.name
    try:
        parser = WasmParser.from_wasm_path(p)
        assert parser is not None
        if not is_expected_case(parser):
            query = {
                'type': 'not_expected_case',
                'case_name': p.name
            }
            collection.insert_one(query)
            return
        if new_path.exists():
            return
        assert parser is not None
        rewrite_a_case(parser, new_path)
        assert can_invalid or validate_wasm(new_path, print_detail_reason=True)
    except Exception as e:
        print(e, traceback.format_exc())
        cp_file(p, exception_dir)



def run_a_case_by_byte(p, outpur_dir, exception_dir, collection,can_invalid):
    new_path = Path(outpur_dir) / p.name
    if new_path.exists():
        return
    try:
        rewriter = ByteSmithRewriter(p)

        if not rewriter.is_expected_case():
            query = {
                'type': 'not_expected_case',
                'case_name': p.name
            }
            collection.insert_one(query)
            return


        rewriter.rewrite_main(new_path)

        assert not can_invalid
        if random() < 0.1:
            
            assert can_invalid or validate_wasm(new_path, print_detail_reason=True)
    except Exception as e:
        print(e, traceback.format_exc())
        cp_file(p, exception_dir)


def get_to_pass_names(collection, outpur_dir):
    to_pass_names = set()
    for item in collection.find():
        if item['type'] == 'not_expected_case':
            to_pass_names.add(item['case_name'])
    out_ps = list(outpur_dir.iterdir())
    out_names = set([p.name for p in out_ps])
    to_pass_names.update(out_names)
    return to_pass_names


def run_n(input_dir, outpur_dir, start_idx, process_num, can_invalid, by_wat):
    outpur_dir = check_dir(outpur_dir)
    collection = MongoClient(MONGO_HOST, MONGO_PORT)['PROCESS_SMITH'][outpur_dir.name]
    to_pass_names = get_to_pass_names(collection, outpur_dir)

    assert not can_invalid
    if by_wat:
        _func = run_a_case_by_wat
    else:
        _func = run_a_case_by_byte



    if process_num is None:

        for p in tqdm(input_dir.iterdir()):
            if p.name in to_pass_names:
                continue
            _func(p, outpur_dir, exception_dir, collection, can_invalid)
    else:
        ps = [p for p in input_dir.iterdir() if p.name not in to_pass_names]

        ps = ps[start_idx:]
        if process_num is None:
            process_num = len(ps)
        ps = ps[:process_num]

        for p in tqdm(ps):
            _func(p, outpur_dir, exception_dir, collection, can_invalid)


if __name__ == '__main__':
        
    input_dir = sys.argv[1]
    input_dir = Path(input_dir)
    outpur_dir = sys.argv[2]
    outpur_dir = Path(outpur_dir)
    exception_dir = sys.argv[3]
    exception_dir = check_dir(exception_dir)
    mode = sys.argv[4]
    assert mode in ['p', 'n']
    argv = sys.argv


        


    num_args = [int(x) for x in argv[5:] if x.isdigit()]
    not_num_args = [x for x in argv[5:] if not x.isdigit()]
    if len(num_args) == 0:
        start_idx = 0
        process_num = None
    if len(num_args) >= 1:
        start_idx = num_args[0]
        if len(num_args) >= 2:
            process_num = num_args[1]
    if not_num_args and not_num_args[0] == 'can_invalid':
        can_invalid = True
    else:
        can_invalid = False 
        
    by_wat = 'by_wat' in not_num_args
    if mode == 'p':
        assert 0

    else:
        run_n(input_dir, outpur_dir, start_idx, process_num, can_invalid, by_wat)
