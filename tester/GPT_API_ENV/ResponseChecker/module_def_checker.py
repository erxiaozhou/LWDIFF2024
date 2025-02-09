from util.util import FailedParsingException
from typing import Union

def check_wat_format(content:dict):
    if 'summary' not in content:
        raise FailedParsingException('The format of the definition should be described in the `summary` field')
    tokens = split_summary(content['summary'])
    all_sub_keys = set(content.keys()) - {'summary'}
    all_p_tokens = [_process_a_token(token) for token in tokens]
    all_p_sub_keys = [_process_a_token(sub_key) for sub_key in all_sub_keys]
    for token in all_p_tokens:
        # ori token
        if token not in all_p_sub_keys:
            raise FailedParsingException(f'The token `{token}` should be described')
        

def _process_a_token(token:str):
    return token.strip(' *?')

def split_summary(smy_desc:Union[str, list]):
    if isinstance(smy_desc, str):
        spliters = ['|', ' ', '"', '(', ')', ',']
        for spliter in spliters:
            if spliter != ' ': # ignore space
                smy_desc = smy_desc.replace(spliter, ' ')
        # smy_desc = smy_desc.replace('  ', ' ')
        tokens = smy_desc.split(' ')
        tokens = [t for t in tokens if t]
        # * remove the parts after ':'
        for idx, token in enumerate(tokens):
            if ':' in token:
                new_token = token.split(':')[0]
                tokens[idx] = new_token
    else:
        tokens = smy_desc
    return tokens
    # 


def new_check_wat_format(data:dict):
    raise NotImplementedError('Not implemented yet')
