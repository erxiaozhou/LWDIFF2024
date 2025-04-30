from pathlib import Path


class cmnImplResultPathGroup:
    def __init__(self, tgt_vstack_path, tgt_store_path, tgt_inst_path):
        self.vstack_path = tgt_vstack_path
        self.store_path = tgt_store_path
        self.inst_path = tgt_inst_path
    
    @property
    def paths(self):
        return [
            self.store_path,
            self.inst_path,
            self.vstack_path
        ]
    
    @classmethod
    def from_impl_name_and_tc_result_dir(cls, impl_name, tc_result_dir):
        base_dir = Path(tc_result_dir)
        return cls(
            tgt_vstack_path = base_dir / f'{impl_name}=vstack-part',
            tgt_store_path = base_dir / f'{impl_name}=store-part',
            tgt_inst_path = base_dir / f'{impl_name}=has_instance'
        )


class analyzeResultDirs:
    def __init__(self, result_base_dir) -> None:
        self.result_base_dir = Path(result_base_dir)
    
    @property
    def log_category_base_dir(self):
        return self.result_base_dir / 'log_category_base'

    @property
    def reason_summary_base_dir(self):
        return self.result_base_dir / 'reason_summarys'
    
    @property
    def stack_category_base_dir(self):
        return self.result_base_dir / 'stack_category_base'
