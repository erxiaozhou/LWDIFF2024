from pathlib import Path
import sys 
from typing import Optional
from pymongo.collection import Collection
from config import MONGO_HOST, MONGO_PORT
from pymongo import MongoClient
import numpy as np

from file_util import path_read


def get_time_and_cov_rate(collection:Collection):
    each_epoch_status_data = collection.find({'type': 'each_epoch_status'},{'_id': 0, 'type': 0})
    data = list(each_epoch_status_data)
    times = [d['time'] for d in data]
    cov_rate = [d['cov_rate'] for d in data]
    return times, cov_rate


def get_finished_full_cov(collection:Collection, check_time=86400):
    for t, cov in zip(*get_time_and_cov_rate(collection)):
        if t >= check_time:
            return cov
    return None

def get_max_cov(collection:Collection):
    covs = get_time_and_cov_rate(collection)[1]
    return np.max(covs)


def get_cp910_collection_name(collection_name:str, check_time):
    db = MongoClient(MONGO_HOST, MONGO_PORT)['Qlearning']
    # actual_name = f'CP910_{collection_name}'
    collection = db[collection_name]
    result = get_finished_full_cov(collection, check_time)
    return result

def see_multi_times(collection_name:str, check_times:list[int]):
    for check_time in check_times:
        print(f'{check_time}: {get_cp910_collection_name(collection_name, check_time)}')
    print(f'Max cov: {get_max_cov(MongoClient(MONGO_HOST, MONGO_PORT)["Qlearning"][collection_name])}')

if __name__ == '__main__':
    collection_name = sys.argv[1]
    # 
    if Path(collection_name).exists():
        if Path(collection_name).is_dir():
            conllection_name_path = Path(collection_name) / 'tester_paras/start_time.txt'
            collection_name = path_read(conllection_name_path).strip(' \n')
        else:
            collection_name = path_read(collection_name).strip(' \n')
    else:
        pass
    # 
    check_times = [int(t) for t in sys.argv[2:]]
    see_multi_times(collection_name, check_times)
