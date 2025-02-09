from .get_reason_util import reason_base_dir2reason_summary_json
from file_util import check_dir
from extract_dump.dump_data_util import no_exec_state_attrs
from extract_dump.data_comparer import DiffStrategy


class reasonSummary:
    def __init__(self, reason_summary_base_dir, reason_base_dir, exec=True, must_gen=False):
        reason_summary_base_dir = check_dir(reason_summary_base_dir)
        full_reason_summary_path = reason_summary_base_dir / 'full_summary.json'
        only_exec_reason_summary_path = reason_summary_base_dir / 'only_exec_summary.json'
        stack_reason_summary_path = reason_summary_base_dir / 'stack_summary.json'
        if exec:
            if (not full_reason_summary_path.exists()) or must_gen:
                reason_base_dir2reason_summary_json(reason_base_dir, full_reason_summary_path, DiffStrategy.ALL)
            if (not stack_reason_summary_path.exists()) or must_gen:
                reason_base_dir2reason_summary_json(reason_base_dir, stack_reason_summary_path, diff_strategy=DiffStrategy.Variable)
            if (not only_exec_reason_summary_path.exists()) or must_gen:
                reason_base_dir2reason_summary_json(reason_base_dir, only_exec_reason_summary_path, diff_strategy=DiffStrategy.ExecStatus)
        self.full_smry_path = full_reason_summary_path
        self.only_exec_smry_path = only_exec_reason_summary_path
        self.stack_smry_path = stack_reason_summary_path
