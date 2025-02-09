import re



# remove (;@0;)
p = re.compile(r'\(;\s*@(\d+)\s*;\)')
p = re.compile(r'\(;.*?;\)')


def process_comment(line):
    return p.sub('', line)
