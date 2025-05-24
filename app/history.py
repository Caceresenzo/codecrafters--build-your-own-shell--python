previous_lines = []

def add_line(line):
    previous_lines.append(line)

def iterate():
    for index, line in enumerate(previous_lines):
        yield (index + 1, line)
