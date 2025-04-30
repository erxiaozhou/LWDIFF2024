from file_util import remove_file_without_exception
from pathlib import Path
import shutil
from util import CLIResult, exec_impl_and_collect_CLI_result
from util import cmnImplResultPathGroup
from .util import combine_path



class dumpOriPathGroup(cmnImplResultPathGroup):
    def __init__(self, ori_store_path, ori_vstack_path, ori_inst_path):
        super().__init__(tgt_vstack_path=ori_vstack_path, tgt_store_path=ori_store_path, tgt_inst_path=ori_inst_path)
        
    @classmethod
    def _from_new_dict(cls, dict_):
        name_in_para_dict2para_name = {
            'dump_store_rpath': 'ori_store_path',
            'dump_vstack_rpath': 'ori_vstack_path',
            'dump_instante_rpath': 'ori_inst_path'
        }
        paras = {}
        for name_in_para_dict, para_name in name_in_para_dict2para_name.items():
            paras[para_name] = dict_.get(name_in_para_dict, None)
        return cls(**paras)

    @classmethod
    def _from_old_dict(cls, dict_):
        dump_dir = dict_['dump_dir']
        name_in_para_dict2para_name = {
            'dump_store_rpath': 'ori_store_path',
            'dump_vstack_rpath': 'ori_vstack_path',
            'dump_instante_rpath': 'ori_inst_path'
        }
        paras = {}
        for name_in_para_dict, para_name in name_in_para_dict2para_name.items():
            if name_in_para_dict in dict_:
                paras[para_name] = combine_path(dump_dir, dict_[name_in_para_dict])
            else:
                paras[para_name] = None
        return cls(**paras)


class NomoveBasedExecutor:
    def __init__(self, 
                 ori_paths:cmnImplResultPathGroup,
                timeout_th,
                dump_cmd_fmt, err_channel, pre_cmd=None, post_cmd=None):
        self.ori_paths = ori_paths
        self.timeout = timeout_th
        self.dump_cmd_fmt = dump_cmd_fmt
        self._result_paths = None
        self.err_channel = err_channel
        self.pre_cmd = pre_cmd
        self.post_cmd = post_cmd

    @classmethod
    def from_new_dict(cls, dict_, timeout_th):
        ori_paths = dumpOriPathGroup._from_new_dict(dict_)
        dump_cmd_fmt =dict_['dump_cmd']
        err_channel = dict_['err_channel']
        pre_cmd = dict_.get('pre_cmd', None)
        post_cmd = dict_.get('post_cmd', None)
        return cls(ori_paths, timeout_th, dump_cmd_fmt, err_channel, pre_cmd=pre_cmd, post_cmd=post_cmd)

    def execute(self, tc_path, func_name='to_test'):
        self._clean_previous_dumped_data()
        cli_result = exec_impl_and_collect_CLI_result(self.dump_cmd_fmt, self.timeout,tc_path, self.err_channel, pre_cmd=self.pre_cmd, post_cmd=self.post_cmd, func_name=func_name)
        return cli_result
    
    def _clean_previous_dumped_data(self):
        for p in self.ori_paths.paths:
            remove_file_without_exception(p)
    
    def set_result_paths(self, result_paths):
        assert isinstance(result_paths, cmnImplResultPathGroup)
        self._result_paths = result_paths


class dumpedResultGenerator:
    def __init__(self, dump_extractor_class, name=None):
        self.dump_extractor_class = dump_extractor_class
        self.name = name
        self._result_paths = None
        self.cli_result = None

    def set_result_paths(self, result_paths):
        assert isinstance(result_paths, cmnImplResultPathGroup)
        self._result_paths = result_paths

    def update_cli_result(self, cli_result:CLIResult):
        self.cli_result = cli_result

    def _result_obj_paras(self):
        data = {}
        data['paths'] = self._result_paths
        data['cli_result'] = self.cli_result
        data['name'] = self.name
        return data

    def get_result_obj(self):
        paras = self._result_obj_paras()
        assert all(v is not None for v in paras.values())
        result = self.dump_extractor_class(**paras)
        return result
