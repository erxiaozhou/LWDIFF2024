from .seed_select_info_util import Path2SeedSelectInfoClass
from .V1SeedSchedulerBase import V1SeedSchedulerBase
from .V1SeedSchedulerBase import _get_all_can_success_seeds
import random
from extract_dump.retrieve_coverage import CoverageAll
from .util import select_a_seed_randomly
from typing import Optional

class V3SeedScheduler(V1SeedSchedulerBase):
    def __init__(self, seed_pool, seedPath2SeedSelectInfo: Path2SeedSelectInfoClass, seed_updater_json:Optional[str], logger=None):
        super().__init__(seed_pool, seedPath2SeedSelectInfo, seed_updater_json, logger)

    def _get_energy(self, seed_path, coverage_summary: CoverageAll):
        return 20

    def _select_a_seed(self, coverage_summary: CoverageAll):
        random_num = random.random()
        
        # while self.init_seeds:
        #     seed_path = self.init_seeds.pop(0)
        #     if seed_path not in self.seedPath2SeedSelectInfo:
        #         return self.seed_pool.index(seed_path), seed_path
        # un-exec seeds
        unexec_seeds = []
        for _seed in self.seed_pool:
            if _seed not in self.seedPath2SeedSelectInfo:
                unexec_seeds.append(_seed)
        if unexec_seeds:
            # return 
            seed = random.choice(unexec_seeds)
            seed_idx = self.seed_pool.index(seed)
            return seed_idx, seed
        if random_num < 0.5:
            return select_a_seed_randomly(self.seed_pool)
        else:
            considered_seeds = _get_all_can_success_seeds(self.seedPath2SeedSelectInfo, self.seed_pool)
            assert considered_seeds
            seed = random.choice(considered_seeds)
            seed_idx = self.seed_pool.index(seed)
            return seed_idx, seed
