from pathlib import Path

from tqdm import tqdm
from pymongo import MongoClient
from extract_dump.retrieve_coverage import collect_a_cov
from extract_dump.retrieve_coverage import oneExecCoverage, CoverageAll
from config import MONGO_HOST, MONGO_PORT
from file_util import check_dir, get_time_string, save_json
import sys


def run_a_dir(collection, item_name, base_dir,result_base_dir,  func_name='to_test', cov_summary=None):
    if cov_summary is None:
        cov_summary = CoverageAll()
    

    cov_data_dir = check_dir(check_dir(result_base_dir) / 'cov_data')

    print('SSSS base_dir', base_dir)
    paths = list(Path(base_dir).iterdir())
    paths = [p for p in paths if p.suffix == '.wasm']
    for p in tqdm(paths, total=len(paths)):

        if p.suffix != '.wasm':
            continue
        try:
            result = collect_a_cov(p)



            cov = result
            assert cov is not None
            cov_summary.update_coverage_info(cov)
        except TimeoutError:
            print('! time out error!')
            continue

    query = {
        'type': item_name,  # v19_tcs_30k_seed_base_cov
        'time': get_time_string(),
        'base_dir': str(base_dir),
        'cov_rate': cov_summary.cov_rate
    }
    collection.insert_one(query)

    print(cov_summary.cov_rate)
    return cov_summary
    
    

def run_cp910SE():
    db = MongoClient(MONGO_HOST, MONGO_PORT)['CP912BASELINE']
    collection = db['CP910SE']
    item_name = 'CP910SE_seed_base_cov'
    base_dir = '../../v19_tcs_from_cloud'
    result_base_dir = '/media/hdd8T1/baseline/CP910SE'
    cov_summary = CoverageAll()
    run_a_dir(collection, item_name, base_dir, result_base_dir, cov_summary=cov_summary)


def run_cp910():
    base_dirs = [
         '../../v19_tcs_from_cloud',
         '/media/hdd8T1/baseline/CP910/test_std_new_tcs'
    ]
    db = MongoClient(MONGO_HOST, MONGO_PORT)['CP912BASELINE']
    collection = db['CP910']
    result_base_dir = '/media/hdd8T1/baseline/CP910_clloect_cov'
    item_name = 'CP910_seed_base_cov'
    cov_summary = CoverageAll()
    for base_dir in base_dirs:
        cov_summary = run_a_dir(collection, item_name, base_dir, result_base_dir, cov_summary=cov_summary)
    
    print(cov_summary.cov_rate)


def run_cp910SE_24h(result_base_dir):
    result_base_dir = Path(result_base_dir)
    db = MongoClient(MONGO_HOST, MONGO_PORT)['CP912BASELINE_24H']
    collection = db['CP910SE']
    item_name = Path(result_base_dir).stem


    cov_summary = CoverageAll()
    run_a_dir(collection, item_name, result_base_dir/'test_std_new_tcs', result_base_dir, cov_summary=cov_summary)




if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'NO_MUTATION_CP910SE':
            run_cp910SE()
        elif sys.argv[1] == 'MUTATION_CP910':
            run_cp910()
    if len(sys.argv) == 3:
        if sys.argv[1] == '24h':
            run_cp910SE_24h(sys.argv[2])
