from functools import lru_cache
from typing import List
from .funcType import funcType, FuncTypeCatException, match_func_type
from .funcTypeFactory import funcTypeFactory
from enum import Enum


class REQRESULT(Enum):
    UNMATCH = 1
    MATCH = 2
    UNKNOWN = 3

    def matched(self):
        return self == REQRESULT.MATCH


class typeReq:
    def __init__(self, tys: List[funcType], req_type='eq'):
        # self.tys = [ty.copy() for ty in tys]
        self._tys = tys

        assert req_type in ['eq',
                            'eg_param_f', 'eg_param_and_result']
        self.req_type = req_type

    @property
    def tys(self):
        return self._tys

    @tys.setter
    def tys(self, value):
        raise Exception('tys setter is not allowed')
    

    def impossible(self):
        return len(self.tys) == 0

    @property
    def ty0(self):
        return self.tys[0]

    @classmethod
    def from_one_ty(cls, ty: funcType, req_type='eq'):
        return cls([ty], req_type)

    def __eq__(self, __value: object) -> bool:
        return set(self.tys) == set(__value.tys) and self.req_type == __value.req_type

    def __repr__(self) -> str:
        return f'typeReq(tys={self.tys}, req_type={self.req_type})'


def merge_req(req1, req2):
    assert req1 is not None and req2 is not None, print(req1, req2)
    assert isinstance(req1, typeReq)
    assert isinstance(req2, typeReq)

    if req1.req_type == 'eg_param_and_result' :
    # else:
        # req1.req_type == 'eq' and req2.req_type == 'eg_param_f':
        possible_cats = []
        for self_ty in req1.tys:
            for value_ty in req2.tys:
                try:
                    possible_cat = self_ty + value_ty
                    possible_cat =funcTypeFactory.generate_one_func_type_default(param_type=self_ty.param_types, result_type=possible_cat.result_types)
                    possible_cats.append(possible_cat)
                except FuncTypeCatException as e:
                    pass

        # determine req_ty
        # possible_cats = []
        self_req_type = req1.req_type
        value_req_type = req2.req_type
        req_ty = _determine_req_ty(self_req_type, value_req_type)
        return typeReq(possible_cats, req_ty)
        
    else:
        # first, we determine the possible function type candidates
        # second, we determine the req_type
        possible_cats = []
        for self_ty in req1.tys:
            for value_ty in req2.tys:
                try:
                    possible_cat = self_ty + value_ty
                    possible_cats.append(possible_cat)
                except FuncTypeCatException as e:
                    pass


        # determine req_ty
        self_req_type = req1.req_type
        value_req_type = req2.req_type
        req_ty = _determine_req_ty(self_req_type, value_req_type)
        return typeReq(possible_cats, req_ty)
    req_ty = _determine_req_ty(self_req_type, value_req_type)
    return typeReq(possible_cats, req_ty)

@lru_cache(maxsize=1024)
def _determine_req_ty(self_req_type, value_req_type):
    if 'eg_param_and_result' in [self_req_type, value_req_type]:
        req_ty = 'eg_param_and_result'
    elif 'eg_param_f' in [self_req_type, value_req_type]:
        req_ty = 'eg_param_f'
    else:
        req_ty = 'eq'
    return req_ty


def check_ftype_match_req(fty, req):
    if req is None:
        return REQRESULT.UNKNOWN
    if len(req.tys) > 1:
        for ty in req.tys:
            new_req = typeReq.from_one_ty(ty, req.req_type)
            # print('new_req', new_req)
            if check_ftype_match_req(fty, new_req) == REQRESULT.MATCH:
                return REQRESULT.MATCH
        return REQRESULT.UNMATCH
    req_ty = req.ty0
    if req.req_type == 'eq':
        if fty == req_ty:
            return REQRESULT.MATCH
        else:
            return REQRESULT.UNMATCH
    if req.req_type in ['eg_param_f', 'eg_param_and_result']:
        if len(req_ty.param_types) > len(fty.param_types):
            return REQRESULT.UNMATCH
        new_fty_param = fty.param_types[len(fty.param_types)-len(
            req_ty.param_types):len(fty.param_types)]
    else:
        new_fty_param = fty.param_types
    if req.req_type == 'eg_param_and_result':
        if len(req_ty.result_types) > len(fty.result_types):
            return REQRESULT.UNMATCH
        new_fty_result = fty.result_types[len(fty.result_types)-len(
            req_ty.result_types):len(fty.result_types)]
    else:
        new_fty_result = fty.result_types
    new_fty = funcTypeFactory.generate_one_func_type_default(param_type=new_fty_param,
                       result_type=new_fty_result)
    # print('new_req_type', new_fty)
    if match_func_type(new_fty, req_ty):
        return REQRESULT.MATCH
    else:
        return REQRESULT.UNMATCH
