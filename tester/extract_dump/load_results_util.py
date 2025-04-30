from .dump_data_util import dumpData, get_extractor_from_pkl
from pathlib import Path


def load_results_from_one_dumped_data_dir(one_tc_result_dir):
    results = []
    for p in Path(one_tc_result_dir).iterdir():
        if p.suffix == '.pkl':
            dumped_path = str(p)
            result: dumpData = get_extractor_from_pkl(dumped_path)
            results.append(result)
    return results
