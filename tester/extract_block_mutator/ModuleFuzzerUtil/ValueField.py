from typing import Any, Callable, List, Optional,  Union
from typing import Protocol
from random import choice, choices, randint, random
import inspect



class FieldFunc:
    def __init__(self, func: Callable):
        self.func = func
        self.signature = inspect.signature(func)

    def __call__(self, **kwds):
        try:
            # Bind the provided keyword arguments to the function's signature
            bound_arguments = self.signature.bind_partial(**kwds)
            # Call the function with the bound keyword arguments
            # print('See bound_arguments', bound_arguments, self.func)
            return self.func(*bound_arguments.args, **bound_arguments.kwargs)
        except TypeError as e:
            raise ValueError(f"Error binding arguments: {e}")




class ValueField:
    def random_valid_cvalue(self, *args, **kwds)->Any:
        raise NotImplementedError

def common_generate_one(x, *args, **kwds):
    if callable(x):
        # print('See x', x)
        # print('See kwds', kwds)
        
        return x(**kwds)
    elif isinstance(x, ValueField):
        return x.random_valid_cvalue(*args, **kwds)
    return x


class ComibedField(ValueField):
    def __init__(self, fields:List[ValueField], probs:List[float]):
        self.fields = fields
        self.probs = probs

    def random_valid_cvalue(self, *args, **kwds):
        rv = random()
        sum_ = 0
        for i, prob in enumerate(self.probs):
            sum_ += prob
            if rv < sum_:
                return self.fields[i].random_valid_cvalue(*args, **kwds)
        return self.fields[-1].random_valid_cvalue(*args, **kwds)


class discreteValueField(ValueField):
    def __init__(self, all_candis:List[Any], population:Optional[List[float]]=None):
        self.all_candis: List[Any] = all_candis
        self.population = population
        if population is None:
            self.population = [1/len(all_candis) for _ in range(len(all_candis))]

    def random_valid_cvalue(self, *args, **kwds):
        if kwds.get('required') is not None:
            return kwds['required']
        return choices(self.all_candis, self.population)[0]


class funcDeterminedRangeIntValueField(ValueField):
    def __init__(self, min_:Union[int, FieldFunc], max_:Union[int, FieldFunc], lopen:bool, uopen:bool):
        self.min_ = min_
        self.max_ = max_
        self.uopen = uopen
        self.lopen = lopen

    def random_valid_cvalue(self, *args, **kwds):
        lb = common_generate_one(self.min_, **kwds)
        if self.lopen:
            lb += 1
        ub = common_generate_one(self.max_, **kwds)
        if self.uopen:
            ub -= 1
        return randint(lb, ub)


class OneFuncValueField(ValueField):
    def __init__(self, func: FieldFunc):
        self.func = func

    def random_valid_cvalue(self, *args, **kwds):
        return self.func(**kwds)


class ListedField(OneFuncValueField):
    def __init__(self, sub_value_fileld:ValueField):
        elem_generate_func = sub_value_fileld.random_valid_cvalue

        def _generate_list(length:int, **kwds):
            return [elem_generate_func(**kwds) for _ in range(length)]

        super().__init__(FieldFunc(_generate_list))

class keyConditionField(OneFuncValueField):
    def __init__(self, fields_dict:dict[Any, Any]):
        self.fields_dict = fields_dict
        def _gen_func(key, **kwds):
            return common_generate_one(self.fields_dict[key], **kwds)
        super().__init__(FieldFunc(_gen_func))
            # return self.fields_dict[key].random_valid_cvalue(**kwds)
        # self.func = FieldFunc(gen_func)
        # self.func = gen_func
    # def random_valid_cvalue(self, *args, **kwds):
        
