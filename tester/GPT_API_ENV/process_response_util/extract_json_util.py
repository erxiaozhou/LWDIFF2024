# =============== extract content start ===============

def detect_line_idxs(lines:list[str], line_content:str):
    idxs = [idx for idx, line in enumerate(lines) if line_content == line]
    return idxs

def match_md_json_start_idxs(lines:list[str]):
    return detect_line_idxs(lines, '```json')


def match_md_json_end_idxs(lines:list[str]):
    return detect_line_idxs(lines, '```')


def track_lines_of_a_dict(lines:list[str]):
    stored_paragraphs:list[str] = []
    depth = 0
    stored_lines:list[str] = []
    for line in lines:
        if line.strip() == '{':
            depth += 1
            stored_lines.append(line)
            continue
        if depth > 0:
            stored_lines.append(line)
            depth_change_in_cur_line = line.count('{') - line.count('}')
            depth += depth_change_in_cur_line
            if depth == 0:
                stored_paragraphs.append('\n'.join(stored_lines))
                stored_lines = []
        elif depth < 0:
            raise Exception('The depth should >= 0, indicating a bug in parsing program')
    if depth > 0 or stored_lines:
        assert depth == 0
        assert stored_lines
        raise UnfinishedParsingException('The response is unfinished')
    # print('*****************************************************')
    # print(stored_paragraphs)
    # print('*****************************************************')
    return stored_paragraphs


class UnfinishedParsingException(Exception):
    pass
