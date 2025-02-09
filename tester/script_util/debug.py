from pathlib import Path
from typing import Union
from file_util import path_read

def get_around_lines(file_path:Union[str, Path], searched_texts:list[str], result_path:Union[str, Path], around_line_num=10):
    lines = path_read(file_path).split('\n')
    liine_idxs = [idx for idx, line in enumerate(lines) if _searched_texts_in_line(line, searched_texts)]
    final_paragraphgs = []
    for line_idx in liine_idxs:
        start, end = get_line_range(line_idx, around_line_num, len(lines))
        final_paragraphgs.append('\n'.join(lines[start:end]))
    # write to file
    with open(result_path, 'w') as f:
        f.write('\n-----\n'.join(final_paragraphgs))

def _searched_texts_in_line(line:str, searched_texts:list[str]):
    for text in searched_texts:
        if text in line:
            return True
    return False


def get_line_range(line_idx, around_line_num, total_line_num):
    start = max(0, line_idx - around_line_num)
    end = min(total_line_num, line_idx + around_line_num)
    return start, end
